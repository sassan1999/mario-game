"""Smooth side-scrolling camera with look-ahead and impact shake."""
from __future__ import annotations

import math

from config import CONFIG, DESIGN_HEIGHT, DESIGN_WIDTH


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.look_ahead = 0.0
        self.shake = 0.0
        self.world_width = DESIGN_WIDTH
        self.world_height = DESIGN_HEIGHT
        self.viewport_w = DESIGN_WIDTH
        self.viewport_h = DESIGN_HEIGHT

    def resize(self, width, height):
        self.viewport_w = max(1.0, float(width))
        self.viewport_h = max(1.0, float(height))

    def set_world_bounds(self, width, height):
        self.world_width = max(self.viewport_w, float(width))
        self.world_height = max(self.viewport_h, float(height))
        self._clamp_targets()

    def _clamp_targets(self):
        self.target_x = max(0.0, min(self.target_x, max(0.0, self.world_width - self.viewport_w)))
        self.target_y = max(0.0, min(self.target_y, max(0.0, self.world_height - self.viewport_h)))

    def snap_to(self, x, y):
        self.x = self.target_x = float(x)
        self.y = self.target_y = float(y)
        self._clamp_targets()
        self.x, self.y = self.target_x, self.target_y

    def focus(self, player, dt):
        cfg = CONFIG["camera"]
        desired_look = player.vx * 0.28 + player.facing * cfg["look_ahead"]
        self.look_ahead += (desired_look - self.look_ahead) * min(1.0, dt * cfg["look_ahead_lerp"])
        center_x = player.cx - self.viewport_w * 0.5 + self.look_ahead
        center_y = player.cy - self.viewport_h * 0.5
        margin = cfg["dead_zone_x"]
        if player.cx - self.x < margin:
            center_x = player.cx - margin
        elif player.cx - self.x > self.viewport_w - margin:
            center_x = player.cx - self.viewport_w + margin
        self.target_x = center_x
        self.target_y = center_y
        self._clamp_targets()
        factor = min(1.0, dt * cfg["lerp"])
        self.x += (self.target_x - self.x) * factor
        self.y += (self.target_y - self.y) * min(1.0, dt * cfg["vertical_lerp"])
        self.x = max(0.0, min(self.x, max(0.0, self.world_width - self.viewport_w)))
        self.y = max(0.0, min(self.y, max(0.0, self.world_height - self.viewport_h)))
        self.shake = max(0.0, self.shake - dt * cfg["shake_decay"])

    def bump(self, amount=8.0):
        self.shake = max(self.shake, amount)

    def offset(self, t=0.0):
        if not self.shake:
            return self.x, self.y
        return (self.x + math.sin(t * 31.0) * self.shake,
                self.y + math.cos(t * 37.0) * self.shake * 0.45)
