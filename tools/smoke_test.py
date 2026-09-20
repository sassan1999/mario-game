"""Head-less playability check for COMET ZIP (no Kivy required).

Drives the simulation with a simple bot: hold right, jump when a wall, gap or
enemy is ahead, shoot at armoured enemies, and report per-level telemetry.
"""
from __future__ import annotations

import sys
from pathlib import Path

GAME = Path(__file__).resolve().parent.parent / "game"
sys.path.insert(0, str(GAME))

from config import CONFIG, TILE            # noqa: E402
from controls import ControlState          # noqa: E402
from game_world import GameWorld           # noqa: E402


class BotControls(ControlState):
    """ControlState driven the way a thumb would: hold a direction, tap jump."""

    def __init__(self, world):
        super().__init__()
        self.world = world
        self.frame = 0
        self.stuck_frames = 0
        self.last_x = 0.0
        self.hold_jump = 0

    def decide(self):
        self.clear()
        world = self.world
        p = world.player
        level = world.level
        self.frame += 1

        if abs(p.x - self.last_x) < 1.0:
            self.stuck_frames += 1
        else:
            self.stuck_frames = 0
        self.last_x = p.x

        self.keyboard["right"] = True

        head = int((p.y + 6) // TILE)
        chest = int((p.cy + 8) // TILE)
        near = int((p.right + 12) // TILE)
        wall_ahead = any(level.solid_at(near, ty) for ty in (head, chest))
        foot = int((p.bottom + 5) // TILE)
        gap_ahead = not any(level.solid_at(tx, foot) or level.solid_at(tx, foot + 1)
                            for tx in (near, near + 1))
        hazard = any(level.tile(tx, ty) in ("^", "~")
                     for tx in range(near, near + 3) for ty in range(head, foot + 1))
        enemy_ahead = any(e.alive and e.stompable and -4 < e.cx - p.cx < 104 and abs(e.cy - p.cy) < 80
                          for e in world.enemies)

        if self.hold_jump:
            self.hold_jump -= 1
            self.keyboard["jump"] = True
        elif p.on_ground and (wall_ahead or gap_ahead or hazard or enemy_ahead or self.stuck_frames > 20):
            self.jump_queued = True
            self.keyboard["jump"] = True
            self.hold_jump = 12
            self.stuck_frames = 0

        rammer_near = any(e.kind == "rammer" and e.alive and abs(e.cx - p.cx) < 420 for e in world.enemies)
        spitter_near = any(e.kind == "spitter" and e.alive and abs(e.cx - p.cx) < 360 for e in world.enemies)
        if (rammer_near or spitter_near) and self.frame % 14 == 0:
            self.attack_queued = True


def run(level_index, max_seconds=140.0):
    world = GameWorld()
    world.load_level(level_index, fresh=True)
    bot = BotControls(world)
    dt = 1 / 60.0
    frames = int(max_seconds / dt)
    peak_x = 0.0
    for i in range(frames):
        bot.decide()
        world.update(dt, bot, None)
        peak_x = max(peak_x, world.player.cx)
        if world.game_over or world.finished or world.level_index != level_index:
            break
    return world, i * dt, peak_x


def main():
    world = GameWorld()
    levels = len(__import__("levels").LEVELS)
    failures = []
    for index in range(levels):
        result, seconds, peak = run(index)
        advanced = result.level_index != index or result.finished
        if advanced and result.level_index == index:
            pass
        print(f"L{index + 1} {result.level.name[:22]:24s} "
              f"time={seconds:6.1f}s peak_x={peak:7.1f}/{result.level.world_width:6.1f} "
              f"advanced={advanced} coins={result.coins_count} lives={result.lives} "
              f"score={result.score} enemies_left={len(result.enemies)}")
        if not advanced and not result.game_over:
            failures.append(index + 1)
    # targeted rule checks
    checks = {}
    w = GameWorld(); w.load_level(0, fresh=True)
    w.player.move_to(w.player.x, w.level.world_height + 200)
    w.update(1/60, ControlState(), None)
    checks["pit_costs_a_life"] = w.lives == CONFIG["player"]["lives"] - 1
    w = GameWorld(); w.load_level(0, fresh=True)
    w.player.power_up()
    checks["mushroom_grows_player"] = (w.player.w, w.player.h) == (CONFIG["player"]["big_width"], CONFIG["player"]["big_height"])
    w.player.take_damage(0)
    checks["powerup_absorbs_a_hit"] = (not w.player.powered) and w.lives == CONFIG["player"]["lives"]
    w = GameWorld(); w.load_level(0, fresh=True)
    enemy = w.enemies[0]
    w.player.move_to(enemy.cx - w.player.w / 2, enemy.y - w.player.h - 2); w.player.vy = 300
    w.update(1/60, ControlState(), None)
    checks["stomp_defeats_enemy"] = (not enemy.alive) and w.player.vy < 0
    w = GameWorld(); w.load_level(0, fresh=True)
    checks["bonus_blocks_exist"] = any(c in "?%Bb" for row in w.level.tiles for c in row)
    w = GameWorld(); w.load_level(0, fresh=True)
    spotted = None
    for tx in range(w.level.width):
        for ty in range(w.level.height):
            if w.level.tile(tx, ty) in "?%":
                spotted = (tx, ty); break
        if spotted: break
    broke = False
    if spotted:
        tx, ty = spotted
        w.level.set_tile(tx, ty, "B")
        w.player.move_to(tx * TILE + 2, (ty + 1) * TILE + 2); w.player.vy = -400
        w.update(1/60, ControlState(), None)
        broke = w.level.tile(tx, ty) == "."
    checks["head_bump_breaks_block"] = broke
    print("\nrule checks:", checks)
    ok = all(checks.values()) and not failures
    print("RESULT:", "PASS" if ok else f"FAIL {checks} {failures}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
