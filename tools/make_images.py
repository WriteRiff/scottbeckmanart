"""Make web-sized copies of the paintings for the site.

Usage:  python tools/make_images.py
Reads originals from archive/images (or any path listed below), writes
assets/img/<name>-sm.jpg (900 px wide) and <name>-lg.jpg (up to 2400 px),
and assets/img/sizes.json with each file's width and height.
To add a painting: put the original anywhere, add a line to IMAGES, run again.
"""
import json, os
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "archive", "images")
OUT = os.path.join(ROOT, "assets", "img")

IMAGES = {
    "wild-radiance": "19131dab_Wild_Radiance.jpg",
    "wild-radiance-detail": "698f58bb_Wild_Radianceb.jpg",
    "wild-radiance-message": "38457b82_Wild_Radiancemessage.jpg",
    "yellow-house": "3e8bbf13_Yellowhouse2.jpg",
    "yellow-house-framed": "7a19c90b_Yellowhouse.jpg",
    "yellow-house-detail": "74928d84_Yellowhouse4.jpg",
    "yellow-house-3": "6a2910e8_Yellowhouse3.jpg",
    "yellow-house-frame": "f9f746a4_Yellowhouse5.jpg",
    "old-barn": "d683823b_Barn16x20.jpg",
    "old-barn-framed": "978b26a7_Barn16x20_1.jpg",
    "old-barn-2": "d9ed6b28_Barn16x20_2.jpg",
    "old-barn-3": "73021a31_Barn16x20_3.jpg",
    "old-barn-frame": "349c01d6_Barn16x20_4.jpg",
    "pig": "fccb42de_Pig.jpg",
    "white-flowers": "8bf2ca26_WhiteFlowers.jpg",
    "my-son": "433b33af_MySon.jpg",
    "lady": "e541bb41_Lady.jpg",
    "majestic-horse": "363245ea_MajesticHorse.jpg",
    "bliss-birds": "52c634cb_BlissBirds.jpg",
    "purple-flowers": "76dcf5a3_PurpleFlowers.jpg",
    "yellow-flowers": "f1312cde_Yellowflowers.jpg",
    "yellow-flowers-message": "57701093_Yellowflowersmessage.jpg",
    "scott": "c3911b0e_Scott2.jpg",
}

def save(im, path, max_w=None, max_long=None):
    im = im.copy()
    if max_w and im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    if max_long and max(im.size) > max_long:
        s = max_long / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im.save(path, "JPEG", quality=82, optimize=True, progressive=True)
    return im.size

os.makedirs(OUT, exist_ok=True)
sizes = {}
for name, src in IMAGES.items():
    p = src if os.path.isabs(src) else os.path.join(A, src)
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    sm = save(im, os.path.join(OUT, f"{name}-sm.jpg"), max_w=900)
    lg = save(im, os.path.join(OUT, f"{name}-lg.jpg"), max_long=2400)
    sizes[name] = {"sm": sm, "lg": lg}
    print(name, sm, lg)
json.dump(sizes, open(os.path.join(OUT, "sizes.json"), "w"), indent=1)
