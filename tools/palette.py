"""Original colour palettes for COMET ZIP art (no third-party assets used)."""

def hx(code):
    code = code.lstrip('#')
    return tuple(int(code[i:i + 2], 16) for i in (0, 2, 4))

PLAYER = {
    "outline": hx("0B1E46"),
    "fur_hi": hx("8FD8FF"),
    "fur": hx("2E9BFF"),
    "fur_mid": hx("1C6FE0"),
    "fur_dark": hx("12407F"),
    "belly": hx("E8F6FF"),
    "shoe_hi": hx("FFE9A8"),
    "shoe": hx("FFC13B"),
    "shoe_low": hx("C9860F"),
    "eye_white": hx("FFFFFF"),
    "eye": hx("16331F"),
    "muzzle": hx("D8EFFF"),
    "nose": hx("20405F"),
    "glow": hx("7BF3FF"),
}

COIN = {
    "outline": hx("5A3200"),
    "gold": hx("FFD23F"),
    "gold_hi": hx("FFF3B0"),
    "gold_low": hx("D98A0B"),
    "star": hx("FFFDF0"),
}

MUSHROOM = {
    "outline": hx("3A1230"),
    "cap_hi": hx("FF9DE0"),
    "cap": hx("F0409B"),
    "cap_low": hx("A5185F"),
    "spot": hx("FFF3FA"),
    "stem": hx("FFF0D6"),
    "stem_low": hx("E0BE97"),
    "power": hx("6CF6E0"),
}

ENEMIES = {
    "grubbo": {"outline": hx("2A1508"), "body": hx("C97A3C"), "hi": hx("F0B27A"),
               "dark": hx("8A4B1E"), "eye": hx("FFFFFF"), "pupil": hx("20120A"), "belly": hx("F6E3C2")},
    "zippbat": {"outline": hx("1B1030"), "body": hx("8E5BD8"), "hi": hx("C9A6FF"),
                "dark": hx("5A2FA8"), "eye": hx("FFE45E"), "pupil": hx("241033"), "wing": hx("6E3FC0")},
    "bouncer": {"outline": hx("0C2C1A"), "body": hx("4CD98A"), "hi": hx("B4F5D0"),
                "dark": hx("1E9257"), "eye": hx("FFFFFF"), "pupil": hx("0C2C1A")},
    "spitter": {"outline": hx("2E1020"), "body": hx("E0574F"), "hi": hx("FFA08F"),
                "dark": hx("9A2B26"), "eye": hx("FFF1B8"), "pupil": hx("2A0E18"), "spore": hx("B9F36C")},
    "rammer": {"outline": hx("1A1A24"), "body": hx("5A6570"), "hi": hx("A7B2BD"),
               "dark": hx("333B45"), "eye": hx("FF6B4A"), "pupil": hx("2A0E18"), "horn": hx("EDEFF2")},
}

TILES = {
    "grass": {"outline": hx("10321B"), "top": hx("5FDA7E"), "top_hi": hx("A6F5B8"),
              "body": hx("8A5A2E"), "body_dark": hx("5E3B1C"), "pebble": hx("B07C45")},
    "dirt": {"outline": hx("2C1A0B"), "body": hx("7A4F27"), "body_dark": hx("523213"),
             "pebble": hx("A8703A"), "top": hx("8F5C2C"), "top_hi": hx("B07C45")},
    "stone": {"outline": hx("1C2130"), "body": hx("68738C"), "body_dark": hx("414B60"),
              "pebble": hx("9AA6BE"), "top": hx("7C879F"), "top_hi": hx("AEBBd1".upper())},
    "crystal": {"outline": hx("0E2340"), "body": hx("3FA9F5"), "body_dark": hx("1F6FB8"),
                "pebble": hx("9BE3FF"), "top": hx("7FD8FF"), "top_hi": hx("DBF6FF")},
    "ice": {"outline": hx("19506B"), "body": hx("BEEBFF"), "body_dark": hx("8CCFEF"),
            "pebble": hx("FFFFFF"), "top": hx("E4F8FF"), "top_hi": hx("FFFFFF")},
    "breakable": {"outline": hx("3A2A12"), "body": hx("E0B15C"), "body_dark": hx("B07C2A"),
                  "pebble": hx("F6DC9E"), "top": hx("EFC97C"), "top_hi": hx("FFF0C4")},
    "bonus": {"outline": hx("4A2A00"), "body": hx("FFC53D"), "body_dark": hx("D1880C"),
              "pebble": hx("FFF0B8"), "top": hx("FFDE7A"), "top_hi": hx("FFFBE4")},
    "used": {"outline": hx("2E2438"), "body": hx("9A8FA8"), "body_dark": hx("6B6278"),
             "pebble": hx("BEB4C8"), "top": hx("A79CB4"), "top_hi": hx("CFC6DA")},
    "platform": {"outline": hx("3A2611"), "body": hx("C98B4A"), "body_dark": hx("96602A"),
                 "pebble": hx("F0C48C"), "top": hx("E5A863"), "top_hi": hx("FFE0B0")},
    "spikes": {"outline": hx("2B2F3A"), "body": hx("CBD3E0"), "body_dark": hx("8892A6"),
               "pebble": hx("F2F5FA"), "top": hx("E8EDF5"), "top_hi": hx("FFFFFF")},
    "goo": {"outline": hx("1E0A30"), "body": hx("9B4DE0"), "body_dark": hx("6A22AE"),
            "pebble": hx("D6A6FF"), "top": hx("C57CFF"), "top_hi": hx("F0DEFF")},
}

UI = {
    "outline": hx("0A1730"),
    "panel": hx("14273F"),
    "panel_hi": hx("24456B"),
    "panel_low": hx("0B1A2E"),
    "accent": hx("43D0FF"),
    "accent_dark": hx("157BAD"),
    "text": hx("F2FAFF"),
    "gold": hx("FFD23F"),
    "danger": hx("FF5A5A"),
    "green": hx("5CE08A"),
}

THEMES = {
    "meadow": {"sky_top": hx("7ECBF5"), "sky_low": hx("DFF4FF"), "far": hx("8BC7E8"),
               "near": hx("5FB07A"), "near_hi": hx("86D69B"), "cloud": hx("FFFFFF"),
               "sun": hx("FFF3C4")},
    "cave": {"sky_top": hx("1B1038"), "sky_low": hx("3A2263"), "far": hx("4A2E7A"),
             "near": hx("2C1B4E"), "near_hi": hx("6A46A8"), "cloud": hx("7B5FB8"),
             "sun": hx("A9E9FF")},
    "city": {"sky_top": hx("20124A"), "sky_low": hx("6E2A78"), "far": hx("39235E"),
             "near": hx("1B1436"), "near_hi": hx("5B3E8C"), "cloud": hx("C77BD8"),
             "sun": hx("FFD37A")},
}
