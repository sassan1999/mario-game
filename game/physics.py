"""Body kinematics: gravity, acceleration, friction, jump and swept movement."""
from __future__ import annotations

from collision import resolve_x, resolve_y, tile_range
from config import TILE


class Body:
    """A movable axis-aligned box.  ``x, y`` is the top-left corner."""

    __slots__ = ("x", "y", "w", "h", "vx", "vy", "on_ground", "facing", "wall_hit",
                 "standing_on_oneway", "prev_x", "prev_y", "gravity_scale",
                 "grounded_last", "standing_platform")

    def __init__(self, x=0.0, y=0.0, w=TILE, h=TILE):
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)
        self.h = float(h)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.grounded_last = False
        self.facing = 1
        self.wall_hit = 0
        self.standing_on_oneway = None
        self.standing_platform = None
        self.prev_x = float(x)
        self.prev_y = float(y)
        self.gravity_scale = 1.0

    # -- geometry helpers ---------------------------------------------------
    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.w

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.h

    @property
    def cx(self):
        return self.x + self.w * 0.5

    @property
    def cy(self):
        return self.y + self.h * 0.5

    def move_to(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def translate(self, dx, dy):
        self.x += dx
        self.y += dy

    def __repr__(self):                                  # pragma: no cover
        return f"<{type(self).__name__} x={self.x:.1f} y={self.y:.1f} v=({self.vx:.0f},{self.vy:.0f})>"


# --------------------------------------------------------------------------
# scalar helpers
# --------------------------------------------------------------------------
def approach(value: float, target: float, delta: float) -> float:
    if value < target:
        return min(value + delta, target)
    if value > target:
        return max(value - delta, target)
    return value


def apply_gravity(body: Body, dt: float, gravity: float, max_fall: float) -> None:
    if body.on_ground:
        return
    body.vy += gravity * body.gravity_scale * dt
    if body.vy > max_fall:
        body.vy = max_fall


def accelerate_x(body: Body, dt: float, accel: float, direction: int) -> None:
    body.vx = approach(body.vx, accel * direction, accel * dt)


def apply_friction(body: Body, dt: float, friction: float) -> None:
    body.vx = approach(body.vx, 0.0, friction * dt)


def jump(body: Body, velocity: float) -> None:
    body.vy = -velocity
    body.on_ground = False


# --------------------------------------------------------------------------
# swept movement with tile resolution
# --------------------------------------------------------------------------
def move_and_collide(body: Body, dt: float, level, max_step: float = 14.0):
    """Integrate the body and resolve collisions. Returns head-bumped tiles."""
    dx = body.vx * dt
    dy = body.vy * dt
    steps = 1
    longest = max(abs(dx), abs(dy))
    if longest > max_step:
        steps = int(longest / max_step) + 1
    sx = dx / steps
    sy = dy / steps

    ceiling_hits = []
    body.on_ground = False
    body.standing_on_oneway = None
    prev_grounded = body.grounded_last

    for _ in range(steps):
        prev_bottom = body.bottom
        if sx:
            body.x += sx
            resolve_x(body, level)
        if sy:
            body.y += sy
            hits = []
            landed, hits = resolve_y(body, level, prev_bottom)
            if hits:
                ceiling_hits.extend(hits)

    if body.vy >= 0.0 and level.blocks_below(body.x, body.y, body.w, body.h):
        body.on_ground = True
    body.grounded_last = body.on_ground
    if not prev_grounded and body.on_ground:
        body.wall_hit = body.wall_hit
    if body.on_ground and body.vy > 0:
        body.vy = 0.0
    return ceiling_hits


def snap_to_ground_checks(body: Body, level, probe: float = 2.0) -> bool:
    """True when a solid/one-way tile is directly below the body."""
    tx0, tx1, ty = tile_range(body.x + 1, body.y, body.w - 2, 0)[0], 0, 0
    ty = int((body.bottom + probe) // TILE)
    tx0 = int(body.x // TILE)
    tx1 = int((body.right - EPS_TILE) // TILE)
    for tx in range(tx0, tx1 + 1):
        if level.solid_at(tx, ty) or level.tile(tx, ty) == "=":
            return True
    return False


EPS_TILE = 0.01


def is_grounded(body: Body, level) -> bool:
    return snap_to_ground_checks(body, level)
