"""Procedurally render the original COMET ZIP player sprites.

Everything is drawn from primitives (no third-party art), supersampled 2x for
anti-aliasing and finished with a hand-drawn style dark outline.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw

from palette import PLAYER as P
from shapes import canvas, outline_alpha, save

SS = 2
FW, FH = 96, 96          # frame size
S = FW * SS

OUT = Path("/home/user/work/game/assets/images/player")
OUTLINE = P["outline"]


def C(t):
    return tuple(t)


def rot(dx, dy, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return dx * c - dy * s, dx * s + dy * c


def limb(d, root, deg, lengths, widths, colors, cap=True):
    """Draw a 2-segment limb. deg=0 points right, 90 points down."""
    x, y = root
    pts = [(x, y)]
    for ln in lengths:
        dx, dy = ln * math.cos(math.radians(deg)), ln * math.sin(math.radians(deg))
        x, y = x + dx, y + dy
        pts.append((x, y))
    for i in range(len(lengths)):
        d.line([pts[i], pts[i + 1]], fill=colors[i], width=widths[i], joint="curve")
    if cap:
        r = widths[-1] / 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=colors[-1])
    return pts[-1]


def shoe(d, at, deg, big=False):
    """Chunky original runner shoe."""
    w, h = (30, 16) if not big else (34, 18)
    base = canvas(int(w * SS) + 8, int(h * SS) + 8)
    bd = ImageDraw.Draw(base)
    bd.rounded_rectangle([2, 2, 2 + w * SS - 1, 2 + h * SS - 1], radius=7 * SS, fill=C(P["shoe"]))
    bd.rounded_rectangle([2, 2, 2 + w * SS - 1, 2 + h * SS * 0.45], radius=7 * SS, fill=C(P["shoe_hi"]))
    bd.rounded_rectangle([2, 2 + h * SS * 0.62, 2 + w * SS - 1, 2 + h * SS - 1], radius=5 * SS, fill=C(P["shoe_low"]))
    bd.ellipse([w * SS * 0.52, 2, w * SS * 0.52 + 3 * SS, 6 * SS], fill=C(P["shoe_hi"]))
    base = base.rotate(-deg, resample=Image.BICUBIC, expand=True)
    d._image.paste(base, (int(at[0] - base.width / 2), int(at[1] - base.height / 2)), base)


def draw_comet(pose, phase):
    """Return an RGBA frame for the given pose and cycle phase (0..1)."""
    im = canvas(S, S)
    d = ImageDraw.Draw(im)
    d._image = im
    bob = 0.0
    lean = 0.0
    tail = -20.0
    legs = [(70, 60), (110, 30)]          # (thigh deg, shin deg) left/right
    arms = [(120, 40), (60, 40)]
    head_dy = 0.0
    squash = 1.0
    ear_back = 0.0

    t = phase * math.tau
    if pose == "idle":
        bob = math.sin(t) * 2.2 * SS
        head_dy = math.sin(t + 0.6) * 1.6 * SS
        arms = [(118 + math.sin(t) * 5, 46), (62 - math.sin(t) * 5, 46)]
    elif pose == "run":
        sway = math.sin(t)
        bob = (abs(math.cos(t)) * -5.0 + 2.0) * SS
        lean = 6.8 * SS
        ear_back = 16
        legs = [(78 + sway * 34, 62 - sway * 46), (108 - sway * 34, 30 + sway * 46)]
        arms = [(132 + sway * 30, 42 + sway * 16), (48 - sway * 30, 42 - sway * 16)]
        tail = -34 + sway * 14
    elif pose == "skid":
        k = phase
        bob = 2 * SS
        lean = -9 * SS * (1 - k * 0.5)
        legs = [(84 - k * 16, 74 - k * 10), (110 + k * 12, 24 + k * 8)]
        arms = [(150 - k * 22, 30), (36 + k * 18, 34)]
        tail = -8
    elif pose == "jump":
        k = phase
        bob = -1 * SS
        lean = 3 * SS
        legs = [(62 + k * 10, 96), (128 - k * 14, 86)]
        arms = [(38 - k * 18, 40), (142 + k * 18, 40)]
        tail = -46
        head_dy = -1.0 * SS
    elif pose == "fall":
        k = phase
        bob = 1.5 * SS
        lean = 1 * SS
        legs = [(70 + k * 8, 70 + k * 10), (120 - k * 8, 60 - k * 10)]
        arms = [(30 + k * 10, 52), (150 - k * 10, 52)]
        tail = -28
    elif pose == "hurt":
        k = phase
        bob = -1 * SS
        lean = -10 * SS - k * 3 * SS
        legs = [(64 + k * 12, 118), (126 - k * 12, 104)]
        arms = [(20 - k * 10, 34), (160 + k * 10, 34)]
        tail = -60
        head_dy = 1.5 * SS
    elif pose == "shoot":
        k = phase
        bob = 0.5 * SS
        lean = 2 * SS
        legs = [(74, 66), (112, 34)]
        arms = [(240 - k * 6, 26), (56, 44)]      # left arm points into the muzzle line
        tail = -14
    else:
        raise ValueError(pose)

    # ---------------------------------------------------------------- legs
    hip_l = (48 * SS + lean * 0.35, 58 * SS + bob)
    hip_r = (50 * SS + lean * 0.35, 58 * SS + bob)
    for idx, (hip, (th, sh)) in enumerate(zip((hip_l, hip_r), legs)):
        dark = C(P["fur_dark"])
        knee = limb(d, hip, th, [11 * SS, 10 * SS], [15 * SS, 12 * SS], [dark, dark], cap=False)
        seg = [C(P["fur_mid"]), C(P["fur_mid"])]
        knee = limb(d, hip, th, [11 * SS, 10 * SS], [12 * SS, 10 * SS], seg, cap=False)
        shoe(d, (knee[0] + 3 * SS, knee[1] + 5 * SS), sh * 0.55, big=(pose in ("run", "skid")))

    # ---------------------------------------------------------------- tail
    tx, ty = 38 * SS, 74 * SS + bob
    dxr, dyr = rot(1, 0, tail)
    tdx, tdy = rot(1, 0, tail + 55)
    tail_pts = [(tx, ty),
                (tx + dxr * 12 * SS, ty + dyr * 12 * SS),
                (tx + dxr * 12 * SS + tdx * 9 * SS, ty + dyr * 12 * SS + tdy * 9 * SS)]
    d.line(tail_pts, fill=C(P["fur_mid"]), width=11 * SS, joint="curve")
    d.line(tail_pts, fill=C(P["fur"]), width=7 * SS, joint="curve")
    d.ellipse([tail_pts[-1][0] - 7 * SS, tail_pts[-1][1] - 7 * SS,
               tail_pts[-1][0] + 7 * SS, tail_pts[-1][1] + 7 * SS], fill=C(P["fur_hi"]))

    # ---------------------------------------------------------------- torso
    bx = lean
    d.ellipse([30 * SS + bx, 44 * SS + bob, 66 * SS + bx, 78 * SS + bob], fill=C(P["fur"]))
    d.ellipse([33 * SS + bx, 50 * SS + bob, 63 * SS + bx, 76 * SS + bob], fill=C(P["fur_mid"]))
    d.ellipse([36 * SS + bx, 54 * SS + bob, 62 * SS + bx, 76 * SS + bob], fill=C(P["belly"]))

    # ---------------------------------------------------------------- arms
    for (ang, ln) in arms:
        sh = (52 * SS + bx * 1.1, 50 * SS + bob)
        elbow = limb(d, sh, ang, [10 * SS, 9 * SS], [13 * SS, 11 * SS], [C(P["fur_dark"])] * 2, cap=False)
        elbow = limb(d, sh, ang, [10 * SS, 9 * SS], [11 * SS, 9 * SS], [C(P["fur_mid"])] * 2, cap=True)
        r = 6 * SS
        d.ellipse([elbow[0] - r, elbow[1] - r, elbow[0] + r, elbow[1] + r], fill=C(P["fur_hi"]))

    # ---------------------------------------------------------------- head
    hx = 58 * SS + bx * 1.35
    hy = 30 * SS + bob + head_dy
    for side in (-1, 1):
        ex, ey = hx + side * 9 * SS, hy - 18 * SS
        tipx, tipy = hx + side * 17 * SS, hy - 30 * SS
        if ear_back:
            tipx, tipy = hx + side * (17 - ear_back * 0.35) * SS, hy - (30 - ear_back) * SS
        d.polygon([(ex - 5 * SS, ey + 6 * SS), (ex + 5 * SS, ey + 6 * SS), (tipx, tipy)],
                  fill=C(P["fur_mid"]))
        d.polygon([(ex - 2.2 * SS, ey + 3 * SS), (ex + 2.2 * SS, ey + 3 * SS),
                   (tipx * 0.94 + ex * 0.06, tipy + 5 * SS)], fill=C(P["fur_hi"]))
    d.ellipse([hx - 21 * SS, hy - 20 * SS, hx + 21 * SS, hy + 20 * SS], fill=C(P["fur"]))
    d.ellipse([hx - 15 * SS, hy - 18 * SS, hx + 12 * SS, hy + 4 * SS], fill=C(P["fur_hi"]))
    # muzzle
    d.ellipse([hx + 6 * SS, hy + 1 * SS, hx + 30 * SS, hy + 18 * SS], fill=C(P["muzzle"]))
    d.ellipse([hx + 20 * SS, hy + 4 * SS, hx + 30 * SS, hy + 12 * SS], fill=C(P["nose"]))
    # eye
    ow = 4.2 * SS
    if pose == "hurt":
        d.line([hx + 2 * SS, hy - 8 * SS, hx + 16 * SS, hy + 2 * SS], fill=C(P["eye"]), width=int(2.4 * SS))
        d.line([hx + 16 * SS, hy - 8 * SS, hx + 2 * SS, hy + 2 * SS], fill=C(P["eye"]), width=int(2.4 * SS))
    else:
        d.ellipse([hx + 4 * SS, hy - 12 * SS, hx + 4 * SS + ow * 3.2, hy + 2 * SS], fill=C(P["eye_white"]))
        px = hx + 8 * SS + (1.4 * SS if pose == "run" else 0)
        d.ellipse([px, hy - 9 * SS, px + ow, hy + 1 * SS], fill=C(P["eye"]))
        d.ellipse([px + 0.6 * SS, hy - 8 * SS, px + ow * 0.45, hy - 6 * SS], fill=C(P["eye_white"]))
    # mouth
    if pose == "hurt":
        d.arc([hx + 10 * SS, hy + 8 * SS, hx + 26 * SS, hy + 20 * SS], 200, 340, fill=C(P["nose"]), width=int(1.8 * SS))
    else:
        d.arc([hx + 10 * SS, hy + 4 * SS, hx + 24 * SS, hy + 16 * SS], 20, 150, fill=C(P["nose"]), width=int(1.8 * SS))

    # ---------------------------------------------------------------- finish
    im = im.resize((FW, FH), Image.LANCZOS)
    im = outline_alpha(im, OUTLINE, 1)
    return im


def attack_frames():
    """Dedicated 2-frame energy-muzzle frames reused from the shoot pose."""
    return [draw_comet("shoot", i / 2) for i in range(2)]


def main():
    sets = {
        "idle": (4, "idle"), "run": (8, "run"), "jump": (2, "jump"), "fall": (2, "fall"),
        "hurt": (2, "hurt"), "shoot": (2, "shoot"), "skid": (2, "skid"),
    }
    written = 0
    for name, (count, pose) in sets.items():
        folded = canvas(FW * count, FH)
        for i in range(count):
            frame = draw_comet(pose, i / count)
            save(frame, OUT / f"{name}_{i}.png")
            folded.alpha_composite(frame, (i * FW, 0))
            written += 1
        save(folded, OUT / f"sheet_{name}.png")
        # mirrored facing is produced by the renderer, sheets stay right-facing
    print(f"player frames written: {written}")
    # quick silhouette sanity check
    f = Image.open(OUT / "run_0.png")
    bbox = f.split()[3].getbbox()
    print("run_0 bbox:", bbox, "of", f.size)


if __name__ == "__main__":
    main()
