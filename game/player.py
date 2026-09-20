"""Player controller for Comet Zip.

The player is deliberately independent from Kivy.  It consumes a small
ControlState-like object and emits gameplay events for the UI/audio layer.
"""
from __future__ import annotations

from physics import Body, accelerate_x, apply_friction, apply_gravity, jump, move_and_collide
from collision import aabb, overlaps_hazard
from config import CONFIG, TILE


class Player(Body):
    def __init__(self, x=0.0, y=0.0):
        p = CONFIG["player"]
        super().__init__(x, y, p["width"], p["height"])
        self.small_size = (p["width"], p["height"])
        self.big_size = (p["big_width"], p["big_height"])
        self.facing = 1
        self.anim_time = 0.0
        self.state = "idle"
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.attack_cooldown = 0.0
        self.invuln = 0.0
        self.hurt_timer = 0.0
        self.respawn_timer = 0.0
        self.powered = False
        self.power_flash = 0.0
        self.combo = 0
        self.dash_trail_timer = 0.0
        self.last_stomp = False
        self.last_ceiling_hits = []
        self.jump_active = False

    @property
    def center(self):
        return self.cx, self.cy

    def resize_for_power(self, big: bool):
        old_bottom = self.bottom
        self.w, self.h = self.big_size if big else self.small_size
        self.y = old_bottom - self.h

    def power_up(self):
        self.powered = True
        self.resize_for_power(True)
        self.power_flash = 1.0

    def lose_power(self):
        self.powered = False
        self.resize_for_power(False)
        self.power_flash = 0.35

    def reset_at(self, x, y):
        self.move_to(x, y)
        self.vx = self.vy = 0.0
        self.coyote = self.jump_buffer = 0.0
        self.invuln = 0.65
        self.hurt_timer = 0.0
        self.respawn_timer = 0.0
        self.on_ground = False
        self.state = "idle"
        self.last_stomp = False

    def update(self, dt, controls, level, projectiles):
        """Advance one frame and return a list of semantic events."""
        events = []
        self.prev_x, self.prev_y = self.x, self.y
        self.anim_time += dt
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.invuln = max(0.0, self.invuln - dt)
        self.power_flash = max(0.0, self.power_flash - dt)
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.dash_trail_timer = max(0.0, self.dash_trail_timer - dt)
        self.last_stomp = False

        if self.respawn_timer > 0:
            self.respawn_timer -= dt
            self.vx *= 0.90
            apply_gravity(self, dt, CONFIG["physics"]["gravity"], CONFIG["physics"]["max_fall_speed"])
            self.y += self.vy * dt
            return events

        if self.on_ground:
            self.coyote = CONFIG["physics"]["coyote_time"]
        else:
            self.coyote = max(0.0, self.coyote - dt)

        if controls.consume_jump():
            self.jump_buffer = CONFIG["physics"]["jump_buffer_time"]
        else:
            self.jump_buffer = max(0.0, self.jump_buffer - dt)

        axis = controls.move_axis
        phys = CONFIG["physics"]
        max_speed = phys["player_run_speed"]
        if axis:
            self.facing = 1 if axis > 0 else -1
            accel = phys["player_accel"] if self.on_ground else phys["player_air_accel"]
            accelerate_x(self, dt, max_speed, axis)
        else:
            friction = phys["ground_friction"] if self.on_ground else phys["air_friction"]
            if level.tile_at_world(self.cx, self.bottom + 2) == "I":
                friction = phys["ice_friction"]
            apply_friction(self, dt, friction)

        if self.jump_buffer > 0 and (self.on_ground or self.coyote > 0):
            jump(self, phys["jump_velocity"])
            self.jump_buffer = 0.0
            self.coyote = 0.0
            self.jump_active = True
            events.append("jump")

        # Release-to-short-hop: hearts the jump only after a real release.
        if self.jump_active and not controls.is_down("jump"):
            self.jump_active = False
            if self.vy < -140:
                self.vy *= phys["jump_cut_multiplier"]

        if controls.consume_attack() and self.attack_cooldown <= 0:
            projectiles.spawn_player_bolt(self)
            self.attack_cooldown = CONFIG["player"]["attack_cooldown"]
            events.append("shoot")

        previous_bottom = self.bottom
        was_falling = self.vy > 0
        apply_gravity(self, dt, phys["gravity"], phys["max_fall_speed"])
        head_hits = move_and_collide(self, dt, level, phys["max_step_px"])
        self.last_ceiling_hits = head_hits
        if head_hits:
            events.append("bump")

        # Head bumps can alter breakable/bonus tiles. The world handles the
        # actual reward and replaces the tile after receiving this event.
        self.last_stomp = was_falling and previous_bottom < self.y + self.h + 2
        if self.on_ground and abs(self.vx) > 30:
            self.dash_trail_timer = 0.055
        if self.dash_trail_timer > 0:
            events.append("trail")

        hazard = overlaps_hazard(level, self.x + 3, self.y + 3, self.w - 6, self.h - 5)
        if hazard and self.invuln <= 0:
            events.append("damage")

        if self.hurt_timer > 0:
            self.state = "hurt"
        elif not self.on_ground:
            self.state = "jump" if self.vy < 0 else "fall"
        elif abs(self.vx) > 35:
            self.state = "run"
        else:
            self.state = "idle"
        return events

    def take_damage(self, source_x=None):
        if self.invuln > 0 or self.respawn_timer > 0:
            return "ignored"
        self.invuln = CONFIG["player"]["invuln_time"]
        self.hurt_timer = 0.32
        self.vy = -360.0
        if source_x is not None:
            self.vx = -260.0 if source_x > self.cx else 260.0
        if self.powered:
            self.lose_power()
            return "lost_power"
        return "lost_life"

    def fire_frame(self):
        return int(self.anim_time * 10) % 2

    def sprite_frame(self):
        counts = {"idle": 4, "run": 8, "jump": 2, "fall": 2, "hurt": 2, "shoot": 2, "skid": 2}
        name = self.state
        return name, int(self.anim_time * (10 if name == "run" else 6)) % counts[name]
