"""LEVEL 2 - CRYSTAL CAVES.

Ice friction strips, a vertical mover over goo, spitter ledges, a breakable
cluster hiding a mushroom and a second checkpoint.
"""
from .base import LevelBuilder

GROUND = 13
W, H = 108, 17


def build():
    b = LevelBuilder("02 / CRYSTAL CAVES", "The cave echoes answer back.",
                     width=W, height=H, time_limit=200, theme="cave",
                     start=(3, GROUND - 1), goal_hint="Find the deep-cave Aurora Gate")

    b.ground(0, 18, row=GROUND)
    b.ground(23, 38, row=GROUND)
    b.ground(43, 60, row=GROUND)
    b.ground(65, 84, row=GROUND)
    b.ground(89, 107, row=GROUND)

    # crystal pillar and a raised coin ledge
    b.block(10, 10, 2, 3, "Y", walkable_top=True)
    b.coin(10, 8, 2, 1)
    b.enemy("zippbat", 15, 7)
    b.coin_arc(19, GROUND - 1, 4)

    # ice strip: low friction encourages careful stops
    b.fill(27, GROUND - 1, 33, GROUND - 1, "I")
    b.coin(27, GROUND - 2, 4, 1)
    b.bonus(31, 10, "?")
    b.enemy("grubbo", 36, GROUND - 1)

    # goo pit crossed by a vertical mover
    b.hazard(39, GROUND - 1, 4, "~")
    b.mover(40, 10, axis="y", distance=70, speed=58)
    b.coin(41, 7, 2, 1)

    # spitter ledge and the checkpoint
    b.block(45, 10, 5, 1, "#", walkable_top=True)
    b.enemy("spitter", 47, 9)
    b.coin(45, 8, 5, 1)
    b.checkpoint(53, GROUND - 1)
    b.enemy("grubbo", 57, GROUND - 1)

    # breakable cluster hiding the mushroom
    b.block(61, 11, 1, 1, "B")
    b.bonus(62, 11, "?")
    b.block(63, 11, 1, 1, "B")
    b.block(64, 9, 3, 1, "#", walkable_top=True)
    b.coin(64, 7, 3, 1)

    # spike strip and a short vertical climb
    b.hazard(66, GROUND - 1, 3, "^")
    b.block(70, 11, 2, 2, "#", walkable_top=True)
    b.enemy("zippbat", 76, 6)
    b.coin_arc(72, 8, 5)

    # second goo crossing with a horizontal mover
    b.hazard(85, GROUND - 1, 4, "~")
    b.mover(84, 9, axis="x", distance=110, speed=70)
    b.coin(86, 7, 2, 1)
    b.enemy("bouncer", 93, GROUND - 1)
    b.block(96, 10, 4, 1, "#", walkable_top=True)
    b.coin(97, 8, 3, 1)
    b.bonus(101, 10, "?")
    b.goal(104, GROUND - 1)

    b.validate()
    return b


_builder = build()
LEVEL = _builder.build()
