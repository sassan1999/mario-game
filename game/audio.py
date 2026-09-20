"""Small audio facade.  Missing audio devices/files fail soft on desktop and Android."""
from __future__ import annotations

from pathlib import Path

from config import AUDIO_DIR, MUSIC_TRACKS, SOUND_EFFECTS

try:
    from kivy.core.audio import SoundLoader
except Exception:  # Allows headless simulation tests without Kivy.
    SoundLoader = None


class AudioManager:
    def __init__(self):
        self.sounds = {}
        self.music = None
        self.muted = False
        if SoundLoader:
            for name in SOUND_EFFECTS:
                path = AUDIO_DIR / f"{name}.wav"
                if path.exists():
                    try:
                        self.sounds[name] = SoundLoader.load(str(path))
                    except Exception:
                        pass

    def play(self, name, volume=1.0):
        if self.muted:
            return
        sound = self.sounds.get(name)
        if sound:
            try:
                sound.stop()
                sound.volume = max(0.0, min(1.0, volume))
                sound.play()
            except Exception:
                pass

    def set_muted(self, value):
        self.muted = bool(value)
        if self.muted and self.music:
            try:
                self.music.stop()
            except Exception:
                pass

    def play_music(self, name):
        # Procedural WAV SFX are bundled; music is intentionally absent rather
        # than shipping copyrighted tracks. This hook is ready for original OGGs.
        path = AUDIO_DIR / f"{name}.ogg"
        if not SoundLoader or not path.exists() or self.muted:
            return
        try:
            if self.music:
                self.music.stop()
            self.music = SoundLoader.load(str(path))
            self.music.loop = True
            self.music.play()
        except Exception:
            self.music = None
