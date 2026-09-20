"""Small shared entity primitives used by the simulation and renderer."""
from __future__ import annotations

from dataclasses import dataclass, field

from physics import Body


@dataclass
class Entity:
    x: float
    y: float
    w: float
    h: float
    kind: str
    alive: bool = True
    active: bool = True
    anim_time: float = 0.0
    hit_flash: float = 0.0

    @property
    def cx(self):
        return self.x + self.w * 0.5

    @property
    def cy(self):
        return self.y + self.h * 0.5

    def update_animation(self, dt: float):
        self.anim_time += dt
        self.hit_flash = max(0.0, self.hit_flash - dt)


@dataclass
class MovingPlatform(Entity):
    axis: str = "x"
    origin_x: float = 0.0
    origin_y: float = 0.0
    distance: float = 160.0
    speed: float = 70.0
    phase: float = 0.0
    previous_x: float = 0.0
    previous_y: float = 0.0

    def __post_init__(self):
        self.origin_x = self.x
        self.origin_y = self.y
        self.previous_x = self.x
        self.previous_y = self.y

    @property
    def dx(self):
        return self.x - self.previous_x

    @property
    def dy(self):
        return self.y - self.previous_y

    def update(self, dt: float):
        import math
        self.previous_x, self.previous_y = self.x, self.y
        self.phase += dt * self.speed / max(1.0, self.distance)
        offset = math.sin(self.phase) * self.distance
        if self.axis == "x":
            self.x = self.origin_x + offset
        else:
            self.y = self.origin_y + offset
        self.anim_time += dt
