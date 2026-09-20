"""Five original enemy archetypes with their own AI behaviours.

grubbo  : ground patroller, turns at walls and ledges, stompable.
zippbat : aerial looper that drifts on a sine wave, dives when it scents you.
bouncer : springs into the air on a timer, stompable only at the apex.
spitter : rooted turret that lobs spores along its line of sight.
rammer  : armoured charger, shrugs off stomps, must be shot or outrun.
"""
from __future__ import annotations

import math
import random

from config import CONFIG
from physics import Body, apply_gravity, move_and_collide

TILE = 32


class Enemy(Body):
    kind = "enemy"
    anim_name = "walk"
    frame_count = 4
    hp = 1
    stompable = True
    contact_damage = 1
    score = 200

    def __init__(self, x, y, w=40, h=36, difficulty=None):
        super().__init__(x, y, w, h)
        self.difficulty = difficulty or {"enemy_speed": 1.0, "enemy_hp_bonus": 0}
        self.hp = self.hp + int(self.difficulty.get("enemy_hp_bonus", 0))
        self.alive = True
        self.defeated = False
        self.squash_timer = 0.0
        self.anim_time = random.random() * 2.0
        self.start_x, self.start_y = float(x), float(y)
        self.hit_flash = 0.0
        self.facing = -1
        self.invuln = 0.0
        self.ai_timer = 0.0

    # ------------------------------------------------------------------ api
    def take_hit(self, damage=1, from_stomp=False):
        """Returns True when the hit actually landed."""
        if not self.alive or self.invuln > 0:
            return False
        if from_stomp and not self.stompable:
            return False
        self.hp -= damage
        self.hit_flash = 0.16
        self.invuln = 0.12
        if self.hp <= 0:
            self.defeat()
        return True

    def defeat(self):
        self.alive = False
        self.defeated = True
        self.squash_timer = 0.34
        self.vx = self.vy = 0.0

    def update(self, dt, level, player, projectiles):
        self.anim_time += dt
        self.hit_flash = max(0.0, self.hit_flash - dt)
        self.invuln = max(0.0, self.invuln - dt)
        if self.defeated:
            self.squash_timer -= dt
            return
        self.think(dt, level, player, projectiles)

    def think(self, dt, level, player, projectiles):
        raise NotImplementedError

    # -------------------------------------------------------------- helpers
    def speed(self, base):
        return base * float(self.difficulty.get("enemy_speed", 1.0))

    def player_distance(self, player):
        return math.hypot(player.cx - self.cx, player.cy - self.cy)

    def see_player(self, player, radius=260.0):
        return self.player_distance(player) < radius

    def apply_walk(self, dt, level, speed):
        self.vx = speed * self.facing
        apply_gravity(self, dt, CONFIG["physics"]["gravity"], CONFIG["physics"]["max_fall_speed"])
        move_and_collide(self, dt, level, 12.0)
        if self.wall_hit:
            self.facing = -self.facing
            self.wall_hit = 0
        elif self.on_ground and not self.ground_ahead(level):
            self.facing = -self.facing

    def ground_ahead(self, level, probe=6.0):
        tx = int((self.cx + self.facing * (self.w * 0.5 + probe)) // TILE)
        ty = int((self.bottom + 4) // TILE)
        return level.solid_at(tx, ty) or level.tile(tx, ty) == "="

    def wall_ahead(self, level):
        tx = int((self.cx + self.facing * (self.w * 0.5 + 6)) // TILE)
        ty0, ty1 = int(self.top // TILE), int((self.bottom - 4) // TILE)
        return any(level.solid_at(tx, ty) for ty in range(ty0, ty1 + 1))

    def anim_frame(self):
        return int(self.anim_time * 8.0) % self.frame_count


# --------------------------------------------------------------------------
class Grubbo(Enemy):
    """Stout ground beetle that marches a fixed beat and turns on a dime."""
    kind = "grubbo"
    frame_count = 4
    hp = 1
    stompable = True

    def __init__(self, x, y, difficulty=None):
        super().__init__(x, y, 44, 34, difficulty)

    def think(self, dt, level, player, projectiles):
        self.apply_walk(dt, level, self.speed(56))


class ZippBat(Enemy):
    """Bat that loops through the air and swoops at anything close."""
    kind = "zippbat"
    frame_count = 4
    hp = 1
    stompable = True

    def __init__(self, x, y, difficulty=None):
        super().__init__(x, y, 40, 32, difficulty)
        self.base_y = self.y
        self.base_x = self.x
        self.phase = random.random() * math.tau
        self.mode = "patrol"
        self.target_x, self.target_y = self.x, self.y

    def think(self, dt, level, player, projectiles):
        self.ai_timer -= dt
        if self.see_player(player, 230) and self.ai_timer <= 0:
            self.mode = "swoop"
            self.target_x, self.target_y = player.cx, player.cy
            self.ai_timer = 1.4
        elif self.ai_timer <= 0:
            self.mode = "patrol"
        if self.mode == "swoop":
            dx, dy = self.target_x - self.cx, self.target_y - self.cy
            dist = max(1.0, math.hypot(dx, dy))
            spd = self.speed(150)
            self.x += dx / dist * spd * dt
            self.y += dy / dist * spd * dt
            self.facing = 1 if dx > 0 else -1
            if dist < 24 and self.ai_timer < 1.0:
                self.ai_timer = 0.0
        else:
            self.phase += dt * 2.2
            self.x = self.base_x + math.sin(self.phase) * 54
            self.y = self.base_y + math.sin(self.phase * 1.7) * 30
            self.facing = 1 if math.cos(self.phase) > 0 else -1


class Bouncer(Enemy):
    """Spring-fruit that hops in long arcs; stomping it mid-air is safest."""
    kind = "bouncer"
    frame_count = 2
    hp = 1
    stompable = True

    def __init__(self, x, y, difficulty=None):
        super().__init__(x, y, 40, 34, difficulty)
        self.hop_timer = 0.6
        self.airborne = False

    def think(self, dt, level, player, projectiles):
        gravity = CONFIG["physics"]["gravity"]
        if self.on_ground:
            self.airborne = False
            self.hop_timer -= dt
            self.vx *= 0.86
            if self.hop_timer <= 0:
                self.hop_timer = 1.15
                dir_to_player = 1 if player.cx > self.cx else -1
                if self.player_distance(player) > 300:
                    dir_to_player = self.facing
                self.facing = dir_to_player
                self.vy = -self.speed(560)
                self.vx = self.speed(96) * self.facing
                self.airborne = True
        apply_gravity(self, dt, gravity, CONFIG["physics"]["max_fall_speed"])
        move_and_collide(self, dt, level, 12.0)
        if self.wall_hit:
            self.facing = -self.facing
            self.vx = abs(self.vx) * self.facing
            self.wall_hit = 0

    def anim_frame(self):
        return 0 if self.on_ground else 1


class Spitter(Enemy):
    """Potato-shaped turret; fires a spore when it can see the player."""
    kind = "spitter"
    frame_count = 4
    hp = 2
    stompable = True

    def __init__(self, x, y, difficulty=None):
        super().__init__(x, y, 42, 42, difficulty)
        self.cooldown = 1.0 + random.random()
        self.charge = 0.0
        self.facing = -1

    def think(self, dt, level, player, projectiles):
        if not self.on_ground:
            apply_gravity(self, dt, CONFIG["physics"]["gravity"], CONFIG["physics"]["max_fall_speed"])
            move_and_collide(self, dt, level, 12.0)
        if player.cx > self.cx:
            self.facing = 1
        else:
            self.facing = -1
        self.charge = max(0.0, self.charge - dt)
        self.cooldown -= dt
        in_range = self.see_player(player, 420) and abs(player.cy - self.cy) < 190
        if in_range and self.cooldown <= 0 and projectiles is not None:
            projectiles.spawn_spore(self, player.cx, player.cy)
            self.cooldown = 1.7
            self.charge = 0.35

    def anim_frame(self):
        return 0 if self.charge > 0 else int(self.anim_time * 5) % self.frame_count


class Rammer(Enemy):
    """Armoured bruiser: stomps bounce off, so shoot it or get out of the way."""
    kind = "rammer"
    frame_count = 4
    hp = 3
    stompable = False
    contact_damage = 1

    def __init__(self, x, y, difficulty=None):
        super().__init__(x, y, 46, 40, difficulty)
        self.charge_timer = 0.0
        self.windup = 0.0
        self.patrol_span = 260.0

    def think(self, dt, level, player, projectiles):
        if self.windup > 0:
            self.windup -= dt
            self.vx *= 0.8
            apply_gravity(self, dt, CONFIG["physics"]["gravity"], CONFIG["physics"]["max_fall_speed"])
            move_and_collide(self, dt, level, 12.0)
            return
        same_height = abs(player.cy - self.cy) < 70
        if self.see_player(player, 320) and same_height:
            self.facing = 1 if player.cx > self.cx else -1
            if self.charge_timer <= 0:
                self.charge_timer = 2.6
            self.apply_walk(dt, level, self.speed(210))
            if self.wall_hit:
                self.windup = 0.5
                self.wall_hit = 0
        else:
            self.apply_walk(dt, level, self.speed(62))
            if abs(self.cx - self.start_x) > self.patrol_span:
                self.facing = 1 if self.cx < self.start_x else -1


FACTORY = {
    "grubbo": Grubbo,
    "zippbat": ZippBat,
    "bouncer": Bouncer,
    "spitter": Spitter,
    "rammer": Rammer,
}


def enemy_from_spawn(spawn, difficulty):
    cls = FACTORY.get(spawn.kind)
    if cls is None:
        return None
    if cls is Grubbo:
        return cls(spawn.x, spawn.y + 4, difficulty)
    if cls is ZippBat:
        return cls(spawn.x, spawn.y + 14, difficulty)
    return cls(spawn.x, spawn.y + 2, difficulty)
