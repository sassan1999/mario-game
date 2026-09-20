"""Lightweight pooled-ish particle effects; intentionally bounded for phones."""
from __future__ import annotations

import math
import random


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color", "gravity", "kind")

    def __init__(self, x, y, vx, vy, life, size, color, gravity=700.0, kind="dot"):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = self.max_life = life
        self.size, self.color, self.gravity, self.kind = size, color, gravity, kind

    def update(self, dt):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        return self.life > 0


class ParticleSystem:
    def __init__(self, max_particles=260):
        self.items = []
        self.max_particles = max_particles
        self.random = random.Random(7)

    def emit(self, x, y, color=(255, 255, 255), count=8, speed=180, gravity=700, size=4, kind="dot"):
        for _ in range(count):
            if len(self.items) >= self.max_particles:
                self.items.pop(0)
            a = self.random.random() * math.tau
            s = speed * (0.35 + self.random.random() * 0.9)
            self.items.append(Particle(x, y, math.cos(a) * s, math.sin(a) * s,
                                       0.3 + self.random.random() * 0.45,
                                       size * (0.65 + self.random.random() * 0.8), color, gravity, kind))

    def trail(self, x, y, color=(123, 243, 255)):
        if len(self.items) < self.max_particles - 2:
            self.items.append(Particle(x, y, 0, 0, .18, 5, color, 0, "trail"))

    def update(self, dt):
        self.items[:] = [p for p in self.items if p.update(dt)]
