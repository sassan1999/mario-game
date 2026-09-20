# COMET ZIP

A complete original 2D Android platformer built with Python + Kivy.

## Features

- Original blue anthropomorphic speedster: Comet
- Three levels: Cloudwind Meadow, Crystal Caves, Neon Skyline
- Coins/tokens, score, lives, timer, checkpoints and game-over flow
- Five original enemy types with distinct AI: Grubbo, ZippBat, Bouncer, Spitter and Rammer
- Breakable blocks, bonus blocks, Twilight Shroom power-up, hazards, pits and moving platforms
- Player energy projectiles and enemy spores
- Gravity, acceleration, friction, coyote-time jumping, buffered jumping, collision resolution and camera smoothing
- Fixed landscape touch controls with independent multitouch pointer tracking
- Original procedural PNG and WAV assets; no copyrighted game assets or music
- Headless simulation test that runs without Kivy

## Project structure

```text
comet-zip/
├── buildozer.spec
├── README.md
├── game/
│   ├── main.py
│   ├── config.py
│   ├── game_world.py
│   ├── player.py
│   ├── enemies.py
│   ├── physics.py
│   ├── collision.py
│   ├── controls.py
│   ├── camera.py
│   ├── powerups.py
│   ├── projectiles.py
│   ├── particles.py
│   ├── audio.py
│   ├── ui.py
│   ├── entities.py
│   ├── levels/
│   ├── assets/images/
│   ├── assets/audio/
│   └── data/game_config.json
└── tools/
    ├── build_assets.py
    ├── build_player.py
    └── smoke_test.py
```

## Run on desktop

Install Kivy 2.3+ in a Python environment, then:

```bash
python game/main.py
```

The source tree also works for headless checks without Kivy:

```bash
python tools/smoke_test.py
```

## Build an APK

Use Linux, macOS, or WSL2 with Buildozer and Android build dependencies installed:

```bash
python -m pip install buildozer
buildozer android debug
```

The APK is written to `bin/`. For a release build, configure signing credentials and run:

```bash
buildozer android release
```

The app is configured for landscape orientation and supports Android API 23+ on ARMv7 and ARM64.
