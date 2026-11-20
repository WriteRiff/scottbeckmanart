"""Make the brushstroke mask SVGs used by v2's reveal animation and the hidden-message slider.
Run: python v2/tools/make_masks.py"""
import random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "img"
random.seed(7)


def wipe():
    # 300 x 100 box, stretched to the element. Left 130 units solid, then a dry-brush leading
    # edge with bristle streaks running ahead to the right, then empty.
    pts = []
    y = 0.0
    while y <= 100:
        pts.append((128 + random.uniform(-3, 4), y))
        y += random.uniform(0.6, 2.2)
    pts.append((128, 100))
    poly = "M0,0 " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts) + " L0,100 Z"
    streaks = []
    y = 0.0
    while y < 100:
        h = random.uniform(0.35, 1.6)
        length = random.uniform(4, 34) ** 1.0
        x0 = 126 + random.uniform(-2, 3)
        op = random.uniform(0.55, 1)
        streaks.append(f'<rect x="{x0:.1f}" y="{y:.2f}" width="{length:.1f}" height="{h:.2f}" rx="{h/2:.2f}" fill-opacity="{op:.2f}"/>')
        y += h + random.uniform(0.05, 1.1)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100" preserveAspectRatio="none">'
        f'<g fill="#000"><path d="{poly}"/>{"".join(streaks)}</g></svg>'
    )
    (OUT / "mask-wipe.svg").write_text(svg, encoding="utf-8")


def edge():
    # No viewBox: units are CSS px. Solid from x=28 to the right edge; the left 0..28 px is a
    # ragged, bristled paint edge. 3000 px tall so it covers any slider height.
    H = 3000
    pts = []
    y = 0.0
    while y <= H:
        pts.append((14 + random.uniform(-3, 4), y))
        y += random.uniform(2, 7)
    poly = "M40,0 " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts) + f" L40,{H} Z"
    streaks = []
    y = 0.0
    while y < H:
        h = random.uniform(1, 4)
        length = random.uniform(4, 16)
        streaks.append(f'<rect x="{14 - length + 2:.1f}" y="{y:.1f}" width="{length:.1f}" height="{h:.1f}" rx="{h/2:.1f}"/>')
        y += h + random.uniform(0.5, 6)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{H}">'
        f'<g fill="#000"><rect x="38" y="0" width="100%" height="{H}"/><path d="{poly}"/>{"".join(streaks)}</g></svg>'
    )
    (OUT / "mask-edge.svg").write_text(svg, encoding="utf-8")


wipe()
edge()
print("ok", (OUT / "mask-wipe.svg").stat().st_size, (OUT / "mask-edge.svg").stat().st_size)
