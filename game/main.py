"""COMET ZIP Android entry point.

Run locally with ``python main.py`` after installing Kivy.  Build an APK with
Buildozer from the repository root; see ../buildozer.spec and README.md.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Running ``python game/main.py`` from the project root should work too.
GAME_DIR = Path(__file__).resolve().parent
if str(GAME_DIR) not in sys.path:
    sys.path.insert(0, str(GAME_DIR))
os.environ.setdefault("KIVY_NO_ARGS", "1")

try:
    from kivy.config import Config
    Config.set("graphics", "width", "1280")
    Config.set("graphics", "height", "720")
    Config.set("graphics", "resizable", "1")
    Config.set("graphics", "fullscreen", "auto")
    Config.set("input", "mouse", "mouse,disable_multitouch")
    Config.set("kivy", "exit_on_escape", "0")
except Exception:
    Config = None

from config import CONFIG, GAME_SUBTITLE, GAME_TITLE, TILE, TILE_MATERIAL
from game_world import GameWorld
from controls import ControlState
from camera import Camera
from audio import AudioManager
from ui import TextureBank, HudText, button_rects, contains, compact_number, mmss, rgba

try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.window import Window
    from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
    from kivy.uix.label import Label
    from kivy.uix.widget import Widget
    KIVY_AVAILABLE = True
except Exception as exc:  # Make a useful diagnostic instead of a cryptic import crash.
    KIVY_AVAILABLE = False
    KIVY_ERROR = exc


if KIVY_AVAILABLE:
    class GameView(Widget):
        """Main scene: simulation update, world renderer and multitouch input."""
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.world = GameWorld()
            self.controls = ControlState()
            self.camera = Camera()
            self.audio = AudioManager()
            self.textures = TextureBank()
            self.mode = "title"
            self.time = 0.0
            self.touch_actions = {}
            self.control_rects = button_rects(self.width or 1280, self.height or 720)
            self._make_labels()
            self.bind(size=self._on_resize, pos=self._on_resize)
            Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
            Clock.schedule_interval(self._tick, 1 / 60.0)
            self._update_camera(0)
            self._redraw()

        # ----------------------------------------------------------- labels
        def _make_labels(self):
            self.hud = Label(text="")
            self.level_label = Label(text="")
            self.message_label = Label(text="")
            self.center_label = Label(text="")
            self.hint_label = Label(text="")
            for label in (self.hud, self.level_label, self.message_label, self.center_label, self.hint_label):
                self.add_widget(label)
            HudText.style(self.hud, 20, (0.94, 0.98, 1, 1), True)
            HudText.style(self.level_label, 18, (0.73, 0.94, 1, 1), True)
            HudText.style(self.message_label, 22, (1, 0.93, 0.45, 1), True)
            HudText.style(self.center_label, 38, (0.95, 0.99, 1, 1), True)
            HudText.style(self.hint_label, 17, (0.74, 0.88, 0.96, 1), False)

        def _on_resize(self, *_):
            self.control_rects = button_rects(self.width, self.height)
            self._update_labels()
            self._update_camera(0)

        def _update_labels(self):
            w, h = self.width, self.height
            self.hud.pos = (26, h - 67); self.hud.size = (460, 42)
            self.hud.text_size = self.hud.size
            self.level_label.pos = (w / 2 - 250, h - 65); self.level_label.size = (500, 38)
            self.level_label.text_size = self.level_label.size
            self.message_label.pos = (w / 2 - 300, h * .77); self.message_label.size = (600, 44)
            self.message_label.text_size = self.message_label.size
            self.center_label.pos = (w / 2 - 500, h * .44); self.center_label.size = (1000, 76)
            self.center_label.text_size = self.center_label.size
            self.hint_label.pos = (w / 2 - 500, h * .32); self.hint_label.size = (1000, 38)
            self.hint_label.text_size = self.hint_label.size

        # ----------------------------------------------------------- input
        def _on_key_down(self, _window, key, _scancode, codepoint, modifiers):
            key_name = codepoint or {32: "spacebar", 13: "enter", 27: "escape"}.get(key, str(key))
            if key_name in ("enter", "return") and self.mode in ("title", "gameover", "victory"):
                self._start_or_restart()
                return True
            if key_name in ("escape", "p"):
                self._toggle_pause()
                return True
            self.controls.set_key(key_name, True)
            return True

        def _on_key_up(self, _window, key, _scancode):
            mapping = {32: "spacebar", 13: "enter", 27: "escape"}
            self.controls.set_key(mapping.get(key, str(key)), False)
            return True

        def on_touch_down(self, touch):
            x, y = touch.x, touch.y
            if self.mode in ("title", "gameover", "victory"):
                self._start_or_restart()
                return True
            if contains(self.control_rects["pause"], x, y):
                self._toggle_pause()
                touch.grab(self)
                self.touch_actions[touch.uid] = "pause"
                return True
            for action in ("left", "right", "jump", "attack"):
                if contains(self.control_rects[action], x, y):
                    self.controls.button_down(action, touch.uid)
                    touch.grab(self)
                    self.touch_actions[touch.uid] = action
                    return True
            return True  # consume touches: no accidental scroll/zoom gestures

        def on_touch_up(self, touch):
            action = self.touch_actions.pop(touch.uid, None)
            if action and action in self.controls.buttons:
                self.controls.button_up(action, touch.uid)
            if touch.grab_current is self:
                touch.ungrab(self)
            return True

        def on_touch_move(self, touch):
            # A thumb drifting outside a button releases it; a new button can
            # be entered without lifting, which feels natural on phones.
            action = self.touch_actions.get(touch.uid)
            if not action or action == "pause":
                return True
            if not contains(self.control_rects[action], touch.x, touch.y):
                self.controls.button_up(action, touch.uid)
            return True

        def _start_or_restart(self):
            if self.mode == "title":
                self.mode = "playing"
            else:
                self.world.start_new_game()
                self.mode = "playing"
            self.audio.play_music("level1")
            self._update_labels()

        def _toggle_pause(self):
            if self.mode != "playing":
                return
            self.world.paused = not self.world.paused
            self._update_labels()

        # ---------------------------------------------------------- update
        def _update_camera(self, dt):
            self.camera.resize(self.width or 1280, self.height or 720)
            self.camera.set_world_bounds(self.world.world_width, self.world.world_height)
            self.camera.focus(self.world.player, dt)

        def _tick(self, dt):
            self.time += dt
            if self.mode == "playing":
                self.world.update(dt, self.controls, self.audio)
                if self.world.game_over:
                    self.mode = "gameover"
                elif self.world.finished:
                    self.mode = "victory"
            self._update_camera(dt)
            for button in self.controls.buttons.values():
                button.pulse *= 0.84
            self._update_labels()
            self._redraw()

        # --------------------------------------------------------- drawing
        def _screen_y(self, world_y, world_h, cam_y):
            return self.height - (world_y - cam_y + world_h)

        def _tex(self, folder, stem, frame, count):
            frame = int(frame) % count
            return self.textures.get(f"{folder}/{stem}_{frame}.png")

        def _draw_tex(self, texture, x, y, w, h, cam_x, cam_y, flip=False, alpha=1.0):
            if texture is None:
                return
            sx = x - cam_x
            sy = self._screen_y(y, h, cam_y)
            Color(1, 1, 1, alpha)
            coords = (1, 0, 0, 0, 0, 1, 1, 1) if flip else (0, 0, 1, 0, 1, 1, 0, 1)
            Rectangle(pos=(sx, sy), size=(w, h), texture=texture, tex_coords=coords)

        def _redraw(self):
            self.canvas.clear()
            w, h = self.width or 1280, self.height or 720
            cam_x, cam_y = self.camera.offset(self.time)
            # Background is fixed to the screen and is deliberately original.
            bg = self.textures.get(f"environments/background_{self.world.level.theme}.png")
            if bg:
                Rectangle(pos=(0, 0), size=(w, h), texture=bg)
            else:
                Color(.08, .15, .28, 1); Rectangle(pos=(0, 0), size=(w, h))

            with self.canvas:
                if self.mode == "title":
                    self._draw_title(w, h)
                    self._set_label_state()
                    return
                self._draw_world(cam_x, cam_y)
                self._draw_hud_backplates(w, h)
                if self.mode in ("playing",) and not self.world.paused:
                    self._draw_controls(w, h)
                if self.mode in ("gameover", "victory") or self.world.paused:
                    self._draw_modal(w, h)
            self._set_label_state()

        def _draw_world(self, cam_x, cam_y):
            level = self.world.level
            tx0 = max(0, int(cam_x // TILE) - 2); tx1 = min(level.width - 1, int((cam_x + self.width) // TILE) + 2)
            ty0 = max(0, int(cam_y // TILE) - 2); ty1 = min(level.height - 1, int((cam_y + self.height) // TILE) + 2)
            for ty in range(ty0, ty1 + 1):
                for tx in range(tx0, tx1 + 1):
                    tile = level.tile(tx, ty)
                    material = TILE_MATERIAL.get(tile)
                    if material:
                        self._draw_tex(self.textures.get(f"environments/tile_{material}.png"), tx*TILE, ty*TILE, TILE, TILE, cam_x, cam_y)
            for platform in self.world.platforms:
                self._draw_tex(self.textures.get("environments/tile_platform.png"), platform.x, platform.y, platform.w, platform.h, cam_x, cam_y)
            for coin in self.world.coins:
                if not coin.collected:
                    frame = int(coin.anim * 11) % 6
                    self._draw_tex(self._tex("collectibles", "coin_spin", frame, 6), coin.x - 4, coin.y - 9, 30, 40, cam_x, cam_y)
            for power in self.world.powerups.items:
                if not power.dead:
                    self._draw_tex(self._tex("collectibles", "mushroom_idle", int(power.anim*7), 4), power.x - 9, power.y - 10, 48, 48, cam_x, cam_y)
            for cp in self.world.checkpoints:
                self._draw_tex(self.textures.get(f"ui/checkpoint_{'on_0' if cp.active else 'off'}.png"), cp.x-14, cp.y-20, 70, 110, cam_x, cam_y)
            if self.world.goal:
                self._draw_tex(self._tex("ui", "goal_idle", int(self.world.goal.anim*6), 4), self.world.goal.x-18, self.world.goal.y-20, 90, 130, cam_x, cam_y)
            for enemy in self.world.enemies:
                if enemy.defeated and enemy.squash_timer <= 0:
                    continue
                frame = enemy.anim_frame()
                alpha = 1.0 if enemy.hit_flash <= 0 else .45
                ew, eh = enemy.w * 1.6, enemy.h * 1.8
                ey = enemy.y - (eh - enemy.h)
                if enemy.defeated:
                    eh *= .55; ey += enemy.h * .35
                self._draw_tex(self._tex("enemies", f"{enemy.kind}_walk", frame, 4), enemy.cx-ew/2, ey, ew, eh, cam_x, cam_y, enemy.facing < 0, alpha)
            for projectile in self.world.projectiles.items:
                stem = "bolt_fly" if projectile.friendly else "spore_fly"
                self._draw_tex(self._tex("collectibles", stem, int(projectile.anim*12), 2), projectile.x-8, projectile.y-8, 42, 26, cam_x, cam_y, projectile.vx < 0)
            for particle in self.world.particles.items:
                sx = particle.x - cam_x; sy = self._screen_y(particle.y, particle.size, cam_y)
                Color(*(c/255 for c in particle.color), max(0, min(1, particle.life/particle.max_life)))
                if particle.kind == "trail":
                    Ellipse(pos=(sx-particle.size/2, sy-particle.size/2), size=(particle.size, particle.size))
                else:
                    Ellipse(pos=(sx, sy), size=(particle.size, particle.size))
            p = self.world.player
            state, frame = p.sprite_frame()
            if p.hurt_timer > 0 and int(self.time*18)%2 == 0:
                pass
            else:
                pw, ph = p.w*2.15, p.h*2.15
                self._draw_tex(self._tex("player", state, frame, {"idle":4,"run":8,"jump":2,"fall":2,"hurt":2,"shoot":2,"skid":2}[state]), p.cx-pw/2, p.cy-ph/2, pw, ph, cam_x, cam_y, p.facing < 0, .72 if p.invuln > 0 else 1)
                if p.power_flash > 0:
                    Color(.42, .96, .85, .25 + .2 * (p.power_flash % .35))
                    Line(circle=(p.cx-cam_x, self.height-(p.cy-cam_y), max(p.w,p.h)*.9), width=2)

        def _draw_hud_backplates(self, w, h):
            Color(.03, .08, .16, .76); RoundedRectangle(pos=(16, h-72), size=(500, 52), radius=[(16,16)]*4)
            Color(.03, .08, .16, .66); RoundedRectangle(pos=(w/2-260, h-68), size=(520, 44), radius=[(14,14)]*4)

        def _draw_controls(self, w, h):
            for action, label in (("left", "←"), ("right", "→"), ("jump", "JUMP"), ("attack", "ATTACK")):
                x,y,bw,bh = self.control_rects[action]; pressed = self.controls.is_down(action)
                pulse = self.controls.buttons[action].pulse * 3
                Color(.08, .43, .64, .90 if pressed else .72)
                RoundedRectangle(pos=(x-pulse/2,y-pulse/2), size=(bw+pulse,bh+pulse), radius=[(20,20)]*4)
                Color(.32, .86, 1.0, .9); Line(rounded_rectangle=(x-pulse/2,y-pulse/2,bw+pulse,bh+pulse,20), width=2)
                # labels are drawn with canvas-free Kivy Labels in _set_label_state.
            x,y,bw,bh=self.control_rects["pause"]
            Color(.05,.16,.28,.80); RoundedRectangle(pos=(x,y),size=(bw,bh),radius=[(15,15)]*4)
            Color(.4,.9,1,.8); Line(rounded_rectangle=(x,y,bw,bh,15),width=2)

        def _draw_title(self, w, h):
            Color(.02, .06, .13, .32); Rectangle(pos=(0,0), size=(w,h))
            Color(.03, .11, .22, .78); RoundedRectangle(pos=(w*.15,h*.16),size=(w*.70,h*.68),radius=[(28,28)]*4)
            Color(.22,.72,1,.9); Line(rounded_rectangle=(w*.15,h*.16,w*.70,h*.68,28),width=3)

        def _draw_modal(self, w, h):
            Color(.01,.03,.09,.72); Rectangle(pos=(0,0),size=(w,h))
            Color(.04,.12,.24,.94); RoundedRectangle(pos=(w*.23,h*.22),size=(w*.54,h*.54),radius=[(28,28)]*4)
            Color(.25,.82,1,.85); Line(rounded_rectangle=(w*.23,h*.22,w*.54,h*.54,28),width=3)

        def _set_label_state(self):
            self._update_labels()
            if self.mode == "title":
                self.hud.text = ""; self.level_label.text = ""; self.message_label.text = ""
                self.center_label.text = GAME_TITLE
                self.hint_label.text = f"{GAME_SUBTITLE}\n\nTAP TO LAUNCH  •  A/D or ←/→  •  SPACE JUMP  •  J ATTACK"
            elif self.mode == "gameover":
                self.hud.text = f"FINAL SCORE  {compact_number(self.world.score)}"
                self.level_label.text = "RUN ENDED"
                self.center_label.text = "THE SKYLINE FADES"
                self.hint_label.text = "TAP OR PRESS ENTER TO RESTART"
                self.message_label.text = ""
            elif self.mode == "victory":
                self.hud.text = f"FINAL SCORE  {compact_number(self.world.score)}"
                self.level_label.text = "ALL 3 ZONES CLEARED"
                self.center_label.text = "THE SKYLINE IS YOURS!"
                self.hint_label.text = "TAP OR PRESS ENTER TO RUN AGAIN"
                self.message_label.text = ""
            else:
                self.hud.text = (f"SCORE  {compact_number(self.world.score)}     "
                                 f"TOKENS  {self.world.coins_count:02d}     "
                                 f"LIVES  {'♥' * max(0,self.world.lives)}")
                self.level_label.text = f"{self.world.level.name}    {mmss(self.world.time_left)}"
                self.message_label.text = self.world.message if self.world.message_timer > 0 else ""
                if self.world.paused:
                    self.center_label.text = "PAUSED"
                    self.hint_label.text = "TAP THE PAUSE ICON TO RESUME"
                else:
                    self.center_label.text = ""
                    self.hint_label.text = ""

            # Canvas doesn't draw text, so put control captions into the hint
            # label only on normal play? Use a dedicated tiny label-free canvas
            # isn't worth another widget; button labels are rendered below with
            # one custom label per button.
            if not hasattr(self, "button_labels"):
                self.button_labels = {}
                for action, text in (("left","←"),("right","→"),("jump","JUMP"),("attack","ATTACK"),("pause","Ⅱ")):
                    lbl=Label(text=text); HudText.style(lbl, 26 if len(text)>2 else 38, (0.94,0.99,1,1), True); self.add_widget(lbl); self.button_labels[action]=lbl
            for action, lbl in self.button_labels.items():
                x,y,bw,bh=self.control_rects[action]
                lbl.pos=(x,y); lbl.size=(bw,bh); lbl.text_size=lbl.size
                lbl.opacity=1 if self.mode=="playing" and (not self.world.paused or action=="pause") else 0


    class CometZipApp(App):
        title = GAME_TITLE
        def build(self):
            self.icon = str(GAME_DIR / "assets" / "images" / "ui" / "goal_idle_0.png")
            return GameView()

        def on_pause(self):
            # Android resume callback: keep game alive and freeze simulation.
            return True

    def main():
        CometZipApp().run()

else:
    def main():
        raise RuntimeError("Kivy is required to run COMET ZIP. Install Kivy 2.3+ or build with Buildozer.") from KIVY_ERROR


if __name__ == "__main__":
    main()
