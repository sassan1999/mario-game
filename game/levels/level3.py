"""LEVEL 3 - NEON SKYLINE.

Hardest zone: armoured rammers that must be shot, spitters firing across
drops, fast movers, spike corridors, a late checkpoint and the Star Beacon.
"""
from .base import LevelBuilder

GROUND = 13
W, H = 112, 17


def build():
    b = LevelBuilder("03 / NEON SKYLINE", "No brakes above the city lights.",
                     width=W, height=H, time_limit=225, theme="city",
                     start=(3, GROUND - 1), goal_hint="Cross the city and touch the Star Beacon")

    b.ground(0, 16, row=GROUND)
    b.ground(21, 34, row=GROUND)
    b.ground(39, 55, row=GROUND)
    b.ground(60, 78, row=GROUND)
    b.ground(83, 97, row=GROUND)
    b.ground(102, 111, row=GROUND)

    # opening: coin run-up then the first armoured rammer
    b.coin(6, GROUND - 2, 3, 1)
    b.enemy("rammer", 13, GROUND - 1)
    b.block(17, 11, 3, 1, "=")

    # fast horizontal mover over a spike pit
    b.mover(17, 9, axis="x", distance=130, speed=88)
    b.coin(22, 7, 3, 1)
    b.enemy("zippbat", 26, 7)

    # breakable/bonus pair, then a spitter battery over goo
    b.block(28, 10, 1, 1, "B")
    b.bonus(29, 10, "?")
    b.coin(30, 8, 3, 1)
    b.block(31, 10, 3, 1, "#", walkable_top=True)
    b.enemy("spitter", 32, 9)
    b.hazard(35, GROUND - 1, 4, "~")

    # vertical climb with a rammer guarding a ledge
    b.mover(38, 10, axis="y", distance=92, speed=74)
    b.block(41, 9, 3, 1, "#", walkable_top=True)
    b.enemy("rammer", 44, 8)
    b.coin(41, 7, 3, 1)
    b.enemy("grubbo", 49, GROUND - 1)
    b.checkpoint(52, GROUND - 1)

    # spike corridor with short hops
    b.hazard(56, GROUND - 1, 3, "^")
    b.block(60, 10, 2, 1, "#", walkable_top=True)
    b.bonus(62, 10, "?")
    b.enemy("bouncer", 66, GROUND - 1)
    b.coin_arc(63, 10, 5)
    b.enemy("zippbat", 71, 6)

    # long goo drop with a fast mover and a downward spitter
    b.hazard(79, GROUND - 1, 4, "~")
    b.mover(79, 10, axis="x", distance=120, speed=92)
    b.block(86, 10, 3, 1, "#", walkable_top=True)
    b.enemy("spitter", 87, 9)
    b.coin(86, 8, 3, 1)

    # finale: spike strip, mover, rammer and the Star Beacon
    b.hazard(98, GROUND - 1, 3, "^")
    b.mover(98, 9, axis="x", distance=104, speed=96)
    b.block(103, 10, 3, 1, "#", walkable_top=True)
    b.coin(103, 8, 3, 1)
    b.enemy("rammer", 106, GROUND - 1)
    b.block(108, 8, 3, 1, "#", walkable_top=True)
    b.goal(109, GROUND - 1)

    b.validate()
    return b


_builder = build()
LEVEL = _builder.build()
