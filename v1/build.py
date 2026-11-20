"""Builds the Night Gallery (v1) pages from ../content/artworks.json.
Run:  python v1/build.py   (from the site folder, or anywhere)
"""
import json
from html import escape
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
DATA = json.loads((SITE / "content" / "artworks.json").read_text(encoding="utf-8"))
SIZES = json.loads((SITE / "assets" / "img" / "sizes.json").read_text(encoding="utf-8"))
ARTS = DATA["artworks"]
BY = {a["slug"]: a for a in ARTS}

ICONS = {
    "Instagram": ("https://www.instagram.com/scottbeckmanart/", '<path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10Zm0 8.2A3.2 3.2 0 1 1 12 8.8a3.2 3.2 0 0 1 0 6.4ZM17.3 5.5a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4ZM21.9 7.1c-.1-1.6-.4-3-1.6-4.2S17.6 1.3 16 1.2C14.3 1.1 9.7 1.1 8 1.2c-1.6.1-3 .4-4.2 1.6S2.2 5.5 2.1 7.1C2 8.8 2 13.2 2.1 14.9c.1 1.6.4 3 1.6 4.2s2.6 1.5 4.2 1.6c1.7.1 6.3.1 8 0 1.6-.1 3-.4 4.2-1.6s1.5-2.6 1.6-4.2c.1-1.7.1-6.1.2-7.8Zm-2.2 9.9a3.3 3.3 0 0 1-1.8 1.8c-1.3.5-4.3.4-5.9.4s-4.6.1-5.9-.4A3.3 3.3 0 0 1 4.3 17c-.5-1.3-.4-4.3-.4-5.7s-.1-4.4.4-5.7A3.3 3.3 0 0 1 6.1 3.8C7.4 3.3 10.4 3.4 12 3.4s4.6-.1 5.9.4a3.3 3.3 0 0 1 1.8 1.8c.5 1.3.4 4.3.4 5.7s.1 4.4-.4 5.7Z"/>'),
    "YouTube": ("https://www.youtube.com/@paintingwithscott", '<path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8ZM9.8 15V9l5.8 3-5.8 3Z"/>'),
    "Facebook": ("https://www.facebook.com/profile.php?id=61572902832946", '<path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.4v7A10 10 0 0 0 22 12Z"/>'),
}


def social():
    return '<div class="social">' + "".join(
        f'<a href="{u}" rel="noopener" target="_blank"><svg viewBox="0 0 24 24" aria-hidden="true">{p}</svg>{n}</a>'
        for n, (u, p) in ICONS.items()) + "</div>"


ARROW = '<span class="arr" aria-hidden="true"></span>'


def wh(name, size="sm"):
    w, h = SIZES[name][size]
    return w, h


def medium(a):
    return a.get("medium", "Oil painting")


def meta_line(a):
    m = f'{medium(a)} · {a["size"]}'
    return m + (" · Available" if a.get("available") else "")


def img(A, name, alt, size="sm", lazy=True, extra="", cls=""):
    w, h = wh(name, size)
    attrs = ' loading="lazy" decoding="async"' if lazy else ""
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{A}img/{name}-{size}.jpg" width="{w}" height="{h}" alt="{escape(alt)}"{attrs}{extra}>'


def pswp_a(A, a, name=None, inner="", cls="frame", hidden=False):
    name = name or a["slug"]
    w, h = wh(name, "lg")
    hid = " hidden" if hidden else ""
    return (f'<a class="{cls}" href="{A}img/{name}-lg.jpg" data-pswp-width="{w}" data-pswp-height="{h}" '
            f'data-title="{escape(a["title"])}" data-meta="{escape(meta_line(a))}"{hid}>{inner}</a>')


def page(P, title, desc, body, current="", og="wild-radiance", extra_head="", gallery=False):
    A = P + "../assets/"
    nav = "".join(
        f'<a href="{P}{slug}/"' + (' aria-current="page"' if current == slug else "") + f'>{label}</a>'
        for slug, label in [("work", "Work"), ("commissions", "Commissions"), ("about", "About"), ("contact", "Contact")])
    ps_css = f'<link rel="stylesheet" href="{A}vendor/photoswipe/photoswipe.css">\n' if gallery else ""
    ps_js = f'<script type="module" src="{A}js/gallery.js"></script>\n' if gallery else ""
    foot_nav = "".join(f'<a href="{P}{s}/">{l}</a>' for s, l in [("work", "The collection"), ("commissions", "Commissions"), ("about", "About Scott"), ("contact", "Contact")])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="{A}img/{og}-lg.jpg">
<meta property="og:type" content="website">
<meta name="theme-color" content="#13110f">
<link rel="icon" href="{A}img/favicon.png">
<script>document.documentElement.classList.add("js")</script>
<link rel="preload" href="{P}fonts/bodoni-moda-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{P}fonts/jost-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}css/night.css">
{ps_css}{extra_head}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
  <a class="brand" href="{P or './'}"><span class="name">Scott Michael Beckman</span><span class="tag">Original oil paintings</span></a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav"><span class="txt">Menu</span><span class="bars" aria-hidden="true"></span></button>
  <nav class="nav" id="site-nav" aria-label="Main">{nav}</nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="site-footer"><div class="wrap">
  <div class="foot">
    <div class="brandcol"><p class="sig">Scott Michael <em>Beckman</em></p><p class="sub">Original oil paintings, made in Central Arkansas. Commissions welcome.</p></div>
    <div><h2>Visit</h2><nav aria-label="Footer">{foot_nav}</nav></div>
    <div><h2>Follow</h2>{social()}</div>
  </div>
  <div class="fine"><span>© <span data-year>2026</span> Scott Michael Beckman</span><span>All paintings and images are the artist's own; please ask before reusing them.</span></div>
</div></footer>
<script src="{A}js/site.js" defer></script>
<script src="{P}js/night.js" defer></script>
{ps_js}</body>
</html>
"""


def label_html(a, no=None, artist=True):
    s = '<div class="tag-label">'
    if no is not None:
        s += f'<span class="no">No. {no:02d}</span>'
    s += f'<span class="t">{escape(a["title"])}</span>'
    if artist:
        s += '<span class="a">Scott Michael Beckman, American</span>'
    s += f'<span class="m">{escape(medium(a))}</span><span class="m">{escape(a["size"])}</span>'
    if a.get("available"):
        s += '<span class="avail">Available</span>'
    return s + "</div>"


LOCK_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3.6"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/></svg>'


def reveal(A, base, msg, size, start, label, alt_base, alt_msg):
    w, h = wh(base, size)
    return f"""<div class="reveal" style="--pos:{start}%">
  <img src="{A}img/{base}-{size}.jpg" width="{w}" height="{h}" alt="{escape(alt_base)}" loading="lazy" decoding="async">
  <div class="top"><img src="{A}img/{msg}-{size}.jpg" width="{w}" height="{h}" alt="{escape(alt_msg)}" loading="lazy" decoding="async"></div>
  <div class="dim"></div>
  <input type="range" min="0" max="100" value="{start}" aria-label="{escape(label)}">
  <div class="beam"><span class="knob">{LOCK_SVG}</span></div>
</div>"""


# ------------------------------------------------------------------ HOME
def home():
    P = ""
    A = "../assets/"
    hero_set = [("wild-radiance", "lg", "(min-width: 901px) 52vh, 80vw"),
                ("majestic-horse", "lg", "(min-width: 901px) 56vw, 96vw"),
                ("yellow-flowers", "lg", "(min-width: 901px) 56vw, 96vw"),
                ("pig", "lg", "(min-width: 901px) 46vw, 90vw")]
    slides, caps = [], []
    for n, (slug, _, sizes) in enumerate(hero_set):
        a = BY[slug]
        sw, sh = wh(slug, "sm"); lw, lh = wh(slug, "lg")
        extra = ' fetchpriority="high"' if n == 0 else ""
        lazy = "" if n == 0 else ' loading="lazy"'
        slides.append(
            f'<div class="slide{" is-on" if n == 0 else ""}">'
            f'<img src="{A}img/{slug}-sm.jpg" srcset="{A}img/{slug}-sm.jpg {sw}w, {A}img/{slug}-lg.jpg {lw}w" sizes="{sizes}" '
            f'width="{sw}" height="{sh}" alt="{escape(a["alt"])}"{lazy} decoding="async"{extra}></div>')
        caps.append(f'<div class="cap-item{" is-on" if n == 0 else ""}"><span class="t">{escape(a["title"])}</span>'
                    f'<span class="m">{escape(medium(a))} · {escape(a["size"])}</span></div>')

    walk_set = [("white-flowers", ""), ("majestic-horse", "r wide"), ("pig", ""), ("purple-flowers", "r wide"), ("my-son", "wide")]
    bays = []
    for n, (slug, cls) in enumerate(walk_set, 1):
        a = BY[slug]
        bays.append(f'<figure class="bay lit {cls}">' + pswp_a(A, a, inner=img(A, slug, a["alt"])) +
                    f'<figcaption>{label_html(a, n)}</figcaption></figure>')
    # figcaption wrapper must not break grid; flatten it
    bays = [b.replace("<figcaption>", "").replace("</figcaption>", "") for b in bays]

    originals = []
    for slug in ["old-barn", "yellow-house"]:
        a = BY[slug]
        photos = a["photos"]
        main_name = slug  # the painting itself; frame photos below
        thumbs = photos
        th_html = ""
        for k, nm in enumerate(thumbs):
            if k < 3:
                inner = img(A, nm, f'{a["title"]}, ' + ("in the oak frame Scott built for it" if k == 0 else "detail of the painting and its handmade oak frame"))
                if k == 2 and len(thumbs) > 3:
                    inner += f'<span class="more">+{len(thumbs) - 3} more</span>'
                th_html += pswp_a(A, a, nm, inner, cls="")
            else:
                th_html += pswp_a(A, a, nm, "", cls="", hidden=True)
        originals.append(f"""<article class="original lit">
  <div data-gallery>
    <div class="hang">{pswp_a(A, a, main_name, img(A, main_name, a["alt"]))}</div>
    <div class="photos">{th_html}</div>
  </div>
  <div class="info tag-label">
    <h3>{escape(a["title"])}</h3>
    <p class="specs">{escape(a["medium"])} · {escape(a["size"])}</p>
    <p class="status"><span class="avail">Available, ask about it</span></p>
    <p class="frame-note">{escape(a["frame"])}</p>
    <a class="link" href="contact/?painting={quote(a["title"])}#message">Ask about this painting {ARROW}</a>
  </div>
</article>""")

    body = f"""<div class="house-lights" aria-hidden="true"></div>
<section class="hero" data-hero aria-label="Introduction">
  <div class="stage" aria-roledescription="slideshow" aria-label="Featured paintings">{''.join(slides)}</div>
  <div class="hero-copy">
    <h1><span class="pre">Oil paintings · Central Arkansas</span><span class="ln">Scott</span><span class="ln">Michael</span><span class="ln"><em>Beckman</em></span></h1>
    <p class="lead">Flowers, animals, landscapes and people in oil, built layer by layer until the canvas holds its own light.</p>
    <div class="now">
      <div class="cap" aria-live="polite">{''.join(caps)}</div>
      <div class="ctrl no-js-hide">
        <button type="button" data-step="-1" aria-label="Previous painting"><svg viewBox="0 0 14 14" aria-hidden="true"><path d="M9.5 1.5 4 7l5.5 5.5-1 1L2 7l6.5-6.5z"/></svg></button>
        <span class="count" aria-hidden="true">01 / 04</span>
        <button type="button" data-step="1" aria-label="Next painting"><svg viewBox="0 0 14 14" aria-hidden="true"><path d="M4.5 1.5 10 7l-5.5 5.5 1 1L12 7 5.5.5z"/></svg></button>
        <button type="button" data-pause aria-label="Pause slideshow"></button>
      </div>
    </div>
  </div>
  <span class="scroll-cue" aria-hidden="true"></span>
</section>

<section class="section" aria-labelledby="walk-h">
  <div class="wrap">
    <div class="section-head fade">
      <div><p class="eyebrow">The gallery</p><h2 id="walk-h">A walk through <em>the studio</em></h2></div>
      <p>Every canvas is built slowly, in layers of oil, until the light seems to come from inside the paint. Select any painting to see it larger.</p>
    </div>
    <div class="walk" data-gallery>
      {''.join(bays)}
    </div>
    <div class="walk-end fade"><a class="btn" href="work/">See all {len(ARTS)} paintings</a></div>
  </div>
</section>

<section class="section" aria-labelledby="secret-h">
  <div class="wrap secret">
    <div class="copy fade">
      <p class="eyebrow">A hidden message</p>
      <h2 id="secret-h">Some paintings keep <em>a secret</em></h2>
      <p class="date">January 19, 2002</p>
      <p>On their wedding day, Scott gave his wife Jana <em>Yellow Flowers</em>. Hidden in the texture of the petals and background is a message only they knew was there.</p>
      <p>More than twenty years later it is still the piece she loves showing people most. She tells them the story, then asks if they can see the words.</p>
      <p><strong>Shine the light across the painting to find them.</strong></p>
      <a class="link" href="commissions/">Put your own message in a painting {ARROW}</a>
    </div>
    <div class="fade">
      {reveal(A, "yellow-flowers", "yellow-flowers-message", "lg", 58, "Slide to shine a light across Yellow Flowers and reveal the hidden message",
              "Yellow Flowers, the painting as it appears on the wall", "Yellow Flowers with the hidden words 'With love' and 'I love you' traced in red")}
      <div class="reveal-label"><span>Yellow Flowers · 24 × 36 in</span><span class="hint">Drag the light</span></div>
    </div>
  </div>
</section>

<section class="section" id="available" aria-labelledby="avail-h">
  <div class="wrap">
    <div class="section-head fade">
      <div><p class="eyebrow">Available originals</p><h2 id="avail-h">Ready to hang, in frames <em>he built by hand</em></h2></div>
      <p>Scott mills the oak for his frames from trees on his own land, so each frame is as one-of-a-kind as the painting inside it.</p>
    </div>
    <div class="originals">{''.join(originals)}</div>
  </div>
</section>

<section class="section" aria-labelledby="artist-h">
  <div class="wrap artist">
    <div class="lit"><div class="frame">{img(A, "scott", "Portrait of Scott Beckman outdoors among trees")}</div></div>
    <div class="fade">
      <p class="eyebrow" id="artist-h">The artist</p>
      <blockquote class="quote">“Art is my lifelong pursuit. Each new work is an opportunity to grow and challenge myself. I strive to make every painting the best I’ve ever done.”<cite>Scott Michael Beckman</cite></blockquote>
      <p>Born in Cincinnati and now living in Central Arkansas, Scott is a U.S. military veteran and registered nurse who worked in Texas ICUs during the Covid-19 pandemic. Those years shape how he paints: patiently, with an eye for the small moments that matter.</p>
      <a class="link" href="about/">Read Scott’s story {ARROW}</a>
    </div>
  </div>
</section>"""
    return page(P, "Scott Beckman Art | Original Oil Paintings",
                "Original oil paintings by Scott Michael Beckman: florals, animals, landscapes and portraits, painted in Central Arkansas. Commissions welcome.",
                body, gallery=True,
                extra_head=f'<link rel="preload" as="image" href="{A}img/wild-radiance-sm.jpg" imagesrcset="{A}img/wild-radiance-sm.jpg 900w, {A}img/wild-radiance-lg.jpg 1500w" imagesizes="(min-width: 901px) 52vh, 80vw">\n')


# ------------------------------------------------------------------ WORK
def work():
    P = "../"
    A = "../../assets/"
    subjects = [("all", "All"), ("florals", "Florals"), ("animals", "Animals"), ("landscapes", "Landscapes"), ("portraits", "Portraits"), ("available", "Available")]
    def cnt(f):
        if f == "all": return len(ARTS)
        if f == "available": return sum(1 for a in ARTS if a.get("available"))
        return sum(1 for a in ARTS if a["subject"] == f)
    filt = "".join(f'<button type="button" data-filter="{f}" aria-pressed="{"true" if f == "all" else "false"}">{l}<sup>{cnt(f)}</sup></button>' for f, l in subjects)
    items = []
    for n, a in enumerate(ARTS, 1):
        av = " data-available" if a.get("available") else ""
        lab = (f'<div class="tag-label"><div><span class="t">{escape(a["title"])}</span>'
               + ('<span class="avail">Available</span>' if a.get("available") else "")
               + f'</div><span class="m">{escape(a["size"])}<br>{escape(medium(a))}</span></div>')
        items.append(f'<figure class="art lit" data-subject="{a["subject"]}"{av}><div class="hang">'
                     + pswp_a(A, a, inner=img(A, a["slug"], a["alt"], lazy=n > 3)) + f'</div>{lab}</figure>')
    body = f"""<section class="wrap page-head">
  <p class="eyebrow">The collection</p>
  <h1>Eleven paintings, <em>one wall</em></h1>
  <p class="lead">Florals, animals, landscapes and a portrait, all in oil. Select a painting to see it full size, brushstrokes and all.</p>
</section>
<section class="wrap" aria-label="All paintings">
  <div class="filters" role="group" aria-label="Show paintings by subject">{filt}</div>
  <div class="collection gallery" data-gallery>
    {''.join(items)}
  </div>
  <div class="commission-cta fade">
    <h2>Have a painting <em>in mind?</em></h2>
    <a class="btn" href="../commissions/">Commission Scott</a>
  </div>
</section>
<div class="section tight"></div>"""
    return page(P, "The Collection | Scott Beckman Art",
                "All original oil paintings by Scott Michael Beckman: florals, animals, landscapes and portraits, with sizes. Two framed originals are available.",
                body, current="work", gallery=True)


# ------------------------------------------------------------------ COMMISSIONS
PRICES = [(11, 14, "$900", "lady"), (16, 20, "$1,800", "old-barn"), (18, 24, "$2,450", "yellow-house"),
          (24, 36, "$4,850", "wild-radiance"), (24, 48, "$6,500", "purple-flowers"), (30, 40, "$6,750", "white-flowers")]

STEPS = ["Phone consultation with the artist.",
         "Verbal agreement on subject, size and price.",
         "The artist designs a digital composition and presents it to you.",
         "If you both decide to go forward, a written contract is signed by both.",
         "You pay 50% up front, before the physical painting begins.",
         "The artist completes the painting.",
         "You pay the remaining 50% and receive your finished painting.",
         "You hang it somewhere visible, with bragging rights to an original Scott Beckman oil painting."]

FAQ = [("How long does it take?", """<p>Every painting is different, so it is impossible to give an exact timeline. The two main factors are how many commissions are ahead of yours and the size of the painting. A 30 × 40 in painting takes approximately 100 hours once the concept is agreed and paint starts going on the canvas. When it is complete, it takes 2–4 weeks to dry. That puts a 30 × 40 at roughly 4–6 weeks if no commissions are ahead of yours, not including shipping or delivery.</p>
<p>When the written contract is made, you will have an agreed completion date in writing, along with your options if the artist cannot meet the deadline.</p>
<p>In a time crunch, or need a gift sooner? For an extra charge you can get an original black-and-white graphite drawing of the planned painting to present with the promise of the painting to come.</p>"""),
       ("Who decides what is in the painting?", """<p>It’s a collaboration between you and the artist. The best works of art come from inspiration deep within the artist as they create; without it, the final piece would be missing that special something. That is why Scott reserves the right to turn down commissions that don’t inspire him.</p>
<p><em>“I won’t start a painting that I am not willing to hang in my living room when it is complete.”</em></p>
<p>Scott often works from several photographs to make a single painting. You can provide photos you took yourself or that aren’t under copyright. For example, if you’d like your wedding flowers painted from your professional photographer’s pictures, you’ll need the photographer’s written permission, even though you paid for the images.</p>
<p>Photos aren’t required, though. What flowers were at the wedding? What colors? Scott can compose a painting from that, and you’ll see the composition before any deposit. You can also choose from flower photographs Scott has taken himself, or just name your favorite color and let him find the flower to match.</p>"""),
       ("Why oil paint?", """<p>Oil paint has been the preferred medium of master artists for centuries, prized for its rich pigments, depth and longevity. It allows smooth blending and intricate detail, and its slow drying time lets the artist build layers and luminosity unmatched by other mediums. Many masterpieces from the Renaissance and beyond have survived for hundreds of years, their colors still vibrant. Properly cared for, an oil painting is a legacy that can be passed down for generations.</p>
<p>Scott’s paintings are typically touch-dry within 2–4 weeks, when a temporary protective retouch varnish can be applied before delivery. Oil paint can take 6 months to a year to dry fully; after that, a final varnish is recommended.</p>"""),
       ("Can I get a discount?", """<p>Unlike mass-reproduced art from big-box stores, original art is an investment: a one-of-a-kind work the artist puts their heart and soul into. There is no experience like standing in front of an original and seeing the texture of each brushstroke. A printer or a screen cannot recreate that, and as AI fills the world with mass-produced images, hand-made human art becomes even more valuable.</p>
<p>When you commission an original oil painting from me, I will put everything I have into it, and be just as passionate about it as you are. You’re not just buying a pretty picture; you’re buying the centerpiece of your space, an investment that won’t be discounted in the future.</p>""")]


def commissions():
    P = "../"
    A = "../../assets/"
    wf = BY["white-flowers"]
    canv = "".join(
        f'<div class="canvas"><div class="hangbox"><div class="piece" style="--w:{w};--h:{h}">{img(A, pic, "")}</div></div>'
        f'<span class="sz">{w} × {h} in</span><span class="pr">{p}</span></div>' for w, h, p, pic in PRICES)
    steps = "".join(f"<li><p>{s}</p></li>" for s in STEPS)
    faq = "".join(f'<details><summary>{q}<span class="pm" aria-hidden="true"></span></summary><div class="answer">{ans}</div></details>' for q, ans in FAQ)
    sizes = "".join(f"<option>{w} × {h} in</option>" for w, h in [(11, 14), (16, 20), (18, 24), (24, 36), (30, 40), (24, 48)])
    body = f"""<section class="wrap intro">
  <div class="fade">
    <p class="eyebrow">Commissions</p>
    <h1>A painting made <em>for you</em></h1>
    <p class="lead">There’s something timeless and deeply expressive about painting flowers. Each bloom carries its own personality: soft and delicate, bold and vibrant, fleeting yet full of life.</p>
    <p>I love capturing the way light dances on petals, the richness of color, and the quiet elegance that flowers bring to a space. With oil paint, I can build layers of texture and depth, creating pieces that feel almost alive. Painting flowers allows me to celebrate nature’s beauty in a way that lasts forever.</p>
    <div class="btn-row"><a class="btn solid" href="#start">Start a commission</a><a class="link" href="#prices">See prices {ARROW}</a></div>
  </div>
  <div class="lit"><div class="frame">{img(A, "white-flowers", wf["alt"], lazy=False, extra=' fetchpriority="high"')}</div></div>
</section>

<section class="section" aria-labelledby="msg-h">
  <div class="wrap">
    <div class="section-head fade">
      <div><p class="eyebrow">A hidden message</p><h2 id="msg-h">Words only <em>you know</em> are there</h2></div>
      <p>At first glance you would never see it, but can you see the words hidden within the texture of these paintings? Move the light across each one.</p>
    </div>
    <div class="reveal-pair">
      <div class="fade">
        {reveal(A, "yellow-flowers", "yellow-flowers-message", "lg", 58, "Slide to shine a light across Yellow Flowers and reveal the hidden message",
                "Yellow Flowers, the painting as it appears on the wall", "Yellow Flowers with the hidden words 'With love' and 'I love you' traced in red")}
        <div class="reveal-label"><span>Yellow Flowers</span><span class="hint">Drag the light</span></div>
      </div>
      <div class="fade">
        {reveal(A, "wild-radiance", "wild-radiance-message", "sm", 55, "Slide to shine a light across Wild Radiance and reveal the hidden message",
                "Wild Radiance, the painting as it appears on the wall", "Wild Radiance with its hidden message traced in red")}
        <div class="reveal-label"><span>Wild Radiance</span><span class="hint">Drag the light</span></div>
      </div>
    </div>
    <div class="section-head fade" style="margin:clamp(60px,8vw,100px) 0 0">
      <p style="color:var(--ink)">I presented <em>Yellow Flowers</em> to my wife on our wedding day, January 19th, 2002. To this day it is one of her most valuable possessions. Not only is it a beautiful oil painting to look at, it is a story: a message of love we have enjoyed for over 20 years.</p>
      <p>It is also a conversation piece. Jana loves to show it to people. She tells them it was a wedding gift I gave her on that special day, then asks if they can see the message. <strong style="color:var(--ink);font-weight:400">What message would you include in your commissioned painting? What would it mean to you? What story would it tell?</strong></p>
    </div>
  </div>
</section>

<section class="section" id="prices" aria-labelledby="prices-h">
  <div class="wrap">
    <div class="section-head fade">
      <div><p class="eyebrow">Sizes and prices</p><h2 id="prices-h">Choose your <em>canvas</em></h2></div>
      <p>Hung here to scale with each other, on one eye line, so you can picture each size on your own wall.</p>
    </div>
    <div class="scale-wall fade" role="list" aria-label="Commission sizes and prices">{canv.replace('<div class="canvas">', '<div class="canvas" role="listitem">')}</div>
    <p class="scale-note">Custom sizes are available. Ask Scott about the size you have in mind.</p>
  </div>
</section>

<section class="section" aria-labelledby="process-h">
  <div class="wrap">
    <div class="section-head fade">
      <div><p class="eyebrow">How it works</p><h2 id="process-h">The commission <em>process</em></h2></div>
      <p>Eight steps from first phone call to the day it goes on your wall. You see the composition before any deposit is paid.</p>
    </div>
    <ol class="steps fade">{steps}</ol>
  </div>
</section>

<section class="section" aria-labelledby="faq-h" style="padding-top:0">
  <div class="wrap">
    <div class="section-head fade"><div><p class="eyebrow">Questions</p><h2 id="faq-h">Good <em>to know</em></h2></div></div>
    <div class="faq">{faq}</div>
  </div>
</section>

<section class="section" id="start" aria-labelledby="start-h" style="padding-top:0">
  <div class="wrap form-wrap">
    <div class="fade">
      <p class="eyebrow">Let’s create art together</p>
      <h2 id="start-h">Start your <em>commission</em></h2>
      <p class="muted">Tell Scott a little about what you have in mind and he’ll be in touch.</p>
    </div>
    <form class="form" data-form="Commission inquiry">
      <div><label for="c-name">Your name *</label><input id="c-name" name="name" autocomplete="name" required></div>
      <div><label for="c-email">Your email *</label><input id="c-email" name="email" type="email" autocomplete="email" required></div>
      <div><label for="c-phone">Phone</label><input id="c-phone" name="phone" type="tel" autocomplete="tel"></div>
      <div><label for="c-size">Size</label><select id="c-size" name="size"><option value="">Not sure yet</option>{sizes}<option>Custom size</option></select></div>
      <div class="full"><label for="c-delivery">How you’ll receive it</label><select id="c-delivery" name="delivery"><option value="">Choose one</option><option>Pickup in Central Arkansas</option><option>Shipping in the USA</option><option>International shipping</option><option>Artist delivered</option></select></div>
      <div class="full"><label for="c-msg">Your vision *</label><textarea id="c-msg" name="message" required placeholder="What would you like painted? When do you need it? Is there a hidden message you'd like in it?"></textarea></div>
      <input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">
      <div class="full"><button class="btn solid" type="submit">Send to Scott</button>
        <p class="note">Your answers go to Scott by email through Formspree, a form service. They’re used only to reply to you about your commission.</p>
        <p class="form-status" role="status" aria-live="polite"></p></div>
    </form>
  </div>
</section>"""
    return page(P, "Commissions | Scott Beckman Art",
                "Commission an original oil painting by Scott Michael Beckman, with an optional hidden message only you know is there. Sizes, prices and the process.",
                body, current="commissions", og="yellow-flowers")


# ------------------------------------------------------------------ ABOUT
def about():
    P = "../"
    A = "../../assets/"
    body = f"""<section class="wrap about-hero">
  <div class="lit"><div class="frame">{img(A, "scott", "Portrait of Scott Beckman outdoors among trees", size="lg", lazy=False, extra=' fetchpriority="high"')}</div></div>
  <div class="fade">
    <p class="eyebrow">The artist</p>
    <h1>Scott Michael <em>Beckman</em></h1>
    <p class="lead">Born in Cincinnati, Ohio, and now living in Central Arkansas, Scott is a versatile oil painter whose work spans landscapes, animals, florals and portraits.</p>
  </div>
</section>
<section class="section" aria-label="Biography">
  <div class="wrap">
    <div class="bio fade">
      <p>With a deep passion for the expressive nature of oil painting, Scott’s work reflects both his artistic vision and his connection to the world around him.</p>
      <p>His artistic journey has been shaped by a variety of life experiences. He proudly served in the U.S. military and later became a registered nurse. During the Covid-19 pandemic, Scott traveled to some of Texas’ hardest-hit areas, working in the ICU caring for those most in need. These experiences left a lasting impact on his approach to both life and art.</p>
      <p>Scott has been married to his wife for 23 years and is the proud father of a son and daughter. His family remains a strong source of inspiration and support throughout his creative work.</p>
      <p>Through his art, Scott captures the beauty and complexity of the world, inviting viewers to appreciate the small and significant moments in life. Whether it’s the calm of a landscape, the strength and beauty of an animal, or the intimate details of a portrait, his paintings evoke emotion and invite reflection.</p>
    </div>
  </div>
</section>
<section class="section" aria-label="In his words" style="padding-top:0">
  <div class="wrap big-quote fade">
    <blockquote class="quote">“Art is my lifelong pursuit. Each new work is an opportunity to grow and challenge myself. I strive to make every painting the best I’ve ever done.”<cite>Scott Michael Beckman</cite></blockquote>
  </div>
</section>
<section class="section" aria-labelledby="follow-h" style="padding-top:0">
  <div class="wrap commission-cta fade">
    <div><p class="eyebrow">Follow along</p><h2 id="follow-h">New work and <em>painting videos</em></h2></div>
    {social()}
  </div>
</section>"""
    return page(P, "About | Scott Beckman Art",
                "About Scott Michael Beckman: oil painter in Central Arkansas, U.S. military veteran and registered nurse who painted his way through life's big moments.",
                body, current="about", og="scott")


# ------------------------------------------------------------------ CONTACT
def contact():
    P = "../"
    body = f"""<section class="wrap page-head form-wrap" style="padding-bottom:clamp(90px,12vw,170px)">
  <div class="fade">
    <p class="eyebrow">Contact</p>
    <h1>Write to <em>Scott</em></h1>
    <p class="lead muted">Questions about a painting, a commission, or just want to say hello? Scott would love to hear from you.</p>
    <p class="muted" style="margin-top:40px">Or find Scott here:</p>
    {social()}
    <p style="margin-top:40px"><a class="link" href="../commissions/#start">Commission details {ARROW}</a></p>
  </div>
  <div id="message">
    <form class="form" data-form="Message from scottbeckmanart.com" style="grid-template-columns:1fr">
      <div><label for="m-name">Your name *</label><input id="m-name" name="name" autocomplete="name" required></div>
      <div><label for="m-email">Your email *</label><input id="m-email" name="email" type="email" autocomplete="email" required></div>
      <div><label for="m-msg">Message *</label><textarea id="m-msg" name="message" required></textarea></div>
      <input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">
      <div><button class="btn solid" type="submit">Send message</button>
        <p class="note">Your name, email and message go to Scott by email through Formspree, a form service. They’re used only to reply to you.</p>
        <p class="form-status" role="status" aria-live="polite"></p></div>
    </form>
  </div>
</section>"""
    return page(P, "Contact | Scott Beckman Art",
                "Send Scott Michael Beckman a message about a painting, a commission, or just to say hello.",
                body, current="contact")


def write(rel, html):
    p = HERE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8", newline="\n")
    print("wrote", p.relative_to(SITE))


write("index.html", home())
write("work/index.html", work())
write("commissions/index.html", commissions())
write("about/index.html", about())
write("contact/index.html", contact())
