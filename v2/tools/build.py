"""Build the v2 "Studio Journal" pages from content/artworks.json.
Run: python v2/tools/build.py  (writes v2/index.html, v2/work/, v2/commissions/, v2/about/, v2/contact/)."""
import json
from html import escape
from pathlib import Path
from urllib.parse import quote

V2 = Path(__file__).resolve().parents[1]
ROOT = V2.parent
DATA = json.loads((ROOT / "content" / "artworks.json").read_text(encoding="utf-8"))
ARTS = DATA["artworks"]
BY = {a["slug"]: a for a in ARTS}
for i, a in enumerate(ARTS, 1):
    a["no"] = f"{i:02d}"
SIZES = json.loads((ROOT / "assets" / "img" / "sizes.json").read_text(encoding="utf-8"))


def e(s):
    return escape(s, quote=True)


def img_attrs(name, size="sm"):
    w, h = SIZES[name][size]
    return w, h


def meta(a):
    m = a.get("medium") or "Oil painting"
    s = f"{m} · {a['size']}"
    if a.get("available"):
        s += " · Available"
    return s


def pswp_link(a, A, inner="", name=None, cls="", hidden=False, extra=""):
    name = name or a["slug"]
    w, h = img_attrs(name, "lg")
    c = f' class="{cls}"' if cls else ""
    hid = " hidden" if hidden else ""
    return (f'<a{c} href="{A}img/{name}-lg.jpg" data-pswp-width="{w}" data-pswp-height="{h}" '
            f'data-title="{e(a["title"])}" data-meta="{e(meta(a))}"{extra}{hid}>{inner}</a>')


def img(name, A, alt, lazy=True, size="sm", extra=""):
    w, h = img_attrs(name, size)
    lz = ' loading="lazy" decoding="async"' if lazy else ""
    return f'<img src="{A}img/{name}-{size}.jpg" width="{w}" height="{h}" alt="{e(alt)}"{lz}{extra}>'


def own(name, P, alt, w, h, lazy=True, cls=""):
    lz = ' loading="lazy" decoding="async"' if lazy else ""
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{P}img/{name}.jpg" width="{w}" height="{h}" alt="{e(alt)}"{lz}>'


ICONS = {
    "Instagram": ("https://www.instagram.com/scottbeckmanart/", '<path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10Zm0 8.2A3.2 3.2 0 1 1 12 8.8a3.2 3.2 0 0 1 0 6.4ZM17.3 5.5a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4ZM21.9 7.1c-.1-1.6-.4-3-1.6-4.2S17.6 1.3 16 1.2C14.3 1.1 9.7 1.1 8 1.2c-1.6.1-3 .4-4.2 1.6S2.2 5.5 2.1 7.1C2 8.8 2 13.2 2.1 14.9c.1 1.6.4 3 1.6 4.2s2.6 1.5 4.2 1.6c1.7.1 6.3.1 8 0 1.6-.1 3-.4 4.2-1.6s1.5-2.6 1.6-4.2c.1-1.7.1-6.1.2-7.8Zm-2.2 9.9a3.3 3.3 0 0 1-1.8 1.8c-1.3.5-4.3.4-5.9.4s-4.6.1-5.9-.4A3.3 3.3 0 0 1 4.3 17c-.5-1.3-.4-4.3-.4-5.7s-.1-4.4.4-5.7A3.3 3.3 0 0 1 6.1 3.8C7.4 3.3 10.4 3.4 12 3.4s4.6-.1 5.9.4a3.3 3.3 0 0 1 1.8 1.8c.5 1.3.4 4.3.4 5.7s.1 4.4-.4 5.7Z"/>'),
    "YouTube": ("https://www.youtube.com/@paintingwithscott", '<path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8ZM9.8 15V9l5.8 3-5.8 3Z"/>'),
    "Facebook": ("https://www.facebook.com/profile.php?id=61572902832946", '<path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.4v7A10 10 0 0 0 22 12Z"/>'),
}


def social(cls="social"):
    items = "".join(
        f'<li><a href="{u}" rel="noopener" target="_blank"><svg viewBox="0 0 24 24" aria-hidden="true">{p}</svg>{n}</a></li>'
        for n, (u, p) in ICONS.items())
    return f'<ul class="{cls}" role="list" style="list-style:none;margin:0;padding:0">{items}</ul>'


def page(depth, current, title, desc, body, preload=""):
    P = "../" * depth          # to v2/
    A = P + "../assets/"       # to shared assets
    home = "./" if depth == 0 else P
    nav = "".join(
        f'<a href="{P}{slug}/"{" aria-current=\"page\"" if slug == current else ""}>{label}</a>'
        for slug, label in [("work", "Work"), ("commissions", "Commissions"), ("about", "About"), ("contact", "Contact")])
    body = body.replace("{P}", P).replace("{A}", A)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{A}img/wild-radiance-lg.jpg">
<meta property="og:type" content="website">
<meta name="theme-color" content="#e8e3d8">
<link rel="icon" href="{A}img/favicon.png">
<script>document.documentElement.classList.add("js")</script>
<link rel="preload" href="{P}fonts/fraunces-latin-full-normal.woff2" as="font" type="font/woff2" crossorigin>
{preload}<link rel="stylesheet" href="{P}css/journal.css">
<link rel="stylesheet" href="{A}vendor/photoswipe/photoswipe.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast"><div class="wrap mast__in">
<a class="brand" href="{home}"><span class="brand__name">Scott Beckman</span><span class="brand__tag">Oil paintings · Central Arkansas</span></a>
<nav class="nav" aria-label="Main">{nav}</nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="foot">
<div class="wrap">
<p class="kicker">Commissions</p>
<a class="foot__big" href="{P}commissions/#start">Have a story you’d like painted? <span>Start a commission →</span></a>
<div class="foot__grid">
<nav aria-label="Footer"><a href="{home}">Home</a><a href="{P}work/">Work</a><a href="{P}commissions/">Commissions</a><a href="{P}about/">About</a><a href="{P}contact/">Contact</a></nav>
{social()}
</div>
</div>
<p class="foot__mark" aria-hidden="true">Scott Beckman</p>
<div class="wrap foot__legal"><small>© <span data-year>2026</span> Scott Michael Beckman. All paintings and images are the artist’s own; please ask before reusing them.</small></div>
</footer>
<script src="{A}js/site.js" defer></script>
<script src="{P}js/journal.js" defer></script>
<script type="module" src="{A}js/gallery.js"></script>
</body>
</html>
"""


def reveal(A, base, top, alt_base, alt_top, label, pos, size="lg", labels=("The painting", "The hidden message")):
    w, h = img_attrs(base, size)

    def ss(n):
        if size != "lg":
            return ""
        return f' srcset="{A}img/{n}-sm.jpg {SIZES[n]["sm"][0]}w, {A}img/{n}-lg.jpg {SIZES[n]["lg"][0]}w" sizes="(min-width: 960px) 60vw, 100vw"'
    return f"""<div class="reveal" style="--pos:{pos}%">
<img src="{A}img/{base}-{size}.jpg"{ss(base)} width="{w}" height="{h}" alt="{e(alt_base)}" loading="lazy" decoding="async">
<div class="top"><img src="{A}img/{top}-{size}.jpg"{ss(top)} width="{w}" height="{h}" alt="{e(alt_top)}" loading="lazy" decoding="async"></div>
<input type="range" min="0" max="100" value="{pos}" aria-label="{e(label)}">
<div class="handle"></div>
</div>
<div class="reveal-label" aria-hidden="true"><span>← {labels[0]}</span><span>{labels[1]} →</span></div>"""


# ------------------------------------------------------------------ HOME
def home():
    A = "{A}"
    wr = BY["wild-radiance"]

    def plate(slug, cls, drift):
        a = BY[slug]
        inner = img(slug, A, a["alt"])
        d = f' data-drift="{drift}"' if drift else ""
        return (f'<figure class="pl {cls}"{d}><span class="num" aria-hidden="true">{a["no"]}</span>'
                f'<div class="wipe">{pswp_link(a, A, inner)}</div>'
                f'<figcaption class="cap"><span class="cap__no">No. {a["no"]}</span><em>{e(a["title"])}</em>, {a["size"]}</figcaption></figure>')

    def original(slug, rev):
        a = BY[slug]
        main_name, inset_name = {"old-barn": ("old-barn-2", "old-barn-frame"),
                                 "yellow-house": ("yellow-house-3", "yellow-house-frame")}[slug]
        main = pswp_link(a, A, img(main_name, A, f"{a['title']} in the oak frame Scott made for it"), name=main_name, cls="orig__main")
        inset = pswp_link(a, A, img(inset_name, A, f"Side view of the handmade oak frame on {a['title']}"),
                          name=inset_name, cls="orig__inset", extra=' data-drift="-0.06"')
        rest = "".join(pswp_link(a, A, name=n, hidden=True) for n in [slug] + a["photos"] if n not in (main_name, inset_name))
        medium = a["medium"]
        return f"""<article class="orig wrap{' orig--rev' if rev else ''}{' orig--tall' if SIZES[main_name]['sm'][1] > SIZES[main_name]['sm'][0] else ''}">
<div class="orig__media wipe" data-gallery>{main}{inset}{rest}</div>
<div class="orig__text rise">
<p class="cap"><span class="cap__no">No. {a['no']}</span>Available original</p>
<h3>{e(a['title'])}</h3>
<dl class="specs"><div><dt>Medium</dt><dd>{e(medium)}</dd></div><div><dt>Size</dt><dd>{a['size']}</dd></div><div><dt>Frame</dt><dd>{e(a['frame'])}</dd></div></dl>
<p class="status">Available, ask about it</p><br>
<a class="go" href="{{P}}contact/?painting={quote(a['title'])}#message">Ask about this painting</a>
</div>
</article>"""

    body = f"""<section class="hero wrap" aria-labelledby="hero-h">
<p class="hero__kicker kicker"><span>Studio Journal</span><span>Original oil paintings by Scott Michael Beckman</span></p>
<h1 id="hero-h" class="hero__title">
<span class="line wipe">Paintings that</span>
<span class="line wipe" style="--d:.14s">hold <em class="paint">light,</em></span>
<span class="line wipe" style="--d:.28s">texture &amp;</span>
<span class="line wipe" style="--d:.42s">a story.</span>
</h1>
<div class="hero__art">
<div class="frame">
<div class="wipe wipe--slow" style="--d:.2s" data-gallery>{pswp_link(wr, A, img('wild-radiance', A, wr['alt'], lazy=False, extra=' fetchpriority="high"'))}</div>
<figure class="inset" data-drift="-0.1">
<div class="wipe" style="--d:.7s">{own('detail-radiance-petal-sm', '{P}', 'Close-up of a purple anemone petal from Wild Radiance, showing the swirling brushstrokes', 800, 750, lazy=False)}</div>
<figcaption class="cap">Detail</figcaption>
</figure>
</div>
<p class="cap"><span class="cap__no">Fig. 1</span><em>Wild Radiance</em>, {wr['size']}, oil painting</p>
</div>
<div class="hero__lead rise" style="--d:.5s">
<p class="dropcap">Scott Michael Beckman paints flowers, animals, landscapes and people in oil, building every canvas layer by layer until it feels alive. Some even carry a hidden message.</p>
<p class="links"><a class="go" href="{{P}}work/">See the paintings</a><a class="go" href="{{P}}commissions/">Commission a painting</a></p>
</div>
<p class="hero__side" aria-hidden="true">Central Arkansas — Oil on canvas</p>
</section>

<section aria-labelledby="sel-h">
<header class="opener wrap">
<span class="opener__num" aria-hidden="true">01</span>
<p class="kicker">Selected work</p>
<h2 id="sel-h" class="wipe">From the studio</h2>
</header>
<div class="spread__grid wrap" data-gallery>
{plate('yellow-flowers', 'pl--a', '')}
{plate('pig', 'pl--b', '0.06')}
<p class="statement rise">Layer by layer, <b>until it feels alive.</b></p>
{plate('majestic-horse', 'pl--c', '')}
{plate('white-flowers', 'pl--d', '-0.05')}
{plate('old-barn', 'pl--e', '0.05')}
{plate('purple-flowers', 'pl--f pl--wide', '')}
</div>
<div class="wrap more"><a class="go" href="{{P}}work/">All {len(ARTS)} paintings</a></div>
</section>

<section class="closeup wrap" aria-labelledby="close-h">
<div class="closeup__head">
<p class="kicker">Up close</p>
<h2 id="close-h" class="wipe">The brushwork, <em>at arm’s length</em></h2>
</div>
<div class="closeup__row">
<figure data-drift="0.05"><div class="wipe">{own('detail-horse-eye-sm', '{P}', 'Close-up of the eye in Majestic Horse', 800, 633)}</div><figcaption class="cap"><em>Majestic Horse</em>, detail</figcaption></figure>
<figure data-drift="-0.04"><div class="wipe" style="--d:.12s">{own('detail-yellow-bloom-sm', '{P}', 'Close-up of a yellow coreopsis bloom in Yellow Flowers', 800, 663)}</div><figcaption class="cap"><em>Yellow Flowers</em>, detail</figcaption></figure>
<figure data-drift="0.07"><div class="wipe" style="--d:.24s">{own('detail-pig-sm', '{P}', 'Close-up of the snout in Pig', 800, 686)}</div><figcaption class="cap"><em>Pig</em>, detail</figcaption></figure>
<figure data-drift="-0.02"><div class="wipe" style="--d:.36s">{own('detail-dogwood-sm', '{P}', 'Close-up of a dogwood blossom in White Flowers', 800, 583)}</div><figcaption class="cap"><em>White Flowers</em>, detail</figcaption></figure>
</div>
</section>

<section class="secret" aria-labelledby="secret-h">
<div class="wrap secret__grid">
<div class="secret__text">
<span class="opener__num" aria-hidden="true">02</span>
<p class="kicker">A hidden message</p>
<h2 id="secret-h" class="wipe">Can you see the <em>words</em> in the paint?</h2>
<p class="secret__date rise" aria-label="January 19, 2002"><span>01</span><span>19</span><span>2002</span></p>
<p>Scott gave <em>Yellow Flowers</em> to his wife Jana on their wedding day, January 19, 2002. Hidden in the texture of the petals and background is a message only they knew was there. More than twenty years later, it’s still the piece she loves showing people most.</p>
<p class="hint">Drag across the painting to wipe back the paint.</p>
<a class="go go--light" href="{{P}}commissions/">Put your own message in a painting</a>
</div>
<figure class="secret__art" style="margin:0">
{reveal(A, 'yellow-flowers', 'yellow-flowers-message', 'Yellow Flowers, the painting as it appears on the wall', "Yellow Flowers with the hidden words 'With love' and 'I love you' traced in red", 'Slide to reveal the hidden message', 62)}
</figure>
</div>
</section>

<section id="available" aria-labelledby="avail-h">
<header class="opener wrap">
<span class="opener__num" aria-hidden="true">03</span>
<p class="kicker">Available originals</p>
<h2 id="avail-h" class="wipe">Ready to hang, in frames Scott built by hand</h2>
<p class="lead">Scott mills the oak for his frames from trees on his own land, so the frame is as one-of-a-kind as the painting.</p>
</header>
{original('old-barn', False)}
{original('yellow-house', True)}
</section>

<section class="studio" aria-labelledby="studio-h">
<div class="studio__texture"><img src="{{P}}img/brush.jpg" width="1440" height="992" alt="" loading="lazy" decoding="async" data-drift="0.08"></div>
<div class="wrap studio__grid">
<figure class="studio__portrait wipe">{img('scott', A, 'Portrait of Scott Beckman outdoors among trees')}</figure>
<blockquote class="bigquote"><p>“Art is my lifelong pursuit. Each new work is an opportunity to grow and challenge myself. I strive to make every painting the best I’ve ever done.”</p><footer>Scott Michael Beckman</footer></blockquote>
<div class="studio__text rise">
<p class="kicker" id="studio-h">04 — About the artist</p>
<p>Born in Cincinnati and now living in Central Arkansas, Scott is a U.S. military veteran and registered nurse who worked in Texas ICUs during the Covid-19 pandemic. Those years shape how he paints: patiently, and with an eye for the small moments that matter.</p>
<a class="go" href="{{P}}about/">Read Scott’s story</a>
</div>
</div>
</section>"""
    return page(0, "", "Scott Beckman Art | Original Oil Paintings",
                "Original oil paintings by Scott Michael Beckman: florals, animals, landscapes and portraits, painted in Central Arkansas. Commissions welcome.",
                body, preload='<link rel="preload" href="../assets/img/wild-radiance-sm.jpg" as="image">\n')


# ------------------------------------------------------------------ WORK
def work():
    A = "{A}"
    counts = {}
    for a in ARTS:
        counts[a["subject"]] = counts.get(a["subject"], 0) + 1
    avail = sum(1 for a in ARTS if a.get("available"))
    btns = [f'<button type="button" data-filter="all" aria-pressed="true">All<sup>{len(ARTS)}</sup></button>']
    for s in ["florals", "animals", "landscapes", "portraits"]:
        if s in counts:
            btns.append(f'<button type="button" data-filter="{s}" aria-pressed="false">{s.title()}<sup>{counts[s]}</sup></button>')
    btns.append(f'<button type="button" data-filter="available" aria-pressed="false">Available<sup>{avail}</sup></button>')
    figs = []
    for a in ARTS:
        w, h = SIZES[a["slug"]]["sm"]
        shape = "is-port" if h > w * 1.05 else ("is-land" if w > h * 1.05 else "is-sq")
        av = " data-available" if a.get("available") else ""
        badge = '<span class="badge">Available</span>' if a.get("available") else ""
        inner = badge + img(a["slug"], A, a["alt"])
        figs.append(f'<figure class="art {shape}" data-subject="{a["subject"]}"{av}><div class="wipe">{pswp_link(a, A, inner)}</div>'
                    f'<figcaption><span class="no" aria-hidden="true">{a["no"]}</span><span class="t">{e(a["title"])}</span>'
                    f'<span class="m">{a["size"]} · {a["subject"].rstrip("s").title() if a["subject"] != "florals" else "Floral"}</span></figcaption></figure>')
    body = f"""<section class="page-top wrap" aria-labelledby="work-h">
<p class="kicker">The work · {len(ARTS)} paintings in oil</p>
<h1 id="work-h"><span class="line wipe">The</span><span class="line indent wipe" style="--d:.15s"><em>Work</em></span></h1>
<div class="page-top__body rise" style="--d:.4s"><p class="lead">Florals, animals, landscapes and portraits, painted in Central Arkansas. Tap any painting to see it large.</p></div>
<div class="page-top__img"><div class="frame"><div class="wipe wipe--slow" style="--d:.2s">{own('detail-horse-eye', '{P}', 'Close-up of the eye in Majestic Horse', 1200, 950, lazy=False)}</div></div><p class="cap">Detail, <em>Majestic Horse</em></p></div>
</section>
<section class="wrap" aria-label="All paintings">
<div class="filters" role="group" aria-label="Show paintings by subject">{''.join(btns)}</div>
<div class="gallery" data-gallery>
{chr(10).join(figs)}
</div>
</section>"""
    return page(1, "work", "The Work | Scott Beckman Art",
                "All of Scott Michael Beckman's oil paintings: florals, animals, landscapes and portraits, with sizes. Two originals are available.", body)


# ------------------------------------------------------------------ COMMISSIONS
PRICES = [("11 × 14 in", 11, 14, "$900"), ("16 × 20 in", 16, 20, "$1,800"), ("18 × 24 in", 18, 24, "$2,450"),
          ("24 × 36 in", 24, 36, "$4,850"), ("24 × 48 in", 24, 48, "$6,500"), ("30 × 40 in", 30, 40, "$6,750")]
STEPS = ["Phone consultation with the artist.",
         "Verbal agreement on subject, size and price.",
         "The artist designs a digital composition and presents it to you.",
         "If you both decide to go forward, a written contract is signed by both.",
         "You pay 50% up front, before the physical painting begins.",
         "The artist completes the painting.",
         "You pay the remaining 50% and receive your finished painting.",
         "You hang it somewhere visible, with bragging rights to an original Scott Beckman oil painting."]


def commissions():
    A = "{A}"
    wall = "".join(
        f'<div class="canvas-item"><div class="cv" style="--w:{w};--h:{h}" aria-hidden="true"></div><span class="size">{s}</span><span class="amt">{p}</span></div>'
        for s, w, h, p in PRICES)
    steps = "".join(
        f'<li style="--d:{i * 0.07:.2f}s"><span class="n" aria-hidden="true"><span class="o">{i + 1:02d}</span><span class="f">{i + 1:02d}</span></span><p><span class="sr">Step {i + 1}: </span>{t}</p></li>'
        for i, t in enumerate(STEPS))
    wf = BY["white-flowers"]
    body = f"""<section class="page-top wrap" aria-labelledby="com-h">
<p class="kicker">Commissions</p>
<h1 id="com-h"><span class="line wipe">A floral</span><span class="line indent wipe" style="--d:.14s">painting,</span><span class="line wipe" style="--d:.28s"><em>made for you.</em></span></h1>
<div class="page-top__body rise" style="--d:.4s">
<p class="lead">There’s something timeless and deeply expressive about painting flowers. Each bloom carries its own personality: soft and delicate, bold and vibrant, fleeting yet full of life.</p>
<p>I love capturing the way light dances on petals, the richness of color, and the quiet elegance that flowers bring to a space. With oil paint, I can build layers of texture and depth, creating pieces that feel almost alive. Painting flowers allows me to celebrate nature’s beauty in a way that lasts forever.</p>
<p class="links"><a class="go" href="#start">Start a commission</a><a class="go" href="#prices">See prices</a></p>
</div>
<div class="page-top__img"><div class="frame"><div class="wipe wipe--slow" style="--d:.2s" data-gallery>{pswp_link(wf, A, img('white-flowers', A, wf['alt'], lazy=False))}</div>
<figure class="inset" data-drift="-0.1"><div class="wipe" style="--d:.7s">{own('detail-dogwood-sm', '{P}', 'Close-up of a dogwood blossom from White Flowers', 800, 583)}</div><figcaption class="cap">Detail</figcaption></figure></div>
<p class="cap"><span class="cap__no">No. {wf['no']}</span><em>White Flowers</em>, {wf['size']}</p></div>
</section>

<section class="secret secret--pair" aria-labelledby="hm-h" style="margin-top:0">
<div class="wrap secret__grid">
<div class="secret__text">
<p class="kicker">A hidden message</p>
<h2 id="hm-h" class="wipe">Words only <em>you</em> know are there</h2>
<div class="cols" style="margin-top:2.4rem">
<p>At first glance you would never see it, but can you see the words hidden within the texture of these paintings? I presented <em>Yellow Flowers</em> to my wife on our wedding day, January 19th, 2002. To this day it is one of her most valuable possessions. Not only is it a beautiful oil painting to look at, it is a story: a message of love we have enjoyed for over 20 years.</p>
<p>It is also a conversation piece. Jana loves to show it to people. She tells them it was a wedding gift I gave her on that special day, then asks if they can see the message.</p>
</div>
<p class="ask rise">What message would you include in your commissioned painting? <b>What would it mean to you? What story would it tell?</b></p>
<p class="hint" style="margin-top:2rem">Drag across each painting to wipe back the paint.</p>
</div>
<div class="pair">
<figure style="margin:0">{reveal(A, 'yellow-flowers', 'yellow-flowers-message', 'Yellow Flowers, the painting as it appears on the wall', "Yellow Flowers with the hidden words 'With love' and 'I love you' traced in red", 'Slide to reveal the hidden message in Yellow Flowers', 60, labels=('Yellow Flowers', 'Hidden message'))}</figure>
<figure style="margin:0">{reveal(A, 'wild-radiance', 'wild-radiance-message', 'Wild Radiance, the painting as it appears on the wall', 'Wild Radiance with its hidden message traced in red', 'Slide to reveal the hidden message in Wild Radiance', 55, size='sm', labels=('Wild Radiance', 'Hidden message'))}</figure>
</div>
</div>
</section>

<section id="prices" aria-labelledby="price-h">
<header class="opener wrap">
<span class="opener__num" aria-hidden="true">$</span>
<p class="kicker">Sizes and prices</p>
<h2 id="price-h" class="wipe">Six canvases, drawn to scale</h2>
</header>
<div class="wrap">
<div class="wall rise">{wall}</div>
<p class="wall-note">The little canvases are drawn to scale with each other. Custom sizes are available.</p>
</div>
</section>

<section aria-labelledby="proc-h">
<header class="opener wrap">
<span class="opener__num" aria-hidden="true">8</span>
<p class="kicker">How it works</p>
<h2 id="proc-h" class="wipe">The commission process</h2>
</header>
<div class="wrap"><ol class="steps">{steps}</ol></div>
</section>

<section class="faq" aria-labelledby="faq-h">
<header class="opener wrap">
<span class="opener__num" aria-hidden="true">?</span>
<p class="kicker">Questions</p>
<h2 id="faq-h" class="wipe">Good to know</h2>
</header>
<div class="wrap">
<details>
<summary>How long does it take?</summary>
<div class="answer">
<p>Every painting is different, so it is impossible to give an exact timeline. The two main factors are how many commissions are ahead of yours and the size of the painting. A 30 × 40 in painting takes approximately 100 hours once the concept is agreed and paint starts going on the canvas. When it is complete, it takes 2–4 weeks to dry. That puts a 30 × 40 at roughly 4–6 weeks if no commissions are ahead of yours, not including shipping or delivery.</p>
<p>When the written contract is made, you will have an agreed completion date in writing, along with your options if the artist cannot meet the deadline.</p>
<p>In a time crunch, or need a gift sooner? For an extra charge you can get an original black-and-white graphite drawing of the planned painting to present with the promise of the painting to come.</p>
</div>
</details>
<details>
<summary>Who decides what is in the painting?</summary>
<div class="answer">
<p>It’s a collaboration between you and the artist. The best works of art come from inspiration deep within the artist as they create; without it, the final piece would be missing that special something. That is why Scott reserves the right to turn down commissions that don’t inspire him.</p>
<p><em>“I won’t start a painting that I am not willing to hang in my living room when it is complete.”</em></p>
<p>Scott often works from several photographs to make a single painting. You can provide photos you took yourself or that aren’t under copyright. For example, if you’d like your wedding flowers painted from your professional photographer’s pictures, you’ll need the photographer’s written permission, even though you paid for the images.</p>
<p>Photos aren’t required, though. What flowers were at the wedding? What colors? Scott can compose a painting from that, and you’ll see the composition before any deposit. You can also choose from flower photographs Scott has taken himself, or just name your favorite color and let him find the flower to match.</p>
</div>
</details>
<details>
<summary>Why oil paint?</summary>
<div class="answer">
<p>Oil paint has been the preferred medium of master artists for centuries, prized for its rich pigments, depth and longevity. It allows smooth blending and intricate detail, and its slow drying time lets the artist build layers and luminosity unmatched by other mediums. Many masterpieces from the Renaissance and beyond have survived for hundreds of years, their colors still vibrant. Properly cared for, an oil painting is a legacy that can be passed down for generations.</p>
<p>Scott’s paintings are typically touch-dry within 2–4 weeks, when a temporary protective retouch varnish can be applied before delivery. Oil paint can take 6 months to a year to dry fully; after that, a final varnish is recommended.</p>
</div>
</details>
<details>
<summary>Can I get a discount?</summary>
<div class="answer">
<p>Unlike mass-reproduced art from big-box stores, original art is an investment: a one-of-a-kind work the artist puts their heart and soul into. There is no experience like standing in front of an original and seeing the texture of each brushstroke. A printer or a screen cannot recreate that, and as AI fills the world with mass-produced images, hand-made human art becomes even more valuable.</p>
<p>When you commission an original oil painting from me, I will put everything I have into it, and be just as passionate about it as you are. You’re not just buying a pretty picture; you’re buying the centerpiece of your space, an investment that won’t be discounted in the future.</p>
</div>
</details>
</div>
</section>

<section id="start" aria-labelledby="start-h">
<div style="height:clamp(80px,10vw,150px)"></div>
<div class="wrap form-wrap">
<header>
<p class="kicker">Let’s create art together</p>
<h2 id="start-h" class="wipe">Start your commission</h2>
<p class="lead" style="margin-top:1.6rem">Tell Scott a little about what you have in mind and he’ll be in touch.</p>
</header>
<form class="form two" data-form="Commission inquiry">
<div><label for="c-name">Your name *</label><input id="c-name" name="name" autocomplete="name" required></div>
<div><label for="c-email">Your email *</label><input id="c-email" name="email" type="email" autocomplete="email" required></div>
<div><label for="c-phone">Phone</label><input id="c-phone" name="phone" type="tel" autocomplete="tel"></div>
<div><label for="c-size">Size</label>
<select id="c-size" name="size"><option value="">Not sure yet</option><option>11 × 14 in</option><option>16 × 20 in</option><option>18 × 24 in</option><option>24 × 36 in</option><option>30 × 40 in</option><option>24 × 48 in</option><option>Custom size</option></select></div>
<div class="full"><label for="c-delivery">How you’ll receive it</label>
<select id="c-delivery" name="delivery"><option value="">Choose one</option><option>Pickup in Central Arkansas</option><option>Shipping in the USA</option><option>International shipping</option><option>Artist delivered</option></select></div>
<div class="full"><label for="c-msg">Your vision *</label><textarea id="c-msg" name="message" required placeholder="What would you like painted? When do you need it? Is there a hidden message you'd like in it?"></textarea></div>
<input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">
<div class="full"><button class="btn" type="submit">Send to Scott</button>
<p class="note">Your answers go to Scott by email through Formspree, a form service. They’re used only to reply to you about your commission.</p>
<p class="form-status" role="status" aria-live="polite"></p></div>
</form>
</div>
</section>"""
    return page(1, "commissions", "Commissions | Scott Beckman Art",
                "Commission an original oil painting from Scott Michael Beckman, with an optional hidden message. Prices from $900, the 8-step process and answers to common questions.", body)


# ------------------------------------------------------------------ ABOUT
def about():
    A = "{A}"
    body = f"""<section class="page-top wrap" aria-labelledby="about-h">
<p class="kicker">About · Oil painter, Central Arkansas</p>
<h1 id="about-h"><span class="line wipe">Scott</span><span class="line indent wipe" style="--d:.14s"><em>Michael</em></span><span class="line wipe" style="--d:.28s">Beckman</span></h1>
<div class="page-top__body rise" style="--d:.4s"><p class="lead dropcap">Born in Cincinnati, Ohio, and now living in Central Arkansas, Scott Michael Beckman is a versatile artist whose work spans landscapes, animals, florals and portraits.</p></div>
<div class="page-top__img"><div class="frame"><div class="wipe wipe--slow" style="--d:.2s">{img('scott', A, 'Portrait of Scott Beckman outdoors among trees', lazy=False, size='lg')}</div>
<figure class="inset" data-drift="-0.1"><div class="wipe" style="--d:.7s">{own('detail-yellow-bloom-sm', '{P}', 'Close-up of a yellow coreopsis bloom from Yellow Flowers', 800, 663)}</div><figcaption class="cap">Detail, <em>Yellow Flowers</em></figcaption></figure></div></div>
</section>

<section class="wrap bio" aria-label="Biography">
<div class="bio__cols rise">
<p>With a deep passion for the expressive nature of oil painting, Scott’s work reflects both his artistic vision and his connection to the world around him.</p>
<p>His artistic journey has been shaped by a variety of life experiences. He proudly served in the U.S. military and later became a registered nurse. During the Covid-19 pandemic, Scott traveled to some of Texas’ hardest-hit areas, working in the ICU caring for those most in need. These experiences left a lasting impact on his approach to both life and art.</p>
<p>Scott has been married to his wife for 23 years and is the proud father of a son and daughter. His family remains a strong source of inspiration and support throughout his creative work.</p>
<p>Through his art, Scott captures the beauty and complexity of the world, inviting viewers to appreciate the small and significant moments in life. Whether it’s the calm of a landscape, the strength and beauty of an animal, or the intimate details of a portrait, his paintings evoke emotion and invite reflection.</p>
</div>
<dl class="facts rise" style="--d:.15s">
<div><dt>Born</dt><dd>Cincinnati, Ohio</dd></div>
<div><dt>Studio</dt><dd>Central Arkansas</dd></div>
<div><dt>Served</dt><dd>U.S. military</dd></div>
<div><dt>Nursed</dt><dd>Texas ICUs, Covid-19 pandemic</dd></div>
<div><dt>Paints</dt><dd>Landscapes, animals, florals, portraits</dd></div>
<div><dt>Medium</dt><dd>Oil</dd></div>
</dl>
</section>

<section class="quote-band" aria-label="In his words">
<div class="wrap"><blockquote class="bigquote wipe"><p>“Art is my lifelong pursuit. Each new work is an opportunity to grow and challenge myself. I strive to make every painting the best I’ve ever done.”</p><footer>Scott Michael Beckman</footer></blockquote></div>
<div class="quote-band__tex"><img src="{{P}}img/brush.jpg" width="1440" height="992" alt="" loading="lazy" decoding="async"></div>
</section>

<section class="wrap follow" aria-labelledby="follow-h">
<p class="kicker">Follow along</p>
<h2 id="follow-h" class="wipe">New work and painting videos</h2>
{social('social social--ink')}
</section>"""
    return page(1, "about", "About Scott Michael Beckman | Scott Beckman Art",
                "Scott Michael Beckman is an oil painter in Central Arkansas: a U.S. military veteran and registered nurse who paints landscapes, animals, florals and portraits.", body)


# ------------------------------------------------------------------ CONTACT
def contact():
    body = f"""<section class="page-top wrap" aria-labelledby="contact-h">
<p class="kicker">Contact</p>
<h1 id="contact-h"><span class="line wipe">Write to</span><span class="line indent wipe" style="--d:.14s"><em>Scott.</em></span></h1>
<div class="page-top__body rise" style="--d:.4s">
<p class="lead">Questions about a painting, a commission, or just want to say hello? Scott would love to hear from you.</p>
<p class="kicker" style="margin-top:2.4rem">Or find Scott here</p>
{social('social social--ink')}
<p style="margin-top:2rem">Thinking about a painting made just for you? <a class="go" href="{{P}}commissions/#start">Commission details</a></p>
</div>
<div class="page-top__img"><div class="frame"><div class="wipe wipe--slow" style="--d:.2s">{own('detail-pig', '{P}', 'Close-up of the snout in the painting Pig', 1200, 1029, lazy=False)}</div></div><p class="cap">Detail, <em>Pig</em></p></div>
</section>
<section id="message" class="wrap form-wrap" aria-labelledby="msg-h">
<header><p class="kicker">Message</p><h2 id="msg-h" class="wipe">Send Scott a message</h2></header>
<form class="form" data-form="Message from scottbeckmanart.com">
<div><label for="m-name">Your name *</label><input id="m-name" name="name" autocomplete="name" required></div>
<div><label for="m-email">Your email *</label><input id="m-email" name="email" type="email" autocomplete="email" required></div>
<div><label for="m-msg">Message *</label><textarea id="m-msg" name="message" required></textarea></div>
<input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">
<div><button class="btn" type="submit">Send message</button>
<p class="note">Your name, email and message go to Scott by email through Formspree, a form service. They’re used only to reply to you.</p>
<p class="form-status" role="status" aria-live="polite"></p></div>
</form>
</section>"""
    return page(1, "contact", "Contact | Scott Beckman Art",
                "Send Scott Michael Beckman a message about a painting, a commission, or just to say hello.", body)


def write(rel, html):
    p = V2 / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    print("wrote", rel, len(html))


write("index.html", home())
write("work/index.html", work())
write("commissions/index.html", commissions())
write("about/index.html", about())
write("contact/index.html", contact())
