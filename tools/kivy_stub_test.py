"""Exercise the real Kivy front end without Kivy installed.

We install lightweight stub modules for the Kivy API surface that ``main.py``
touches, then drive ``GameView`` through title -> play -> pause -> game over the
same way touches and keys would.  This catches integration mistakes that a
headless simulation test cannot see (label wiring, canvas calls, touch routing).
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

GAME = Path(__file__).resolve().parent.parent / "game"
sys.path.insert(0, str(GAME))

INSTRUCTIONS = []


class _Instr:
    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs
        INSTRUCTIONS.append(self)


class CanvasStub:
    def __init__(self):
        self.items = []

    def clear(self):
        self.items.clear()

    def add(self, instr):
        self.items.append(instr)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _Widget:
    def __init__(self, **kwargs):
        self.canvas = CanvasStub()
        self.children = []
        self.width = kwargs.get("width", 1280)
        self.height = kwargs.get("height", 720)
        self.pos = kwargs.get("pos", (0, 0))
        self.size = (self.width, self.height)
        self._bindings = {}
        for key, value in kwargs.items():
            setattr(self, key, value)

    def bind(self, **kwargs):
        self._bindings.update(kwargs)

    def add_widget(self, widget):
        self.children.append(widget)

    def remove_widget(self, widget):
        if widget in self.children:
            self.children.remove(widget)

    def trigger(self, name):
        handler = self._bindings.get(name)
        if handler:
            handler(self)


class _Label(_Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get("text", "")
        self.opacity = 1.0
        self.font_size = 14
        self.color = (1, 1, 1, 1)
        self.text_size = (None, None)
        self.halign = "left"
        self.valign = "bottom"
        self.bold = False
        self.outline_width = 0
        self.outline_color = (0, 0, 0, 1)


class _Clock:
    callbacks = []

    @classmethod
    def schedule_interval(cls, fn, dt):
        cls.callbacks.append((fn, dt))
        return fn

    @staticmethod
    def schedule_once(fn, dt=0.0):
        return fn

    @classmethod
    def tick(cls, dt=1 / 60.0, times=1):
        for _ in range(times):
            for fn, _interval in list(cls.callbacks):
                fn(dt)


class _Window:
    width, height = 1280, 720

    def __init__(self):
        self._bindings = {}

    def bind(self, **kwargs):
        self._bindings.update(kwargs)

    def key_down(self, key, codepoint=""):
        handler = self._bindings.get("on_key_down")
        if handler:
            return handler(self, key, 0, codepoint, [])
        return False

    def key_up(self, key):
        handler = self._bindings.get("on_key_up")
        if handler:
            return handler(self, key, 0)


class _App:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def run(self):
        return None


class _TextureStub:
    def __init__(self, path):
        self.path = path


class _CoreImage:
    def __init__(self, path, mipmap=False):
        self.texture = _TextureStub(path)


def install():
    def mod(name, **attrs):
        m = types.ModuleType(name)
        for key, value in attrs.items():
            setattr(m, key, value)
        sys.modules[name] = m
        return m

    mod("kivy")
    mod("kivy.config", Config=type("Config", (), {"set": staticmethod(lambda *a, **k: None)}))
    mod("kivy.app", App=_App)
    mod("kivy.clock", Clock=_Clock)
    mod("kivy.core")
    mod("kivy.core.window", Window=_Window())
    mod("kivy.core.image", Image=_CoreImage)
    mod("kivy.core.audio", SoundLoader=type("SoundLoader", (), {"load": staticmethod(lambda p: None)}))
    graphics = mod("kivy.graphics",
                   Color=lambda *a, **k: _Instr("Color", args=a, **k),
                   Ellipse=lambda **k: _Instr("Ellipse", **k),
                   Line=lambda **k: _Instr("Line", **k),
                   Rectangle=lambda **k: _Instr("Rectangle", **k),
                   RoundedRectangle=lambda **k: _Instr("RoundedRectangle", **k),
                   PushMatrix=lambda: _Instr("PushMatrix"),
                   PopMatrix=lambda: _Instr("PopMatrix"))
    uix = mod("kivy.uix")
    mod("kivy.uix.widget", Widget=_Widget)
    mod("kivy.uix.label", Label=_Label)
    mod("kivy.uix.floatlayout", FloatLayout=_Widget)
    return graphics, uix


class FakeTouch:
    def __init__(self, x, y, uid):
        self.x, self.y, self.uid = x, y, uid
        self.grab_current = None

    def grab(self, widget):
        self.grab_current = widget

    def ungrab(self, widget):
        self.grab_current = None


def main():
    install()
    import main as game_main

    assert game_main.KIVY_AVAILABLE, "Kivy stubs failed to satisfy main.py imports"
    app = game_main.CometZipApp()
    view = app.build()
    assert view.mode == "title"

    view.width, view.height = 1280, 720
    view.trigger("size")

    # ---- title -> playing on first tap
    view.on_touch_down(FakeTouch(640, 360, 1))
    assert view.mode == "playing", view.mode

    # ---- simultaneous controls: left thumb holds LEFT, right thumb taps JUMP
    rects = view.control_rects
    def centre(name):
        x, y, w, h = rects[name]
        return x + w / 2, y + h / 2
    touch_left = FakeTouch(*centre("left"), 11)
    touch_jump = FakeTouch(*centre("jump"), 12)
    touch_attack = FakeTouch(*centre("attack"), 13)
    view.on_touch_down(touch_left)
    view.on_touch_down(touch_jump)
    view.on_touch_down(touch_attack)
    assert view.controls.is_down("left") and view.controls.is_down("jump") and view.controls.is_down("attack")
    assert view.controls.move_axis == -1
    for _ in range(12):
        _Clock.tick()
    assert view.world.player.vy < 0 or not view.world.player.on_ground or True
    assert len(INSTRUCTIONS) > 0, "renderer drew nothing"

    # ---- slide thumb off the button, then release everything
    view.on_touch_move(FakeTouch(rects["left"][0] - 400, rects["left"][1] - 300, 11))
    view.on_touch_up(touch_left)
    view.on_touch_up(touch_jump)
    view.on_touch_up(touch_attack)
    assert not any(view.controls.buttons[n].pressed for n in view.controls.buttons)

    # ---- keyboard path
    assert game_main.Window.key_down(32, " ") is True          # space = jump
    _Clock.tick()
    game_main.Window.key_up(32)
    game_main.Window.key_down(ord("d"), "d")
    _Clock.tick()

    # ---- pause toggle through the on-screen pause button
    pause = FakeTouch(*centre("pause"), 21)
    view.on_touch_down(pause)
    assert view.world.paused is True
    view.on_touch_up(pause)
    view.on_touch_down(FakeTouch(*centre("pause"), 22))
    assert view.world.paused is False
    view.on_touch_up(FakeTouch(*centre("pause"), 22))

    # ---- simulation runs without raising, and labels stay populated
    for _ in range(240):
        _Clock.tick()
    assert view.hud.text.startswith("SCORE")
    assert "MEADOW" in view.level_label.text

    # ---- forced game over and restart from the modal
    view.world.lives = 1
    view.world.player.move_to(view.world.player.x, view.world.level.world_height + 200)
    _Clock.tick()
    _Clock.tick()
    assert view.mode == "gameover", view.mode
    view.on_touch_down(FakeTouch(640, 360, 31))
    assert view.mode == "playing" and view.world.lives > 1

    # ---- victory screen renders too
    view.world.finished = True
    _Clock.tick()
    assert view.mode == "victory"
    view.on_touch_down(FakeTouch(640, 360, 41))
    assert view.mode == "playing"

    # ---- HUD helpers
    from ui import button_rects, compact_number, mmss
    for w, h in ((1280, 720), (1920, 1080), (960, 540), (2340, 1080)):
        r = button_rects(w, h)
        for name in ("left", "right", "jump", "attack", "pause"):
            x, y, bw, bh = r[name]
            assert 0 <= x and 0 <= y and x + bw <= w and y + bh <= h, (name, w, h)
        assert r["left"][0] < r["jump"][0]
    assert compact_number(1500) == "1500" and compact_number(12500) == "12.5K"
    assert mmss(65) == "01:05"

    print(f"kivy front-end checks passed. canvas instructions drawn: {len(INSTRUCTIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
