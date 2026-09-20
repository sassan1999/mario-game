"""Central configuration for **COMET ZIP** (original blue speedster platformer).

All gameplay tunables live here or are overridden by ``data/game_config.json``
so the game can be balanced without touching module logic.  This module has no
Kivy imports on purpose: it is safe to import from head-less tests / asset
builders.
"""
from __future__ import annotations

import json
from pathlib import Path

# --------------------------------------------------------------------------
# paths
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
AUDIO_DIR = ASSETS_DIR / "audio"
DATA_DIR = BASE_DIR / "data"
CONFIG_PATH = DATA_DIR / "game_config.json"

GAME_TITLE = "COMET ZIP"
GAME_SUBTITLE = "Blue Comet of the Skyline Isles"
GAME_VERSION = "1.0.0"

# --------------------------------------------------------------------------
# rendering / world metrics
# --------------------------------------------------------------------------
TILE = 32                       # world pixels per tile
DESIGN_WIDTH = 1280.0           # reference viewport (16:9, landscape)
DESIGN_HEIGHT = 720.0

# --------------------------------------------------------------------------
# tile alphabet
# --------------------------------------------------------------------------
EMPTY = "."
SOLID_TILES = frozenset("#GSYIBb?%X")     # full collision
ONEWAY_TILES = frozenset("=")             # collide from above only
HAZARD_TILES = frozenset("^~")            # damage on overlap
ICE_TILES = frozenset("I")                # slippery solid
TILE_MATERIAL = {
    "G": "grass", "#": "dirt", "S": "stone", "Y": "crystal", "I": "ice",
    "B": "breakable", "b": "breakable", "?": "bonus", "%": "bonus",
    "X": "used", "=": "platform", "^": "spikes", "~": "goo",
}

# entity markers inside a level map (removed from the tile grid after parsing)
ENTITY_CHARS = {
    "P": "player_start",
    "o": "coin",
    "1": "grubbo",
    "2": "zippbat",
    "3": "bouncer",
    "4": "spitter",
    "5": "rammer",
    "M": "mushroom",
    "K": "checkpoint",
    "E": "goal",
    "H": "mover_h",
    "V": "mover_v",
}

# --------------------------------------------------------------------------
# default gameplay values (see data/game_config.json for the live copy)
# --------------------------------------------------------------------------
DEFAULTS = {
    "physics": {
        "gravity": 2200.0,
        "max_fall_speed": 1250.0,
        "player_run_speed": 320.0,
        "player_sprint_bonus": 1.0,
        "player_accel": 1550.0,
        "player_air_accel": 900.0,
        "ground_friction": 1900.0,
        "air_friction": 380.0,
        "ice_friction": 260.0,
        "jump_velocity": 760.0,
        "jump_cut_multiplier": 0.42,
        "coyote_time": 0.10,
        "jump_buffer_time": 0.12,
        "max_step_px": 14.0,
        "stomp_bounce": 560.0,
        "moving_platform_speed": 70.0,
    },
    "player": {
        "width": 28.0,
        "height": 42.0,
        "big_width": 36.0,
        "big_height": 54.0,
        "lives": 3,
        "invuln_time": 1.8,
        "attack_cooldown": 0.30,
        "respawn_delay": 0.85,
    },
    "projectiles": {
        "player_speed": 700.0,
        "player_life": 0.95,
        "player_damage": 1,
        "enemy_speed": 260.0,
        "enemy_life": 2.4,
        "enemy_gravity": 330.0,
    },
    "scoring": {
        "coin": 100,
        "coin_block": 150,
        "enemy": 200,
        "combo_bonus": 50,
        "level_clear": 1000,
        "time_bonus_per_second": 10,
        "time_bonus_cap": 3000,
    },
    "camera": {
        "lerp": 6.5,
        "look_ahead": 130.0,
        "look_ahead_lerp": 3.0,
        "dead_zone_x": 40.0,
        "vertical_lerp": 4.0,
        "max_vertical_offset": 190.0,
        "shake_decay": 5.0,
    },
    "difficulty": {
        "1": {"enemy_speed": 0.85, "enemy_hp_bonus": 0, "hazard_scale": 1.0, "time_bonus": 1.0},
        "2": {"enemy_speed": 1.00, "enemy_hp_bonus": 0, "hazard_scale": 1.15, "time_bonus": 1.0},
        "3": {"enemy_speed": 1.15, "enemy_hp_bonus": 1, "hazard_scale": 1.3, "time_bonus": 1.0},
    },
}

# --------------------------------------------------------------------------
# animation frame counts (shared by the asset builder and the renderer)
# --------------------------------------------------------------------------
ANIMATIONS = {
    "player": {
        "idle": 4, "run": 8, "jump": 2, "fall": 2, "hurt": 2, "shoot": 2, "skid": 2,
    },
    "grubbo": {"walk": 4, "squash": 1},
    "zippbat": {"fly": 4, "squash": 1},
    "bouncer": {"idle": 2, "hop": 2, "squash": 1},
    "spitter": {"idle": 4, "fire": 2, "squash": 1},
    "rammer": {"run": 4, "squash": 1},
    "coin": {"spin": 6},
    "mushroom": {"idle": 4},
    "bolt": {"fly": 2},
    "spore": {"fly": 2},
    "checkpoint": {"off": 1, "on": 2},
    "goal": {"idle": 4},
    "tiles": {"grass": 1, "dirt": 1, "stone": 1, "crystal": 1, "ice": 1,
              "breakable": 1, "bonus": 4, "used": 1, "platform": 1,
              "spikes": 1, "goo": 4},
    "ui": {"arrow_left": 2, "arrow_right": 2, "jump": 2, "attack": 2,
           "pause": 2, "coin_icon": 1, "heart": 2, "shroom_icon": 1},
    "backgrounds": {"sky": 1, "hills_far": 1, "hills_near": 1, "clouds": 1, "cave": 1, "city": 1},
}

SOUND_EFFECTS = ("jump", "coin", "stomp", "shoot", "hurt", "powerup", "block_break",
                 "block_bonus", "checkpoint", "goal", "game_over", "select", "land", "dash")
MUSIC_TRACKS = ("title", "level1", "level2", "level3", "victory")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(path: str | Path | None = None) -> dict:
    """Return the merged configuration dictionary."""
    cfg = _deep_merge(DEFAULTS, {})
    target = Path(path) if path is not None else CONFIG_PATH
    try:
        with open(target, "r", encoding="utf-8") as handle:
            cfg = _deep_merge(cfg, json.load(handle))
    except (OSError, ValueError):
        cfg = _deep_merge(cfg, {})
    return cfg


def save_config(cfg: dict, path: str | Path | None = None) -> None:
    target = Path(path) if path is not None else CONFIG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(cfg, handle, indent=2, sort_keys=True)


def image_path(*parts: str) -> Path:
    return IMAGES_DIR.joinpath(*parts)


def audio_path(*parts: str) -> Path:
    return AUDIO_DIR.joinpath(*parts)


CONFIG = load_config()
