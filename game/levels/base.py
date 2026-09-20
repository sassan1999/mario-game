"""Level data, a coordinate-based builder, and runtime world objects.

Maps are one character per 32px tile, top-to-bottom.  ``LevelBuilder`` lets a
level be authored in *tile coordinates* (much less error-prone than hand-drawn
ASCII) and emits the same grid format ``LevelData`` consumes, plus a
``validate()`` pass that guarantees the player physically fits.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from config import ENTITY_CHARS, EMPTY, HAZARD_TILES, ONEWAY_TILES, SOLID_TILES, TILE


@dataclass
class Spawn:
    kind: str
    x: float
    y: float
    data: dict = field(default_factory=dict)


@dataclass
class MovingPlatformSpec:
    x: float
    y: float
    w: float = TILE * 3
    h: float = TILE * 0.45
    axis: str = "x"
    distance: float = TILE * 5
    speed: float = 70.0
    phase: float = 0.0


class LevelData:
    """A level template plus its mutable tile grid (breakable/bonus tiles)."""

    def __init__(self, name: str, subtitle: str, rows: Iterable[str], time_limit: int,
                 theme: str, start: tuple[int, int], goal_hint: str = ""):
        raw = [str(row) for row in rows]
        width = max(len(row) for row in raw)
        self.name = name
        self.subtitle = subtitle
        self.theme = theme
        self.time_limit = time_limit
        self.goal_hint = goal_hint
        self.width = width
        self.height = len(raw)
        self.start_tile = start
        self.rows: list[list[str]] = []
        self.spawns: list[Spawn] = []
        self.platforms: list[MovingPlatformSpec] = []
        self.checkpoints: list[tuple[float, float]] = []
        self.goal: tuple[float, float] | None = None
        self._parse(raw)
        self.initial_tiles = tuple(tuple(r) for r in self.rows)
        self.tiles = [list(r) for r in self.rows]

    def _parse(self, raw: list[str]):
        for ty, source in enumerate(raw):
            row = list(source.ljust(self.width, EMPTY)[: self.width])
            for tx, char in enumerate(row):
                if char in ENTITY_CHARS:
                    kind = ENTITY_CHARS[char]
                    x, y = tx * TILE + 2, ty * TILE
                    if kind == "player_start":
                        self.start_tile = (tx, ty)
                    elif kind == "checkpoint":
                        self.checkpoints.append((x, y))
                        self.spawns.append(Spawn(kind, x, y))
                    elif kind == "goal":
                        self.goal = (x, y)
                        self.spawns.append(Spawn(kind, x, y))
                    elif kind in ("mover_h", "mover_v"):
                        axis = "x" if kind == "mover_h" else "y"
                        self.platforms.append(MovingPlatformSpec(x, y + 11, axis=axis))
                    else:
                        self.spawns.append(Spawn(kind, x, y))
                    row[tx] = EMPTY
            self.rows.append(row)

    def reset(self):
        self.tiles = [list(r) for r in self.initial_tiles]

    def tile(self, tx: int, ty: int) -> str:
        if tx < 0 or tx >= self.width or ty < 0:
            return EMPTY
        if ty >= self.height:
            return EMPTY
        return self.tiles[ty][tx]

    def tile_at_world(self, x: float, y: float) -> str:
        return self.tile(int(x // TILE), int(y // TILE))

    def set_tile(self, tx: int, ty: int, value: str):
        if 0 <= tx < self.width and 0 <= ty < self.height:
            self.tiles[ty][tx] = value

    def solid_at(self, tx: int, ty: int) -> bool:
        return self.tile(tx, ty) in SOLID_TILES

    def hazard_at(self, tx: int, ty: int) -> bool:
        return self.tile(tx, ty) in HAZARD_TILES

    def standable_at(self, tx: int, ty: int) -> bool:
        return self.solid_at(tx, ty) or self.tile(tx, ty) in ONEWAY_TILES

    def blocks_below(self, x: float, y: float, w: float, h: float) -> bool:
        tx0 = int((x + 1) // TILE)
        tx1 = int((x + w - 1) // TILE)
        ty = int((y + h + 1) // TILE)
        return any(self.standable_at(tx, ty) for tx in range(tx0, tx1 + 1))

    @property
    def world_width(self):
        return self.width * TILE

    @property
    def world_height(self):
        return self.height * TILE


def rows_from_text(text: str) -> list[str]:
    return [line.rstrip("\n") for line in text.strip("\n").splitlines()]


class LevelBuilder:
    """Paint a level in tile coordinates and validate it before shipping."""

    GROUND_ROW = 14

    def __init__(self, name, subtitle, width=100, height=16, time_limit=180,
                 theme="meadow", start=(3, GROUND_ROW - 1), goal_hint=""):
        self.name = name
        self.subtitle = subtitle
        self.width = width
        self.height = height
        self.time_limit = time_limit
        self.theme = theme
        self.start = start
        self.goal_hint = goal_hint
        self.grid = [[EMPTY] * width for _ in range(height)]
        self.movers: list[MovingPlatformSpec] = []
        self.problems: list[str] = []
        self._checks = []          # (label, x0, x1) walkable stretches for validation

    # ------------------------------------------------------------ painting
    def _set(self, x, y, char):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = char

    def fill(self, x0, y0, x1, y1, char="#"):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self._set(x, y, char)

    def ground(self, x0, x1, row=None, char="#"):
        row = self.GROUND_ROW if row is None else row
        self.fill(x0, row, x1, self.height - 1, char)
        self._checks.append(("ground", x0, x1, row))
        return self

    def platform(self, x, y, w=3, char="="):
        for i in range(w):
            self._set(x + i, y, char)
        self._checks.append(("platform", x, x + w - 1, y))
        return self

    def block(self, x, y, w=1, h=1, char="#", walkable_top=False):
        for j in range(h):
            for i in range(w):
                self._set(x + i, y + j, char)
        if walkable_top:
            self._checks.append(("block", x, x + w - 1, y))
        return self

    def hazard(self, x, y, w=1, char="^"):
        for i in range(w):
            self._set(x + i, y, char)
        return self

    def stairs(self, x, y, steps, w=1, char="#"):
        for s in range(steps):
            self.block(x + s * w, y - s, w, s + 1, char, walkable_top=True)
        return self

    # --------------------------------------------------------------- items
    def coin(self, x, y, n=1, step=1):
        for i in range(n):
            self._set(x + i * step, y, "o")
        return self

    def coin_arc(self, x, y, n=5):
        for i in range(n):
            dy = -1 if i in (0, n - 1) else (-2 if i in (1, n - 2) else -3)
            self._set(x + i, y + dy, "o")
        return self

    def enemy(self, kind, x, y):
        glyph = {"grubbo": "1", "zippbat": "2", "bouncer": "3", "spitter": "4", "rammer": "5"}[kind]
        self._set(x, y, glyph)
        return self

    def checkpoint(self, x, y):
        self._set(x, y, "K")
        return self

    def goal(self, x, y):
        self._set(x, y, "E")
        return self

    def mover(self, x, y, axis="x", distance=TILE * 4, speed=70.0, w=TILE * 3):
        self.movers.append(MovingPlatformSpec(x * TILE + 2, y * TILE + 11, w=w, h=TILE * .45,
                                              axis=axis, distance=distance, speed=speed))
        self._checks.append(("mover", x, x + 2, y))
        return self

    def breakable_row(self, x, y, w=1):
        return self.block(x, y, w, 1, "B", walkable_top=False)

    def bonus(self, x, y, char="?"):
        self._set(x, y, char)
        return self

    # ---------------------------------------------------------- validation
    def validate(self, player_height=42):
        """Catch genuinely impassable geometry.

        The player box is 42px tall while a tile is 32px, so:
          * solid directly above a surface            -> a step/wall (fine)
          * exactly one empty tile then solid above   -> a tunnel nobody fits (error)
        """
        self.problems = []
        self.step_tiles = []
        for label, x0, x1, y in self._checks:
            for x in range(x0, x1 + 1):
                near = self.grid[y - 1][x] if y - 1 >= 0 else EMPTY
                far = self.grid[y - 2][x] if y - 2 >= 0 else EMPTY
                if near in SOLID_TILES:
                    continue                      # obstacle standing on the surface
                if far in SOLID_TILES or far in ONEWAY_TILES:
                    self.problems.append(f"tunnel too low above {label} at ({x},{y - 2})")
        sx, sy = self.start
        for dy in range(1, 3):
            if self.grid[sy - dy][sx] in SOLID_TILES:
                self.problems.append(f"start headroom blocked at ({sx},{sy - dy})")
        if self.grid[sy + 1][sx] not in SOLID_TILES:
            self.problems.append(f"start tile ({sx},{sy}) is floating")
        return self

    def build(self):
        rows = ["".join(row) for row in self.grid]
        level = LevelData(self.name, self.subtitle, rows, self.time_limit, self.theme,
                          self.start, self.goal_hint)
        level.platforms.extend(self.movers)
        return level
