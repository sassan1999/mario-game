"""Headless-friendly game simulation for COMET ZIP.

This module owns rules and progression but knows nothing about Kivy.  A scene
view may render its public lists, while tests or alternate front ends can run
this world directly.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from collision import aabb
from config import CONFIG, TILE
from enemies import enemy_from_spawn
from entities import MovingPlatform
from levels import LEVELS
from particles import ParticleSystem
from player import Player
from powerups import MushroomManager
from projectiles import ProjectileManager


@dataclass
class Coin:
    x: float
    y: float
    collected: bool = False
    anim: float = 0.0

    w: float = 22.0
    h: float = 28.0

    @property
    def cx(self): return self.x + self.w / 2
    @property
    def cy(self): return self.y + self.h / 2


@dataclass
class Checkpoint:
    x: float
    y: float
    active: bool = False

    w: float = 36.0
    h: float = 76.0


@dataclass
class Goal:
    x: float
    y: float
    w: float = 56.0
    h: float = 96.0
    anim: float = 0.0


class GameWorld:
    def __init__(self):
        self.level_index = 0
        self.level = LEVELS[0]
        self.player = Player()
        self.enemies = []
        self.coins = []
        self.checkpoints = []
        self.goal = None
        self.platforms = []
        self.projectiles = ProjectileManager()
        self.powerups = MushroomManager()
        self.particles = ParticleSystem()
        self.score = 0
        self.coins_count = 0
        self.lives = int(CONFIG["player"]["lives"])
        self.time_left = 0.0
        self.elapsed = 0.0
        self.paused = False
        self.finished = False
        self.game_over = False
        self.last_event = ""
        self.respawn_x = 0.0
        self.respawn_y = 0.0
        self.message = ""
        self.message_timer = 0.0
        self.combo = 0
        self.rider = None
        self.load_level(0, fresh=True)

    @property
    def world_width(self): return self.level.world_width
    @property
    def world_height(self): return self.level.world_height

    def load_level(self, index, fresh=False):
        self.level_index = max(0, min(index, len(LEVELS) - 1))
        self.level = LEVELS[self.level_index]
        self.level.reset()
        difficulty = CONFIG["difficulty"].get(str(self.level_index + 1), {})
        p = CONFIG["player"]
        sx, sy = self.level.start_tile
        self.respawn_x = sx * TILE + 2
        self.respawn_y = sy * TILE + TILE - p["height"]
        self.player = Player(self.respawn_x, self.respawn_y)
        if not fresh and getattr(self, "_keep_power", False):
            self.player.power_up()
        self.enemies = []
        self.coins = []
        self.checkpoints = []
        for spawn in self.level.spawns:
            if spawn.kind == "coin":
                self.coins.append(Coin(spawn.x + 5, spawn.y + 2))
            elif spawn.kind == "checkpoint":
                self.checkpoints.append(Checkpoint(spawn.x, spawn.y - 45))
            elif spawn.kind == "goal":
                self.goal = Goal(spawn.x, spawn.y - 64)
            else:
                enemy = enemy_from_spawn(spawn, difficulty)
                if enemy is not None:
                    self.enemies.append(enemy)
        self.platforms = [MovingPlatform(spec.x, spec.y, spec.w, spec.h, "platform",
                                          axis=spec.axis, distance=spec.distance,
                                          speed=spec.speed, phase=spec.phase)
                          for spec in self.level.platforms]
        self.projectiles.clear()
        self.powerups.clear()
        self.elapsed = 0.0
        self.time_left = float(self.level.time_limit)
        self.finished = False
        self.game_over = False
        self.message = self.level.subtitle
        self.message_timer = 2.4
        self.combo = 0

    def start_new_game(self):
        self.score = 0
        self.coins_count = 0
        self.lives = int(CONFIG["player"]["lives"])
        self._keep_power = False
        self.load_level(0, fresh=True)

    def update(self, dt, controls, audio=None):
        """Advance one simulation frame. Audio is optional and duck-typed."""
        if self.paused or self.finished or self.game_over:
            self.particles.update(dt)
            return
        dt = min(float(dt), 1 / 30)
        self.elapsed += dt
        self.time_left -= dt
        self.message_timer = max(0.0, self.message_timer - dt)
        self.last_event = ""
        if self.time_left <= 0:
            self._lose_life("timeout", audio)
            return

        # Platforms move before bodies; a rider is carried by the delta once.
        self._update_platforms(dt)

        events = self.player.update(dt, controls, self.level, self.projectiles)
        self._play_events(events, audio)
        self._process_block_bumps(audio)

        # Enemies act after player movement, then contacts are resolved.
        for enemy in self.enemies:
            enemy.update(dt, self.level, self.player, self.projectiles)
        self._update_projectiles(dt, audio)
        self._collect_coins(audio)
        self._collect_powerups(audio)
        self._check_checkpoints(audio)
        self._check_enemy_contacts(audio)
        self._check_goal(audio)
        self._check_hazard_and_pit(audio)

        self.powerups.update(dt, self.level)
        self.particles.update(dt)
        self._cleanup_enemies()
        self._detect_platform_ground()

    def _update_platforms(self, dt):
        for platform in self.platforms:
            platform.update(dt)
        if self.rider is not None:
            self.player.translate(self.rider.dx, self.rider.dy)
            self.player.on_ground = True
            self.player.grounded_last = True
        self.rider = None

    def _detect_platform_ground(self):
        """Standing on a moving platform counts as ground for jump and animation."""
        p = self.player
        for platform in self.platforms:
            if (p.bottom >= platform.y - 6 and p.bottom <= platform.y + 16 and
                    p.right > platform.x + 4 and p.x < platform.x + platform.w - 4 and p.vy >= -10):
                p.on_ground = True
                p.grounded_last = True
                p.standing_platform = platform
                self.rider = platform
                if p.hurt_timer <= 0 and p.respawn_timer <= 0:
                    p.state = "run" if abs(p.vx) > 35 else "idle"
                return
        p.standing_platform = None

    def _play_events(self, events, audio):
        for event in events:
            self.last_event = event
            if audio:
                audio.play({"jump": "jump", "shoot": "shoot", "trail": "dash"}.get(event, event))
            if event == "trail":
                self.particles.trail(self.player.cx - self.player.facing * 12, self.player.cy, (123, 243, 255))
            elif event == "damage":
                self._damage_player(None, audio)

    def _process_block_bumps(self, audio):
        for tx, ty in self.player.last_ceiling_hits:
            tile = self.level.tile(tx, ty)
            if tile in "Bb":
                self.level.set_tile(tx, ty, ".")
                self.score += CONFIG["scoring"]["coin_block"]
                self.particles.emit(tx * TILE + 16, ty * TILE + 16, (246, 220, 158), 9, 160, 650, 4)
                if audio: audio.play("block_break")
            elif tile in "?%":
                self.level.set_tile(tx, ty, "X")
                self.score += CONFIG["scoring"]["coin_block"]
                # Bonus blocks alternate coin / Twilight Shroom rewards.
                if (tx + ty + self.level_index) % 2 == 0:
                    self.coins_count += 1
                    self.score += CONFIG["scoring"]["coin"]
                    self.message = "+1 SKY TOKEN"
                    if audio: audio.play("block_bonus")
                else:
                    self.powerups.spawn(tx * TILE + 1, (ty - 1) * TILE + 2)
                    self.message = "TWILIGHT SHROOM!"
                    if audio: audio.play("powerup")
                self.message_timer = 1.5

    def _collect_coins(self, audio):
        for coin in self.coins:
            coin.anim += 1 / 60
            if not coin.collected and aabb(self.player.x, self.player.y, self.player.w, self.player.h,
                                           coin.x, coin.y, coin.w, coin.h):
                coin.collected = True
                self.coins_count += 1
                self.score += CONFIG["scoring"]["coin"]
                self.combo += 1
                self.particles.emit(coin.cx, coin.cy, (255, 220, 64), 8, 170, 400, 3)
                if audio: audio.play("coin")

    def _collect_powerups(self, audio):
        for item in self.powerups.items:
            if not item.dead and aabb(self.player.x, self.player.y, self.player.w, self.player.h,
                                      item.x, item.y, item.w, item.h):
                item.dead = True
                self.player.power_up()
                self.score += 500
                self.message = "TWILIGHT FORM: EXTRA HIT"
                self.message_timer = 2.0
                self.particles.emit(item.cx, item.cy, (108, 246, 224), 20, 240, 240, 5)
                if audio: audio.play("powerup")

    def _check_checkpoints(self, audio):
        for cp in self.checkpoints:
            if not cp.active and aabb(self.player.x, self.player.y, self.player.w, self.player.h,
                                      cp.x, cp.y, cp.w, cp.h):
                cp.active = True
                self.respawn_x = cp.x
                self.respawn_y = cp.y + cp.h - self.player.h
                self.score += 250
                self.message = "CHECKPOINT LIT"
                self.message_timer = 1.6
                self.particles.emit(cp.x + cp.w / 2, cp.y + 20, (92, 255, 184), 16, 180, 300, 4)
                if audio: audio.play("checkpoint")

    def _check_enemy_contacts(self, audio):
        p = self.player
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            if not aabb(p.x, p.y, p.w, p.h, enemy.x, enemy.y, enemy.w, enemy.h):
                continue
            prev_bottom = p.prev_y + p.h
            stomp = enemy.stompable and p.vy >= 0 and prev_bottom <= enemy.y + 16
            if stomp:
                if enemy.take_hit(1, from_stomp=True):
                    p.vy = -CONFIG["physics"]["stomp_bounce"]
                    p.combo += 1
                    self.score += CONFIG["scoring"]["enemy"] + p.combo * CONFIG["scoring"]["combo_bonus"]
                    self.particles.emit(enemy.cx, enemy.y + enemy.h / 2, (255, 164, 88), 14, 230, 650, 5)
                    if audio: audio.play("stomp")
            else:
                self._damage_player(enemy.cx, audio)

    def _update_projectiles(self, dt, audio):
        self.projectiles.update(dt, self.level)
        for bolt in list(self.projectiles.items):
            if bolt.dead:
                continue
            if bolt.friendly:
                for enemy in self.enemies:
                    if enemy.alive and aabb(bolt.x, bolt.y, bolt.w, bolt.h, enemy.x, enemy.y, enemy.w, enemy.h):
                        if enemy.take_hit(bolt.damage):
                            bolt.dead = True
                            self.particles.emit(enemy.cx, enemy.cy, (123, 243, 255), 10, 210, 350, 4)
                            if not enemy.alive:
                                self.score += CONFIG["scoring"]["enemy"]
                            if audio: audio.play("stomp")
                            break
            else:
                if aabb(bolt.x, bolt.y, bolt.w, bolt.h, self.player.x, self.player.y, self.player.w, self.player.h):
                    bolt.dead = True
                    self._damage_player(bolt.x, audio)
        self.projectiles.items[:] = [p for p in self.projectiles.items if not p.dead]

    def _damage_player(self, source_x, audio):
        result = self.player.take_damage(source_x)
        if result == "ignored":
            return
        self.particles.emit(self.player.cx, self.player.cy, (255, 90, 90), 12, 220, 550, 4)
        if audio: audio.play("hurt")
        if result == "lost_life":
            self._lose_life("hit", audio)
        else:
            self.message = "POWER SHIELD BROKEN"
            self.message_timer = 1.2

    def _check_hazard_and_pit(self, audio):
        p = self.player
        if p.y > self.level.world_height + 96:
            self._lose_life("pit", audio)

    def _lose_life(self, reason, audio):
        if self.player.respawn_timer > 0:
            return
        self.lives -= 1
        if audio: audio.play("hurt" if reason != "timeout" else "game_over")
        self.player.respawn_timer = CONFIG["player"]["respawn_delay"]
        self.particles.emit(self.player.cx, self.player.cy, (255, 90, 90), 22, 300, 800, 5)
        if self.lives <= 0:
            self.game_over = True
            self.message = "RUN ENDED"
            self.message_timer = 999
            if audio: audio.play("game_over")
            return
        self._keep_power = self.player.powered
        self.player.reset_at(self.respawn_x, self.respawn_y)
        if self._keep_power:
            self.player.power_up()
        self.message = "BACK TO THE LAST BEACON"
        self.message_timer = 1.5
        self.projectiles.clear()
        self.powerups.clear()

    def _check_goal(self, audio):
        if not self.goal or not aabb(self.player.x, self.player.y, self.player.w, self.player.h,
                                     self.goal.x, self.goal.y, self.goal.w, self.goal.h):
            return
        self.score += CONFIG["scoring"]["level_clear"]
        self.score += min(int(self.time_left), CONFIG["scoring"]["time_bonus_cap"] // CONFIG["scoring"]["time_bonus_per_second"]) * CONFIG["scoring"]["time_bonus_per_second"]
        if self.level_index + 1 >= len(LEVELS):
            self.finished = True
            self.message = "THE SKYLINE IS YOURS!"
            if audio: audio.play("goal")
        else:
            self.level_index += 1
            self._keep_power = self.player.powered
            self.load_level(self.level_index)
            if audio: audio.play("goal")

    def _cleanup_enemies(self):
        self.enemies[:] = [e for e in self.enemies if e.alive or e.squash_timer > 0]

    def restart_after_game_over(self):
        self.start_new_game()
