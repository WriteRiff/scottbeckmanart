"""Color Field: pull a dominant color, an accent and a 5-chip palette from each painting.

Run:  python v3/tools/colors.py
Writes v3/tools/colors.json (used by build.py) and v3/css/colors.css (one class per painting).
Only reads the shared images in ../assets/img; writes only inside v3/.
"""
import colorsys
import json
from pathlib import Path

import numpy as np
from PIL import Image

# Small curation: for these, the second color reads as the painting's main color.
SWAP = {"white-flowers", "yellow-house"}
# Old Barn's grass reads greener on the wall than in the photo's yellow cast.
HUE_NUDGE = {"old-barn": 0.07}

V3 = Path(__file__).resolve().parents[1]
ROOT = V3.parent
IMG = ROOT / "assets" / "img"

SLUGS = ["wild-radiance", "yellow-flowers", "majestic-horse", "old-barn", "pig", "white-flowers",
         "my-son", "yellow-house", "bliss-birds", "purple-flowers", "lady", "scott"]


def lum(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def hexc(rgb):
    return "#%02x%02x%02x" % tuple(int(round(max(0, min(255, c)))) for c in rgb)


def hls_rgb(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (r * 255, g * 255, b * 255)


def palette(path, n=10):
    im = Image.open(path).convert("RGB")
    im.thumbnail((160, 160))
    q = im.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    out = []
    for count, idx in sorted(q.getcolors(), reverse=True):
        rgb = tuple(pal[idx * 3: idx * 3 + 3])
        out.append((count, rgb))
    total = sum(c for c, _ in out)
    return [(c / total, rgb) for c, rgb in out]


def hls(rgb):
    return colorsys.rgb_to_hls(*(c / 255 for c in rgb))


def vivid_score(share, rgb):
    h, l, s = hls(rgb)
    # Favour colors that are both common and alive (not near-black, not grey).
    life = s * (1 - abs(l - 0.55) * 1.6)
    return share * (0.08 + max(0, life)) ** 1.4


def hue_dist(a, b):
    d = abs(a - b) % 1
    return min(d, 1 - d)


def hue_peaks(path):
    """Hue histogram weighted by how colorful each pixel is. Returns [(weight, mean_rgb, hue)] best first."""
    im = Image.open(path).convert("RGB")
    im.thumbnail((200, 200))
    rgb = np.asarray(im, dtype=np.float32) / 255
    hsv = np.asarray(im.convert("HSV"), dtype=np.float32) / 255
    h, s, v = hsv[..., 0].ravel(), hsv[..., 1].ravel(), hsv[..., 2].ravel()
    px = rgb.reshape(-1, 3)
    w = np.clip(s - 0.12, 0, None) * np.clip(v - 0.18, 0, None)
    bins = 36
    idx = np.minimum((h * bins).astype(int), bins - 1)
    hist = np.bincount(idx, weights=w, minlength=bins)
    smooth = hist + 0.6 * (np.roll(hist, 1) + np.roll(hist, -1)) + 0.25 * (np.roll(hist, 2) + np.roll(hist, -2))
    peaks = []
    used = np.zeros(bins, bool)
    for _ in range(4):
        cand = np.where(used, -1, smooth)
        b = int(np.argmax(cand))
        if cand[b] <= 0:
            break
        near = [(b + k) % bins for k in range(-2, 3)]
        mask = np.isin(idx, near) & (w > 0)
        ww = w[mask][:, None]
        mean = (px[mask] * ww).sum(0) / max(ww.sum(), 1e-6) * 255
        peaks.append((float(smooth[b]), tuple(float(x) for x in mean), (b + 0.5) / bins))
        for k in range(-3, 4):
            used[(b + k) % bins] = True
    return peaks


def derive(slug):
    pal = palette(IMG / f"{slug}-sm.jpg")
    peaks = hue_peaks(IMG / f"{slug}-sm.jpg")
    dom = peaks[0][1]
    dh, dl, ds = hls(dom)
    acc = None
    for wgt, rgb, hue in peaks[1:]:
        if hue_dist(hue, dh) > 0.08 and wgt > peaks[0][0] * 0.04:
            acc = rgb
            break
    if acc is None:
        acc = sorted(pal, key=lambda p: vivid_score(*p), reverse=True)[1][1]
    if slug in SWAP:
        dom, acc = acc, dom
    if slug in HUE_NUDGE:
        h, l, s = hls(dom)
        dom = hls_rgb((h + HUE_NUDGE[slug]) % 1, l, s)
    raw_dom, raw_acc = dom, acc
    ah, al, as_ = hls(acc)
    dh, dl, ds = hls(dom)
    # Nudge the colors toward a brighter, more joyful version (kept close to the paint).
    dom = hls_rgb(dh, min(0.62, max(0.45, dl)), min(0.85, ds * 1.2 + 0.08))
    dh, dl, ds = hls(dom)
    acc = hls_rgb(ah, min(0.6, max(0.4, al)), min(0.85, as_ * 1.2 + 0.08))
    ah, al, as_ = hls(acc)

    ink = (20, 18, 16)
    # Soft field behind the painting, and a slightly deeper wash.
    fs = min(0.88, max(0.5, ds * 1.15))
    field = hls_rgb(dh, 0.865, fs)
    wash = hls_rgb(dh, 0.78, min(0.85, fs + 0.05))
    # Deep color for type accents: same hue, darkened until it reads on the field.
    l = 0.42
    deep = hls_rgb(dh, l, min(0.85, ds + 0.1))
    while contrast(deep, field) < 5.2 and l > 0.08:
        l -= 0.02
        deep = hls_rgb(dh, l, min(0.85, ds + 0.1))
    l = 0.45
    accdeep = hls_rgb(ah, l, min(0.85, as_ + 0.1))
    while contrast(accdeep, field) < 4.6 and l > 0.08:
        l -= 0.02
        accdeep = hls_rgb(ah, l, min(0.85, as_ + 0.1))
    vivid = hls_rgb(dh, min(0.62, max(0.45, dl)), min(0.9, ds + 0.15))
    # Five chips: the most common colors, weighted toward the colorful ones, dark to light.
    chroma = lambda c: (max(c) - min(c)) / 255
    pal16 = palette(IMG / f"{slug}-sm.jpg", 16)
    pick = []
    for share, rgb in sorted(pal16, key=lambda p: p[0] * (0.05 + chroma(p[1]) * 3), reverse=True):
        if all(sum(abs(a - b) for a, b in zip(rgb, q)) > 60 for _, q in pick):
            pick.append((share, rgb))
        if len(pick) == 5:
            break
    chips = [hexc(rgb) for _, rgb in sorted(pick, key=lambda p: hls(p[1])[1])]
    # Make sure the chosen dominant and accent appear among the chips.
    chips = sorted([c for c in chips if c not in (hexc(raw_dom), hexc(raw_acc))][:3] + [hexc(raw_dom), hexc(raw_acc)],
                   key=lambda c: hls(tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)))[1])
    return {
        "dominant": hexc(dom), "accent": hexc(acc), "vivid": hexc(vivid),
        "field": hexc(field), "wash": hexc(wash), "deep": hexc(deep), "accentDeep": hexc(accdeep),
        "chips": chips,
        "contrast": {"deep_on_field": round(contrast(deep, field), 2), "ink_on_field": round(contrast(ink, field), 2)},
    }


def main():
    data = {s: derive(s) for s in SLUGS}
    (V3 / "tools" / "colors.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
    css = ["/* Generated by tools/colors.py from the paintings themselves. Do not edit by hand. */"]
    for s, c in data.items():
        css.append(f".c-{s}{{--field:{c['field']};--wash:{c['wash']};--deep:{c['deep']};--accent:{c['accent']};"
                   f"--accent-deep:{c['accentDeep']};--vivid:{c['vivid']};--dominant:{c['dominant']}}}")
    (V3 / "css" / "colors.css").write_text("\n".join(css) + "\n", encoding="utf-8")
    for s, c in data.items():
        print(f"{s:16} dom {c['dominant']} acc {c['accent']} field {c['field']} deep {c['deep']} {c['contrast']}")


if __name__ == "__main__":
    main()
