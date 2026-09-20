"""LEVEL 1 - CLOUDWIND MEADOW.

Teaching level: coin trail, a step, a breakable/bonus pair, one moving
platform, two enemy types, spikes, a checkpoint and the Aurora Gate goal.
"""
from .base import LevelBuilder

GROUND = 13
W, H = 104, 17


def build():
    b = LevelBuilder("01 / CLOUDWIND MEADOW", "Learn the wind, then outrun it.",
                     width=W, height=H, time_limit=180, theme="meadow",
                     start=(3, GROUND - 1), goal_hint="Reach the Aurora Gate")

    # ------------------------------------------------------------- terrain
    b.ground(0, 22, row=GROUND)
    b.ground(26, 44, row=GROUND)
    b.ground(48, 70, row=GROUND)
    b.ground(74, 103, row=GROUND)

    # opening: a one-tile step, coin arc and an easy ground patroller
    b.block(9, GROUND - 1, 2, 1, "#", walkable_top=True)
    b.coin_arc(12, GROUND - 1, 4)
    b.enemy("grubbo", 18, GROUND - 1)

    # floating one-way platform across the first pit
    b.platform(23, 11, 3)
    b.coin(23, 9, 3, 1)

    # breakable + bonus teaching pair (bump from below)
    b.block(30, 10, 1, 1, "B")
    b.bonus(31, 10, "?")
    b.block(32, 10, 1, 1, "B")
    b.coin(30, 9, 3, 1)
    b.block(34, GROUND - 1, 4, 1, "#", walkable_top=True)
    b.enemy("grubbo", 40, GROUND - 1)

    # horizontal moving platform over the second pit
    b.mover(45, 10, axis="x", distance=96, speed=62)
    b.coin(46, 8, 3, 1)

    # a swooping bat and the first checkpoint
    b.enemy("zippbat", 51, 8)
    b.checkpoint(54, GROUND - 1)
    b.block(57, GROUND - 1, 4, 1, "#", walkable_top=True)
    b.coin(57, 11, 4, 1)
    b.enemy("grubbo", 63, GROUND - 1)
    b.hazard(67, GROUND - 1, 2, "^")

    # mushroom reward plus a bouncing enemy before the goal run
    b.block(71, GROUND - 1, 3, 1, "#", walkable_top=True)
    b.bonus(75, 10, "?")
    b.coin_arc(79, GROUND - 1, 5)
    b.enemy("bouncer", 82, GROUND - 1)
    b.block(87, 10, 4, 1, "#", walkable_top=True)
    b.coin(88, 8, 3, 1)
    b.block(95, 8, 5, 1, "#", walkable_top=True)
    b.goal(99, GROUND - 1)

    b.hazard(72, GROUND - 1, 2, "^")
    b.validate()
    return b


_builder = build()
LEVEL = _builder.build()
