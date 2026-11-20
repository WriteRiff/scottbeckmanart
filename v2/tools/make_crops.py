"""Make the v2 detail crops (zoomed painting details and brush texture) into v2/img/.
Run: python v2/tools/make_crops.py  (from the website folder)."""
from pathlib import Path
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "v2" / "img"
OUT.mkdir(exist_ok=True)
A = ROOT / "assets" / "img"

# name: (source, box in source pixels, output width)
CROPS = {
    "detail-radiance-sun": (A / "wild-radiance-lg.jpg", (700, 0, 1500, 520), 1600),
    "detail-radiance-petal": (A / "wild-radiance-lg.jpg", (860, 820, 1500, 1420), 1200),
    "detail-yellow-bloom": (A / "yellow-flowers-lg.jpg", (0, 40, 700, 620), 1200),
    "detail-horse-eye": (A / "majestic-horse-lg.jpg", (880, 380, 1360, 760), 1200),
    "detail-pig": (A / "pig-lg.jpg", (700, 900, 1400, 1500), 1200),
    "detail-dogwood": (A / "white-flowers-lg.jpg", (300, 640, 1000, 1150), 1200),
    "detail-barn-field": (A / "old-barn-lg.jpg", (300, 800, 1300, 1120), 1600),
    "brush": (ROOT / "archive" / "images" / "6a145c85_paint2.jpg", (0, 0, 1440, 992), 1440),
    "brush-strip": (ROOT / "archive" / "images" / "6a145c85_paint2.jpg", (0, 300, 1440, 700), 1440),
}

for name, (src, box, w) in CROPS.items():
    im = Image.open(src).convert("RGB").crop(box)
    h = round(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    im = ImageEnhance.Sharpness(im).enhance(1.15)
    im.save(OUT / f"{name}.jpg", quality=82, optimize=True, progressive=True)
    sm = im.resize((min(800, w), round(h * min(800, w) / w)), Image.LANCZOS)
    sm.save(OUT / f"{name}-sm.jpg", quality=80, optimize=True, progressive=True)
    print(name, im.size, sm.size)

