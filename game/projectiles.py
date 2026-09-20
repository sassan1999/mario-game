"""Energy projectiles: the player's charged bolt and enemy spores."""
from __future__ import annotations

from config import CONFIG
from physics import Body


class Projectile(Body):
    def __init__(self, x, y, vx, vy, friendly, damage=1, gravity=0.0, life=1.0, size=22):
        super().__init__(x, y, size, size * 0.6)
        self.vx = vx
        self.vy = vy
        self.friendly = friendly
        self.damage = damage
        self.gravity = gravity
        self.life = life
        self.anim = 0.0
        self.dead = False

    def update(self, dt, level):
        self.anim += dt
        self.life -= dt
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        tx, ty = int(self.cx // 32), int(self.cy // 32)
        if self.life <= 0 or level.solid_at(tx, ty):
            self.dead = True


class ProjectileManager:
    def __init__(self):
        self.items = []
        self.limit = 12

    def clear(self):
        self.items.clear()

    def spawn_player_bolt(self, player):
        cfg = CONFIG["projectiles"]
        if len([p for p in self.items if p.friendly]) >= 3:
            return None
        x = player.cx + player.facing * 14 - 11
        y = player.cy - 8
        bolt = Projectile(x, y, cfg["player_speed"] * player.facing, 0.0, True,
                          cfg["player_damage"], 0.0, cfg["player_life"])
        self.items.append(bolt)
        return bolt

    def spawn_spore(self, enemy, aim_x, aim_y):
        cfg = CONFIG["projectiles"]
        dx, dy = aim_x - enemy.cx, aim_y - enemy.cy
        dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
        speed = cfg["enemy_speed"]
        spore = Projectile(enemy.cx - 11, enemy.cy - 8, dx / dist * speed, dy / dist * speed - 40,
                           False, 1, cfg["enemy_gravity"], cfg["enemy_life"])
        self.items.append(spore)
        return spore

    def update(self, dt, level):
        for item in self.items:
            item.update(dt, level)
        self.items[:] = [p for p in self.items if not p.dead]
