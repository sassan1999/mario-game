"""Original mushroom-like power-up: the TWILIGHT SHROOM."""


class Mushroom:
    SIZE = 34

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.w = 30.0
        self.h = 30.0
        self.vx = 90.0
        self.vy = 0.0
        self.anim = 0.0
        self.dead = False
        self.spawn_timer = 0.55
        self.emerging = True

    @property
    def cx(self):
        return self.x + self.w * 0.5

    @property
    def cy(self):
        return self.y + self.h * 0.5

    def update(self, dt, level):
        self.anim += dt
        if self.emerging:
            self.spawn_timer -= dt
            self.y -= 34 * dt
            if self.spawn_timer <= 0:
                self.emerging = False
            return
        from physics import Body, apply_gravity, move_and_collide
        ghost = Body(self.x, self.y, self.w, self.h)
        ghost.vx = self.vx
        ghost.vy = self.vy
        apply_gravity(ghost, dt, 1600.0, 900.0)
        move_and_collide(ghost, dt, level, 12.0)
        self.x, self.y, self.vy = ghost.x, ghost.y, ghost.vy
        if ghost.wall_hit:
            self.vx = -self.vx
            ghost.wall_hit = 0
            ghost.vx = self.vx
            # nudge away from the wall we just hit
            self.x += self.vx * dt
        if not self._has_ground_below(level):
            self.vy = max(self.vy, 60.0)

    def _has_ground_below(self, level):
        tx0 = int(self.x // 32)
        tx1 = int((self.x + self.w - 1) // 32)
        ty = int((self.y + self.h + 3) // 32)
        return any(level.solid_at(tx, ty) or level.tile(tx, ty) == "=" for tx in range(tx0, tx1 + 1))


class MushroomManager:
    def __init__(self):
        self.items = []

    def clear(self):
        self.items.clear()

    def spawn(self, x, y):
        self.items.append(Mushroom(x, y))

    def update(self, dt, level):
        for item in self.items:
            item.update(dt, level)
