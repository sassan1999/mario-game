"""Touch and keyboard controls.  Buttons use independent pointer ids, so
left/right can be held while jump or attack is pressed simultaneously."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ButtonState:
    name: str
    pressed: bool = False
    pointer_ids: set = None
    pulse: float = 0.0

    def __post_init__(self):
        self.pointer_ids = set()

    def press(self, pointer_id):
        self.pointer_ids.add(pointer_id)
        self.pressed = True
        self.pulse = 1.0

    def release(self, pointer_id):
        self.pointer_ids.discard(pointer_id)
        self.pressed = bool(self.pointer_ids)

    def release_all(self):
        self.pointer_ids.clear()
        self.pressed = False


class ControlState:
    ACTIONS = ("left", "right", "jump", "attack")

    def __init__(self):
        self.buttons = {name: ButtonState(name) for name in self.ACTIONS}
        self.keyboard = {name: False for name in self.ACTIONS}
        self.pause_requested = False
        self.jump_queued = False
        self.attack_queued = False

    def is_down(self, name):
        return self.buttons[name].pressed or self.keyboard[name]

    @property
    def move_axis(self):
        return int(self.is_down("right")) - int(self.is_down("left"))

    def button_down(self, name, pointer_id):
        if name in self.buttons:
            before = self.buttons[name].pressed
            self.buttons[name].press(pointer_id)
            if name == "jump" and not before:
                self.jump_queued = True
            if name == "attack" and not before:
                self.attack_queued = True

    def button_up(self, name, pointer_id):
        if name in self.buttons:
            self.buttons[name].release(pointer_id)

    def consume_jump(self):
        value, self.jump_queued = self.jump_queued, False
        return value

    def consume_attack(self):
        value, self.attack_queued = self.attack_queued, False
        return value

    def set_key(self, key, down):
        mapping = {"left": "left", "right": "right", "a": "left", "d": "right",
                   "spacebar": "jump", "space": "jump", "w": "jump", "up": "jump",
                   "j": "attack", "x": "attack"}
        name = mapping.get(str(key).lower())
        if name:
            if down and not self.keyboard[name] and name == "jump":
                self.jump_queued = True
            if down and not self.keyboard[name] and name == "attack":
                self.attack_queued = True
            self.keyboard[name] = down

    def clear(self):
        for button in self.buttons.values():
            button.release_all()
        for name in self.keyboard:
            self.keyboard[name] = False
