"""Presentation helpers and fixed-screen HUD for COMET ZIP.

The game world is in world pixels; this module keeps all Android controls and
HUD elements in viewport coordinates, so the camera never drags them around.
"""
from __future__ import annotations

from pathlib import Path

from config import CONFIG, GAME_TITLE, GAME_SUBTITLE, TILE, image_path


class TextureBank:
    """Lazy texture loader.  Keeping one texture per frame avoids per-frame IO."""
    def __init__(self):
        self._textures = {}
        self._available = True
        try:
            from kivy.core.image import Image as CoreImage
            self.CoreImage = CoreImage
        except Exception:
            self._available = False
            self.CoreImage = None

    def get(self, relative: str):
        if relative in self._textures:
            return self._textures[relative]
        if not self._available:
            return None
        path = image_path(*relative.split("/"))
        try:
            texture = self.CoreImage(str(path), mipmap=True).texture
            self._textures[relative] = texture
            return texture
        except Exception:
            self._textures[relative] = None
            return None

    def frames(self, folder: str, stem: str, count: int):
        return [self.get(f"{folder}/{stem}_{i}.png") for i in range(count)]


def rgba(rgb, alpha=1.0):
    return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0, alpha)


def compact_number(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 10_000:
        return f"{value / 1_000:.1f}K"
    return str(int(value))


def mmss(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def button_rects(width: float, height: float) -> dict[str, tuple[float, float, float, float]]:
    """Thumb-friendly landscape layout, in fixed viewport coordinates."""
    scale = max(0.72, min(1.35, min(width / 1280.0, height / 720.0)))
    bw, bh = 122 * scale, 82 * scale
    gap = 18 * scale
    margin = 28 * scale
    bottom = 26 * scale
    return {
        "left": (margin, bottom, bw, bh),
        "right": (margin + bw + gap, bottom, bw, bh),
        "jump": (width - margin - bw * 2 - gap, bottom, bw, bh),
        "attack": (width - margin - bw, bottom, bw, bh),
        "pause": (width - margin - 54 * scale, height - margin - 54 * scale, 54 * scale, 54 * scale),
    }


def contains(rect, x, y):
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh


class HudText:
    """Kivy Label setup kept in one place so typography remains consistent."""
    @staticmethod
    def style(label, size, color=(1, 1, 1, 1), bold=False):
        label.font_size = size
        label.color = color
        label.bold = bold
        label.halign = "center"
        label.valign = "middle"
        label.text_size = (None, None)
        label.outline_width = 1
        label.outline_color = (0.02, 0.06, 0.13, 0.9)
        return label
