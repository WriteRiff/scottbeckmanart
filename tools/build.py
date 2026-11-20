"""Fill the shared parts of every page from content/artworks.json.

Usage:  python tools/build.py
Each page keeps its own text. Between marker comments like
<!-- HEADER --> ... <!-- /HEADER --> this script rewrites the header, footer,
painting grids and the "available originals" cards. Safe to run any time.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "content", "artworks.json"), encoding="utf-8"))
ARTS = data["artworks"]
SIZES = json.load(open(os.path.join(ROOT, "assets", "img", "sizes.json")))
PAGES = {"index.html": "home", "work/index.html": "work", "commissions/index.html": "commissions",
         "about/index.html": "about", "contact/index.html": "contact", "404.html": "404"}
NAV = [("work/", "Work", "work"), ("commissions/", "Commissions", "commissions"),
       ("about/", "About", "about"), ("contact/", "Contact", "contact")]
SOCIAL = [
    ("Instagram", "https://www.instagram.com/scottbeckmanart/", '<path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10Zm0 8.2A3.2 3.2 0 1 1 12 8.8a3.2 3.2 0 0 1 0 6.4ZM17.3 5.5a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4ZM21.9 7.1c-.1-1.6-.4-3-1.6-4.2S17.6 1.3 16 1.2C14.3 1.1 9.7 1.1 8 1.2c-1.6.1-3 .4-4.2 1.6S2.2 5.5 2.1 7.1C2 8.8 2 13.2 2.1 14.9c.1 1.6.4 3 1.6 4.2s2.6 1.5 4.2 1.6c1.7.1 6.3.1 8 0 1.6-.1 3-.4 4.2-1.6s1.5-2.6 1.6-4.2c.1-1.7.1-6.1.2-7.8Zm-2.2 9.9a3.3 3.3 0 0 1-1.8 1.8c-1.3.5-4.3.4-5.9.4s-4.6.1-5.9-.4A3.3 3.3 0 0 1 4.3 17c-.5-1.3-.4-4.3-.4-5.7s-.1-4.4.4-5.7A3.3 3.3 0 0 1 6.1 3.8C7.4 3.3 10.4 3.4 12 3.4s4.6-.1 5.9.4a3.3 3.3 0 0 1 1.8 1.8c.5 1.3.4 4.3.4 5.7s.1 4.4-.4 5.7Z"/>'),
    ("YouTube", "https://www.youtube.com/@paintingwithscott", '<path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8ZM9.8 15V9l5.8 3-5.8 3Z"/>'),
    ("Facebook", "https://www.facebook.com/profile.php?id=61572902832946", '<path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.4v7A10 10 0 0 0 22 12Z"/>'),
]
SUBJECTS = {"florals": "Florals", "animals": "Animals", "landscapes": "Landscapes", "portraits": "Portraits"}
e = html.escape


def social_html():
    return '<div class="social">' + "".join(
        f'<a href="{u}" rel="noopener" target="_blank"><svg viewBox="0 0 24 24" aria-hidden="true">{p}</svg>{n}</a>'
        for n, u, p in SOCIAL) + "</div>"


def header(pre, key):
    links = "".join(
        f'<a href="{pre}{h}"{" aria-current=\"page\"" if k == key else ""}>{t}</a>' for h, t, k in NAV)
    return (f'<a class="skip" href="#main">Skip to content</a>\n<header class="site-header"><div class="wrap">'
            f'<a class="brand" href="{pre or "./"}"><span class="name">Scott Beckman</span><span class="tag">Original oil paintings</span></a>'
            f'<nav class="nav" aria-label="Main">{links}</nav></div></header>')


def footer(pre):
    return (f'<footer class="site-footer"><div class="wrap">{social_html()}'
            f'<small>© <span data-year>2026</span> Scott Michael Beckman. All paintings and images are the artist\'s own; please ask before reusing them.</small>'
            f'</div></footer>')


def img_attrs(slug, pre, which="sm"):
    w, h = SIZES[slug][which]
    return f'src="{pre}assets/img/{slug}-{which}.jpg" width="{w}" height="{h}"'


def link_attrs(slug, pre, title, meta):
    w, h = SIZES[slug]["lg"]
    return (f'href="{pre}assets/img/{slug}-lg.jpg" data-pswp-width="{w}" data-pswp-height="{h}" '
            f'data-title="{e(title)}" data-meta="{e(meta)}"')


def meta_of(a):
    return " · ".join(x for x in [a.get("medium") or "Oil painting", a["size"], "Available" if a.get("available") else ""] if x)


def figure(a, pre, lazy=True):
    badge = '<span class="badge">Available</span>' if a.get("available") else ""
    avail = " data-available" if a.get("available") else ""
    return (f'<figure class="art" data-subject="{a["subject"]}"{avail}>'
            f'<a {link_attrs(a["slug"], pre, a["title"], meta_of(a))}>{badge}'
            f'<img {img_attrs(a["slug"], pre)} alt="{e(a["alt"])}"{" loading=\"lazy\"" if lazy else ""} decoding="async"></a>'
            f'<figcaption><span class="t">{e(a["title"])}</span><span class="m">{e(a["size"])}</span></figcaption></figure>')


def available_cards(pre):
    out = []
    for a in [x for x in ARTS if x.get("available")]:
        photos = [a["slug"]] + a.get("photos", [])[:2]
        extra = a.get("photos", [])[2:]
        links = "".join(
            f'<a {link_attrs(p, pre, a["title"], meta_of(a))}><img {img_attrs(p, pre)} alt="{e(a["alt"] if i == 0 else a["title"] + ", photo of the painting in its handmade frame")}" loading="lazy" decoding="async"></a>'
            for i, p in enumerate(photos))
        hidden = "".join(f'<a {link_attrs(p, pre, a["title"], meta_of(a))} hidden></a>' for p in extra)
        price = f'<p class="price">{e(a["price"])}</p>' if a.get("price") and SHOW_PRICES else ""
        out.append(
            f'<article><div class="photos" data-gallery>{links}{hidden}</div><div class="body">'
            f'<h3>{e(a["title"])}</h3><p class="specs">{e(a.get("medium", "Oil painting"))} · {e(a["size"])}</p>'
            f'{price}<p>{e(a["frame"])}</p>'
            f'<a class="btn ghost" href="{pre}contact/" data-mail data-subject="About the painting &quot;{e(a["title"])}&quot;">Ask about this painting</a>'
            f'</div></article>')
    return '<div class="available">' + "".join(out) + "</div>"


SHOW_PRICES = data.get("show_prices", True)


def replace(text, name, content):
    pat = re.compile(rf"(<!-- {name} -->)(.*?)(<!-- /{name} -->)", re.S)
    return pat.sub(lambda m: m.group(1) + "\n" + content + "\n" + m.group(3), text)


for rel, key in PAGES.items():
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        continue
    pre = "../" * rel.count("/")
    t = open(path, encoding="utf-8").read()
    t = replace(t, "HEADER", header(pre, key))
    t = replace(t, "FOOTER", footer(pre))
    t = replace(t, "SOCIAL", social_html())
    t = replace(t, "GALLERY:all", "\n".join(figure(a, pre, i > 2) for i, a in enumerate(ARTS)))
    t = replace(t, "GALLERY:featured", "\n".join(figure(a, pre) for a in ARTS if a.get("featured")))
    t = replace(t, "AVAILABLE", available_cards(pre))
    filt = '<button type="button" data-filter="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-filter="{k}" aria-pressed="false">{v}</button>' for k, v in SUBJECTS.items()) + \
        '<button type="button" data-filter="available" aria-pressed="false">Available</button>'
    t = replace(t, "FILTERS", filt)
    open(path, "w", encoding="utf-8", newline="\n").write(t)
    print("built", rel)
