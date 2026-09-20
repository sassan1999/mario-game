"""Small drawing helpers built on Pillow primitives."""
from PIL import Image, ImageDraw, ImageFilter


def canvas(w, h, color=(0, 0, 0, 0)):
    return Image.new("RGBA", (w, h), color)


def ellipse(d, box, fill, outline=None, width=1):
    d.ellipse(box, fill=fill, outline=outline, width=width)


def rrect(d, box, radius, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def outline_alpha(img, color, thickness=1):
    """Add an outer outline around every opaque pixel run."""
    alpha = img.split()[3]
    grown = alpha.filter(ImageFilter.MaxFilter(thickness * 2 + 1))
    ring = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ring.putalpha(grown)
    ring.paste(color, (0, 0), grown)
    ring.alpha_composite(img)
    return ring


def glow(img, color, radius=3, strength=140):
    layer = img.copy()
    from PIL import ImageChops
    a = layer.split()[3].filter(ImageFilter.GaussianBlur(radius))
    a = a.point(lambda v: min(255, int(v * strength / 255)) if v else 0)
    halo = Image.new("RGBA", img.size, color + (0,))
    halo.putalpha(a)
    halo.alpha_composite(img)
    return halo


def shift(img, dx, dy, colorize=None):
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    if colorize is not None:
        solid = Image.new("RGBA", img.size, colorize + (255,))
        solid.putalpha(img.split()[3])
        out.paste(solid, (dx, dy))
        return out
    out.paste(img, (dx, dy), img)
    return out


def scale(img, factor):
    return img.resize((max(1, int(img.width * factor)), max(1, int(img.height * factor))), Image.NEAREST)


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
