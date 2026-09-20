"""Collision primitives: AABB tests, tile queries and axis resolution.

Coordinates are *world* pixels with **y growing downwards** (screen style), so
"falling" means ``vy > 0``.  The renderer flips the axis when it draws.
Nothing here imports Kivy: the whole system is simulation-testable.
"""
from __future__ import annotations

from config import ONEWAY_TILES, TILE

EPS = 0.001


def aabb(ax, ay, aw, ah, bx, by, bw, bh) -> bool:
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def rect_of(body):
    return (body.x, body.y, body.w, body.h)


def tile_range(x, y, w, h):
    """Inclusive tile index range covering the rectangle."""
    return (int(x // TILE), int(y // TILE), int((x + w - EPS) // TILE), int((y + h - EPS) // TILE))


def solid_at(level, tx, ty) -> bool:
    return level.solid_at(tx, ty)


def oneway_at(level, tx, ty) -> bool:
    return level.tile(tx, ty) in ONEWAY_TILES


def _solid_columns(level, tx0, tx1, ty):
    for tx in range(tx0, tx1 + 1):
        if level.solid_at(tx, ty):
            return tx
    return None


def resolve_x(body, level) -> int:
    """Snap the body out of solid tiles horizontally. Returns wall hit (-1/0/1)."""
    tx0, ty0, tx1, ty1 = tile_range(body.x, body.y + 1.0, body.w, body.h - 2.0)
    if body.vx > 0:
        for ty in range(ty0, ty1 + 1):
            for tx in range(tx1, tx0 - 1, -1):
                if level.solid_at(tx, ty):
                    body.x = tx * TILE - body.w
                    body.vx = 0.0
                    body.wall_hit = 1
                    return 1
    elif body.vx < 0:
        for ty in range(ty0, ty1 + 1):
            for tx in range(tx0, tx1 + 1):
                if level.solid_at(tx, ty):
                    body.x = (tx + 1) * TILE
                    body.vx = 0.0
                    body.wall_hit = -1
                    return -1
    return 0


def resolve_y(body, level, prev_bottom: float):
    """Snap out of tiles vertically.

    Returns ``(landed, ceiling_hits)`` where ``ceiling_hits`` is a sorted list of
    ``(tx, ty)`` tiles bumped with the head (bonus/breakable blocks).
    """
    tx0, ty0, tx1, ty1 = tile_range(body.x + 1.0, body.y, body.w - 2.0, body.h)
    landed = False
    ceiling_hits = []

    if body.vy > 0:                      # falling: look for the first floor
        for ty in range(ty0, ty1 + 1):
            for tx in range(tx0, tx1 + 1):
                ch = level.tile(tx, ty)
                if level.solid_at(tx, ty):
                    body.y = ty * TILE - body.h
                    body.vy = 0.0
                    body.on_ground = True
                    landed = True
                    return landed, ceiling_hits
                if ch in ONEWAY_TILES and prev_bottom <= ty * TILE + 3.0:
                    body.y = ty * TILE - body.h
                    body.vy = 0.0
                    body.on_ground = True
                    body.standing_on_oneway = (tx, ty)
                    landed = True
                    return landed, ceiling_hits
    elif body.vy < 0:                    # rising: bump the head
        deepest = None
        for ty in range(ty1, ty0 - 1, -1):
            for tx in range(tx0, tx1 + 1):
                if level.solid_at(tx, ty):
                    deepest = ty if deepest is None else min(deepest, ty)
        if deepest is not None:
            for tx in range(tx0, tx1 + 1):
                if level.solid_at(tx, deepest):
                    ceiling_hits.append((tx, deepest))
            body.y = (deepest + 1) * TILE
            body.vy = 0.0
    return landed, ceiling_hits


def overlaps_hazard(level, x, y, w, h):
    """Return the first hazard tile overlapped, or ``None``."""
    tx0, ty0, tx1, ty1 = tile_range(x, y, w, h)
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            if level.tile(tx, ty) in ("^", "~"):
                return (tx, ty)
    return None


def bodies_touching(a, b) -> bool:
    return aabb(a.x, a.y, a.w, a.h, b.x, b.y, b.w, b.h)
