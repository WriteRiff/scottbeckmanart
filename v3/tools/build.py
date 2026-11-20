"""Builds the five pages of look v3 ("Color Field") from content/artworks.json and tools/colors.json.

Run:  python v3/tools/colors.py   (only when paintings change)
      python v3/tools/build.py
Writes only inside v3/.
"""
import html
import json
from pathlib import Path

V3 = Path(__file__).resolve().parents[1]
ROOT = V3.parent
ART = json.loads((ROOT / "content" / "artworks.json").read_text(encoding="utf-8"))["artworks"]
SIZES = json.loads((ROOT / "assets" / "img" / "sizes.json").read_text(encoding="utf-8"))
COL = json.loads((V3 / "tools" / "colors.json").read_text(encoding="utf-8"))
BY = {a["slug"]: a for a in ART}
E = lambda s: html.escape(s, quote=True)
SUBJECTS = [("florals", "Florals"), ("animals", "Animals"), ("landscapes", "Landscapes"), ("portraits", "Portraits")]
ARR = '<span class="arr" aria-hidden="true">&rarr;</span>'

ICONS = {
    "Instagram": '<path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10Zm0 8.2A3.2 3.2 0 1 1 12 8.8a3.2 3.2 0 0 1 0 6.4ZM17.3 5.5a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4ZM21.9 7.1c-.1-1.6-.4-3-1.6-4.2S17.6 1.3 16 1.2C14.3 1.1 9.7 1.1 8 1.2c-1.6.1-3 .4-4.2 1.6S2.2 5.5 2.1 7.1C2 8.8 2 13.2 2.1 14.9c.1 1.6.4 3 1.6 4.2s2.6 1.5 4.2 1.6c1.7.1 6.3.1 8 0 1.6-.1 3-.4 4.2-1.6s1.5-2.6 1.6-4.2c.1-1.7.1-6.1.2-7.8Zm-2.2 9.9a3.3 3.3 0 0 1-1.8 1.8c-1.3.5-4.3.4-5.9.4s-4.6.1-5.9-.4A3.3 3.3 0 0 1 4.3 17c-.5-1.3-.4-4.3-.4-5.7s-.1-4.4.4-5.7A3.3 3.3 0 0 1 6.1 3.8C7.4 3.3 10.4 3.4 12 3.4s4.6-.1 5.9.4a3.3 3.3 0 0 1 1.8 1.8c.5 1.3.4 4.3.4 5.7s.1 4.4-.4 5.7Z"/>',
    "YouTube": '<path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8ZM9.8 15V9l5.8 3-5.8 3Z"/>',
    "Facebook": '<path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.4v7A10 10 0 0 0 22 12Z"/>',
}
LINKS = [("Instagram", "https://www.instagram.com/scottbeckmanart/"),
         ("YouTube", "https://www.youtube.com/@paintingwithscott"),
         ("Facebook", "https://www.facebook.com/profile.php?id=61572902832946")]


def social():
    return '<div class="social">' + "".join(
        f'<a href="{u}" rel="noopener" target="_blank"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[n]}</svg>{n}</a>'
        for n, u in LINKS) + "</div>"


def img(A, slug, alt, size="sm", lazy=True, sizes=None, cls="", extra=""):
    w, h = SIZES[slug]["sm"]
    srcset = ""
    if sizes:
        lw = SIZES[slug]["lg"][0]
        srcset = f' srcset="{A}img/{slug}-sm.jpg 900w, {A}img/{slug}-lg.jpg {lw}w" sizes="{sizes}"'
    load = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{A}img/{slug}-{size}.jpg"{srcset} width="{w}" height="{h}" alt="{E(alt)}"{load}{c}{extra}>'


def pswp(A, slug, title, meta, inner="", hidden=False, cls=""):
    lw, lh = SIZES[slug]["lg"]
    c = f' class="{cls}"' if cls else ""
    hid = " hidden" if hidden else ""
    return (f'<a href="{A}img/{slug}-lg.jpg" data-pswp-width="{lw}" data-pswp-height="{lh}" '
            f'data-title="{E(title)}" data-meta="{E(meta)}"{c}{hid}>{inner}</a>')


def chips(slug, cls="chips pop"):
    return f'<ul class="{cls}" aria-hidden="true">' + "".join(
        f'<li style="--c:{c};--i:{i}"></li>' for i, c in enumerate(COL[slug]["chips"])) + "</ul>"


def meta_of(a):
    m = (a.get("medium") or "Oil painting") + " · " + a["size"]
    return m + (" · Available" if a.get("available") else "")


def desc_of(a):
    d = a["alt"]
    for p in ("Oil painting of ", "Oil painting "):
        if d.startswith(p):
            d = d[len(p):]
    return d[0].upper() + d[1:] + "."


def page(P, title, desc, body, current="", og="wild-radiance"):
    A = P + "../assets/"
    nav = "".join(
        f'<a href="{P}{h}/"{" aria-current=\"page\"" if current == h else ""}>{n}</a>'
        for h, n in [("work", "Work"), ("commissions", "Commissions"), ("about", "About"), ("contact", "Contact")])
    dots = "".join(f'<span style="background:{COL[s][k]}"></span>' for s, k in
                   [("wild-radiance", "vivid"), ("yellow-flowers", "vivid"), ("lady", "accent"), ("white-flowers", "vivid")])
    stripe = "".join(f'<span style="--c:{COL[a["slug"]]["vivid"]}"></span>' for a in ART)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{A}img/{og}-lg.jpg">
<meta property="og:type" content="website">
<meta name="theme-color" content="#16140f">
<link rel="icon" href="{A}img/favicon.png">
<script>document.documentElement.classList.add("js")</script>
<link rel="preload" href="{P}fonts/bricolage-grotesque-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}css/site.css">
<link rel="stylesheet" href="{P}css/colors.css">
<link rel="stylesheet" href="{A}vendor/photoswipe/photoswipe.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
<a class="brand" href="{P or './'}" aria-label="Scott Beckman, home"><span class="dots" aria-hidden="true">{dots}</span><span class="name">Scott <em>Beckman</em></span></a>
<nav class="nav" aria-label="Main">{nav}</nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="site-footer">
<div class="wrap">
<p class="cta">Let&rsquo;s make something <em>that lasts.</em></p>
<div class="btns"><a class="btn" href="{P}commissions/#start">Commission a painting {ARR}</a><a class="btn ghost" href="{P}contact/#message">Send Scott a message</a></div>
<div class="foot-bottom">{social()}<small>&copy; <span data-year>2026</span> Scott Michael Beckman. All paintings and images are the artist&rsquo;s own; please ask before reusing them.</small></div>
<div class="foot-stripe" aria-hidden="true">{stripe}</div>
</div>
</footer>
<script src="{A}js/site.js" defer></script>
<script src="{P}js/v3.js" defer></script>
<script type="module" src="{A}js/gallery.js"></script>
</body>
</html>
"""


def reveal(A, base, top, alt_base, alt_top, pos, label, big=True, peek=False, rid=""):
    w, h = SIZES[base]["lg" if big else "sm"]
    s = "lg" if big else "sm"
    return f"""<div class="reveal-wrap">
<div class="reveal" style="--pos:{pos}%"{' data-peek' if peek else ''}>
<img src="{A}img/{base}-{s}.jpg" width="{w}" height="{h}" alt="{E(alt_base)}" loading="lazy" decoding="async">
<div class="top"><img src="{A}img/{top}-{s}.jpg" width="{w}" height="{h}" alt="{E(alt_top)}" loading="lazy" decoding="async"></div>
<input type="range" min="0" max="100" value="{pos}" aria-label="{E(label)}">
<div class="handle"></div>
<span class="tag l" aria-hidden="true">Painting</span><span class="tag r" aria-hidden="true">Message</span>
</div>
<div class="reveal-row"><div class="toggle" role="group" aria-label="Show"><button type="button" data-to="100" aria-pressed="false">The painting</button><button type="button" data-to="0" aria-pressed="false">The message</button></div><p>Drag across the painting, or tap a button.</p></div>
</div>"""


def tile(A, P, a, d=0):
    s = a["slug"]
    flag = '<span class="flag">Available</span>' if a.get("available") else ""
    inner = flag + img(A, s, a["alt"], sizes="(max-width: 560px) 80vw, (max-width: 900px) 37vw, 25vw")
    return (f'<figure class="tile c-{s} rise" style="--d:{d}">'
            + pswp(A, s, a["title"], meta_of(a), inner)
            + f'<figcaption><span><span class="t">{E(a["title"])}</span><span class="m">{a["size"]}</span></span>{chips(s)}</figcaption></figure>')


def available_room(A, P, a, n, flip=False, intro=""):
    s = a["slug"]
    m = meta_of(a)
    photos = a["photos"]
    first = pswp(A, s, a["title"], m, img(A, s, a["alt"], sizes="(max-width: 860px) 92vw, 50vw"))
    thumbs = "".join(pswp(A, p, a["title"], m, img(A, p, f'{a["title"]}, photo of the painting in its handmade frame'), cls="thumb")
                     for p in photos[:2])
    hidden = "".join(pswp(A, p, a["title"], m, hidden=True) for p in photos[2:])
    q = a["title"].replace(" ", "%20")
    return f"""<section class="section c-{s}" data-field aria-labelledby="av-{s}">
<div class="wrap">{intro}
<div class="room-av{' flip' if flip else ''}">
<div class="av-photos rise" data-gallery>{first}{thumbs}{hidden}</div>
<div class="rise" style="--d:1">
<span class="av-num">Available original, {n} of 2</span>
<h3 class="h2" id="av-{s}">{E(a["title"])}</h3>
<p class="specs">{E(a["medium"])} · {a["size"]}</p>
<p class="status">Available, ask about it</p>
<p>{E(a["frame"])}</p>
{chips(s, "chips lg pop")}
<div class="btns"><a class="btn" href="{P}contact/?painting={q}#message">Ask about this painting {ARR}</a></div>
</div>
</div>
</div>
</section>"""


# ------------------------------------------------------------------ HOME
def home():
    P, A = "", "../assets/"
    wr = BY["wild-radiance"]
    bl = f'style="--field:#fbfbf9;--b1:{COL["wild-radiance"]["vivid"]};--b2:{COL["yellow-flowers"]["vivid"]};--b3:{COL["white-flowers"]["vivid"]};--wr:{COL["wild-radiance"]["deep"]}"'
    feat = "".join(tile(A, P, a, i % 3) for i, a in enumerate([a for a in ART if a.get("featured")]))
    intro = """<div class="head rise"><div><p class="kicker">Available originals</p><h2 class="h2">Ready to hang, in frames Scott <em>built by hand</em>.</h2></div>
<p class="lead" style="max-width:26em">Scott mills the oak for his frames from trees on his own land, so the frame is as one-of-a-kind as the painting.</p></div>"""
    body = f"""<section class="hero c-paper c-wild-radiance" data-field {bl}>
<div class="bloom" aria-hidden="true"><span class="b1"></span><span class="b2"></span><span class="b3"></span></div>
<div class="wrap">
<div class="hero-grid">
<div>
<p class="kicker">Original oil paintings · Central Arkansas</p>
<h1 class="display"><span class="ln"><span style="--i:0">Paintings</span></span><span class="ln"><span style="--i:1">that hold</span></span><span class="ln"><span style="--i:2"><em>light.</em></span></span></h1>
<p class="lead">Scott Michael Beckman paints flowers, animals, landscapes and people in oil, building every canvas layer by layer until it feels alive. Some even carry a hidden message.</p>
<div class="btns"><a class="btn" href="work/">See the paintings {ARR}</a><a class="btn ghost" href="commissions/">Commission a painting</a></div>
</div>
<figure class="hero-art" data-gallery>
<div class="mat">{pswp(A, "wild-radiance", wr["title"], meta_of(wr), img(A, "wild-radiance", wr["alt"], lazy=False, sizes="(max-width: 860px) 90vw, 36vw"))}</div>
<figcaption><span><b>{wr["title"]}</b>, {wr["size"]}</span>{chips("wild-radiance")}</figcaption>
</figure>
</div>
<div class="hero-meta"><span><b>11</b>paintings in the portfolio</span><span><b>2</b>originals available now</span><span><b>Florals to portraits</b>commissions welcome</span></div>
</div>
</section>

<section class="section c-paper" data-field aria-labelledby="sel">
<div class="wrap">
<div class="head rise"><div><p class="kicker">Selected work</p><h2 class="h2" id="sel">Every painting brings its own <em>color</em>.</h2></div><a class="textlink" href="work/">All 11 paintings {ARR}</a></div>
<div class="tiles" data-gallery>{feat}</div>
</div>
</section>

<section class="section c-yellow-flowers" data-field aria-labelledby="msg">
<div class="wrap">
<div class="story-grid">
<div class="rise"><p class="kicker">A hidden message</p><h2 class="h2" id="msg">Can you see the <em>words</em> in the paint?</h2></div>
<div class="rise" style="--d:1">
<p class="date-tag">A wedding gift<span>January 19, 2002</span></p>
<p style="margin-top:18px">Scott gave <i>Yellow Flowers</i> to his wife Jana on their wedding day. Hidden in the texture of the petals and background is a message only they knew was there. More than twenty years later, it&rsquo;s still the piece she loves showing people most.</p>
<a class="textlink" href="commissions/">Put your own message in a painting {ARR}</a>
</div>
</div>
<div class="rise">{reveal(A, "yellow-flowers", "yellow-flowers-message", "Yellow Flowers, the painting as it appears on the wall", "Yellow Flowers with the hidden words 'With love' and 'I love you' traced in red", 62, "Slide to reveal the hidden message", peek=True)}</div>
</div>
</section>

{available_room(A, P, BY["old-barn"], 1, intro=intro)}
{available_room(A, P, BY["yellow-house"], 2, flip=True)}

<section class="section c-scott" data-field aria-labelledby="ab">
<div class="wrap about-t">
<figure class="portrait rise">{img(A, "scott", "Portrait of Scott Beckman outdoors among trees", sizes="(max-width: 860px) 90vw, 36vw")}</figure>
<div class="rise" style="--d:1">
<p class="kicker" id="ab">About the artist</p>
<blockquote class="bigquote">Art is my lifelong pursuit. Each new work is an opportunity to grow and challenge myself. I strive to make every painting the best I&rsquo;ve ever done.<footer>Scott Michael Beckman</footer></blockquote>
<p>Born in Cincinnati and now living in Central Arkansas, Scott is a U.S. military veteran and registered nurse who worked in Texas ICUs during the Covid-19 pandemic. Those years shape how he paints: patiently, and with an eye for the small moments that matter.</p>
<a class="textlink" href="about/">Read Scott&rsquo;s story {ARR}</a>
</div>
</div>
</section>"""
    return page(P, "Scott Beckman Art | Original Oil Paintings",
                "Original oil paintings by Scott Michael Beckman: florals, animals, landscapes and portraits, painted in Central Arkansas. Commissions welcome.", body)


# ------------------------------------------------------------------ WORK
def work():
    P, A = "../", "../../assets/"
    rooms = []
    for i, a in enumerate(ART, 1):
        s = a["slug"]
        avail = ""
        if a.get("available"):
            q = a["title"].replace(" ", "%20")
            avail = f'<div class="avail"><p class="status">Available, ask about it</p><a class="textlink" href="{P}contact/?painting={q}#message">Ask about this painting {ARR}</a></div>'
        subj = dict(SUBJECTS)[a["subject"]]
        rooms.append(f"""<figure class="room art c-{s}" data-field data-subject="{a['subject']}"{' data-available' if a.get('available') else ''}>
<div class="room-art rise">{pswp(A, s, a["title"], meta_of(a), img(A, s, a["alt"], lazy=i > 1, sizes="(max-width: 860px) 92vw, 52vw"))}</div>
<figcaption class="room-text rise" style="--d:1">
<span class="idx">No. {i:02d} of {len(ART)}</span>
<h2>{E(a["title"])}</h2>
<p class="meta"><span>{a["size"]}</span><span>{E(a.get("medium", "Oil painting"))}</span><span>{subj}</span></p>
<p class="desc muted">{E(desc_of(a))}</p>
<div class="palette"><p>Palette</p>{chips(s, "chips lg pop")}</div>
{avail}
</figcaption>
</figure>""")
    filt = '<button type="button" data-filter="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-filter="{k}" aria-pressed="false">{n}</button>' for k, n in SUBJECTS) + \
        '<button type="button" data-filter="available" aria-pressed="false">Available</button>'
    grad = ", ".join(COL[s]["vivid"] for s in ["wild-radiance", "pig", "yellow-flowers", "lady", "white-flowers"])
    body = f"""<section class="work-head c-paper" data-field style="--g:{grad}">
<div class="wrap">
<p class="kicker">The work</p>
<h1 class="display">Eleven rooms<br>of <em>color</em>.</h1>
<p class="lead">Each painting sets the color of its own room as you scroll. Tap any painting to see it large, or switch to the grid for a quick look at everything.</p>
<div class="work-tools">
<div class="filters" role="group" aria-label="Filter by subject">{filt}</div>
<div class="viewsw" role="group" aria-label="View"><button type="button" data-view="rooms" aria-pressed="true">Rooms</button><button type="button" data-view="grid" aria-pressed="false">Grid</button></div>
</div>
<p class="count" data-count aria-live="polite" style="margin-top:12px">{len(ART)} paintings</p>
</div>
</section>
<div class="wrap"><div class="rooms gallery" data-gallery>
{''.join(rooms)}
</div></div>"""
    return page(P, "Work | Scott Beckman Art",
                "All of Scott Michael Beckman's oil paintings: florals, animals, landscapes and portraits, each shown large.", body, "work")


# ------------------------------------------------------------------ COMMISSIONS
def commissions():
    P, A = "../", "../../assets/"
    prices = [("11 × 14 in", 11, 14, "$900", "lady"), ("16 × 20 in", 16, 20, "$1,800", "old-barn"),
              ("18 × 24 in", 18, 24, "$2,450", "bliss-birds"), ("24 × 36 in", 24, 36, "$4,850", "yellow-flowers"),
              ("24 × 48 in", 24, 48, "$6,500", "purple-flowers"), ("30 × 40 in", 30, 40, "$6,750", "wild-radiance")]
    pr = "".join(f'<div class="price"><div class="canvas" style="--w:{w};--h:{h};--i:{i};background:{COL[s]["vivid"]}" title="{E(BY[s]["title"])} colors"></div>'
                 f'<span class="size">{sz}</span><span class="amt">{amt}</span></div>'
                 for i, (sz, w, h, amt, s) in enumerate(prices))
    steps = ["Phone consultation with the artist.", "Verbal agreement on subject, size and price.",
             "The artist designs a digital composition and presents it to you.",
             "If you both decide to go forward, a written contract is signed by both.",
             "You pay 50% up front, before the physical painting begins.", "The artist completes the painting.",
             "You pay the remaining 50% and receive your finished painting.",
             "You hang it somewhere visible, with bragging rights to an original Scott Beckman oil painting."]
    stc = ["wild-radiance", "yellow-flowers", "pig", "white-flowers", "lady", "purple-flowers", "majestic-horse", "bliss-birds"]
    st = "".join(f'<li class="rise" style="--c:{COL[stc[i]]["deep"]};--d:{i % 4}"><p>{t}</p></li>' for i, t in enumerate(steps))
    wf = BY["white-flowers"]
    body = f"""<section class="section c-white-flowers" data-field style="padding-top:clamp(30px,5vw,70px)">
<div class="wrap split">
<div>
<p class="kicker">Commissions</p>
<h1 class="h2" style="font-size:clamp(2.8rem,1.2rem + 5.4vw,7rem)">A floral painting made <em>for you</em>.</h1>
<p class="lead" style="margin-top:28px">There&rsquo;s something timeless and deeply expressive about painting flowers. Each bloom carries its own personality: soft and delicate, bold and vibrant, fleeting yet full of life.</p>
<p>I love capturing the way light dances on petals, the richness of color, and the quiet elegance that flowers bring to a space. With oil paint, I can build layers of texture and depth, creating pieces that feel almost alive. Painting flowers allows me to celebrate nature&rsquo;s beauty in a way that lasts forever.</p>
<div class="btns"><a class="btn" href="#start">Start a commission {ARR}</a><a class="btn ghost" href="#prices">See prices</a></div>
</div>
<figure class="hero-art c-hero-art" data-gallery style="margin:0"><div class="mat">{pswp(A, "white-flowers", wf["title"], meta_of(wf), img(A, "white-flowers", wf["alt"], lazy=False, sizes="(max-width: 860px) 90vw, 34vw"))}</div>
<figcaption><span><b>{wf["title"]}</b>, {wf["size"]}</span>{chips("white-flowers")}</figcaption></figure>
</div>
</section>

<section class="section c-yellow-flowers" data-field aria-labelledby="hm">
<div class="wrap">
<div class="rise" style="margin-bottom:clamp(30px,4vw,56px)"><p class="kicker">A hidden message</p><h2 class="h2" id="hm">Words only <em>you</em> know are there.</h2></div>
<div class="story-grid rise" style="align-items:start">
<p>At first glance you would never see it, but can you see the words hidden within the texture of these paintings? I presented <i>Yellow Flowers</i> to my wife on our wedding day, January 19th, 2002. To this day it is one of her most valuable possessions. Not only is it a beautiful oil painting to look at, it is a story: a message of love we have enjoyed for over 20 years.</p>
<p>It is also a conversation piece. Jana loves to show it to people. She tells them it was a wedding gift I gave her on that special day, then asks if they can see the message. <strong>What message would you include in your commissioned painting? What would it mean to you? What story would it tell?</strong></p>
</div>
<div class="reveal-pair">
<div class="rise">{reveal(A, "yellow-flowers", "yellow-flowers-message", "Yellow Flowers, the painting as it appears on the wall", "Yellow Flowers with the hidden words 'With love' and 'I love you' traced in red", 60, "Slide to reveal the hidden message in Yellow Flowers", peek=True)}<h3>Yellow Flowers</h3></div>
<div class="rise" style="--d:1">{reveal(A, "wild-radiance", "wild-radiance-message", "Wild Radiance, the painting as it appears on the wall", "Wild Radiance with its hidden message traced in red", 55, "Slide to reveal the hidden message in Wild Radiance", big=False)}<h3>Wild Radiance</h3></div>
</div>
</div>
</section>

<section class="section c-paper" data-field id="prices" aria-labelledby="pr">
<div class="wrap">
<div class="head rise"><div><p class="kicker">Sizes and prices</p><h2 class="h2" id="pr">Pick your <em>canvas</em>.</h2></div><p class="lead" style="max-width:22em">Each canvas is drawn to scale with the others, colored from one of Scott&rsquo;s paintings. Custom sizes are available.</p></div>
<div class="prices">{pr}</div>
</div>
</section>

<section class="section c-purple-flowers" data-field aria-labelledby="pc">
<div class="wrap">
<div class="head rise"><div><p class="kicker">How it works</p><h2 class="h2" id="pc">The commission <em>process</em>.</h2></div></div>
<ol class="steps">{st}</ol>
</div>
</section>

<section class="section c-paper" data-field aria-labelledby="fq">
<div class="wrap">
<div class="head rise"><div><p class="kicker">Questions</p><h2 class="h2" id="fq">Good to <em>know</em>.</h2></div></div>
<div class="faq rise">
<details><summary>How long does it take?</summary><div class="answer">
<p>Every painting is different, so it is impossible to give an exact timeline. The two main factors are how many commissions are ahead of yours and the size of the painting. A 30 × 40 in painting takes approximately 100 hours once the concept is agreed and paint starts going on the canvas. When it is complete, it takes 2–4 weeks to dry. That puts a 30 × 40 at roughly 4–6 weeks if no commissions are ahead of yours, not including shipping or delivery.</p>
<p>When the written contract is made, you will have an agreed completion date in writing, along with your options if the artist cannot meet the deadline.</p>
<p>In a time crunch, or need a gift sooner? For an extra charge you can get an original black-and-white graphite drawing of the planned painting to present with the promise of the painting to come.</p>
</div></details>
<details><summary>Who decides what is in the painting?</summary><div class="answer">
<p>It&rsquo;s a collaboration between you and the artist. The best works of art come from inspiration deep within the artist as they create; without it, the final piece would be missing that special something. That is why Scott reserves the right to turn down commissions that don&rsquo;t inspire him.</p>
<p><em>&ldquo;I won&rsquo;t start a painting that I am not willing to hang in my living room when it is complete.&rdquo;</em></p>
<p>Scott often works from several photographs to make a single painting. You can provide photos you took yourself or that aren&rsquo;t under copyright. For example, if you&rsquo;d like your wedding flowers painted from your professional photographer&rsquo;s pictures, you&rsquo;ll need the photographer&rsquo;s written permission, even though you paid for the images.</p>
<p>Photos aren&rsquo;t required, though. What flowers were at the wedding? What colors? Scott can compose a painting from that, and you&rsquo;ll see the composition before any deposit. You can also choose from flower photographs Scott has taken himself, or just name your favorite color and let him find the flower to match.</p>
</div></details>
<details><summary>Why oil paint?</summary><div class="answer">
<p>Oil paint has been the preferred medium of master artists for centuries, prized for its rich pigments, depth and longevity. It allows smooth blending and intricate detail, and its slow drying time lets the artist build layers and luminosity unmatched by other mediums. Many masterpieces from the Renaissance and beyond have survived for hundreds of years, their colors still vibrant. Properly cared for, an oil painting is a legacy that can be passed down for generations.</p>
<p>Scott&rsquo;s paintings are typically touch-dry within 2–4 weeks, when a temporary protective retouch varnish can be applied before delivery. Oil paint can take 6 months to a year to dry fully; after that, a final varnish is recommended.</p>
</div></details>
<details><summary>Can I get a discount?</summary><div class="answer">
<p>Unlike mass-reproduced art from big-box stores, original art is an investment: a one-of-a-kind work the artist puts their heart and soul into. There is no experience like standing in front of an original and seeing the texture of each brushstroke. A printer or a screen cannot recreate that, and as AI fills the world with mass-produced images, hand-made human art becomes even more valuable.</p>
<p>When you commission an original oil painting from me, I will put everything I have into it, and be just as passionate about it as you are. You&rsquo;re not just buying a pretty picture; you&rsquo;re buying the centerpiece of your space, an investment that won&rsquo;t be discounted in the future.</p>
</div></details>
</div>
</div>
</section>

<section class="section c-pig" data-field id="start" aria-labelledby="sc">
<div class="wrap split" style="align-items:start">
<div class="rise"><p class="kicker">Let&rsquo;s create art together</p><h2 class="h2" id="sc">Start your <em>commission</em>.</h2><p class="lead" style="margin-top:24px">Tell Scott a little about what you have in mind and he&rsquo;ll be in touch.</p></div>
<div class="form-card rise" style="--d:1">
<form class="form" data-form="Commission inquiry">
<div><label for="c-name">Your name *</label><input id="c-name" name="name" autocomplete="name" required></div>
<div><label for="c-email">Your email *</label><input id="c-email" name="email" type="email" autocomplete="email" required></div>
<div><label for="c-phone">Phone</label><input id="c-phone" name="phone" type="tel" autocomplete="tel"></div>
<div><label for="c-size">Size</label><select id="c-size" name="size"><option value="">Not sure yet</option><option>11 × 14 in</option><option>16 × 20 in</option><option>18 × 24 in</option><option>24 × 36 in</option><option>30 × 40 in</option><option>24 × 48 in</option><option>Custom size</option></select></div>
<div class="full"><label for="c-delivery">How you&rsquo;ll receive it</label><select id="c-delivery" name="delivery"><option value="">Choose one</option><option>Pickup in Central Arkansas</option><option>Shipping in the USA</option><option>International shipping</option><option>Artist delivered</option></select></div>
<div class="full"><label for="c-msg">Your vision *</label><textarea id="c-msg" name="message" required placeholder="What would you like painted? When do you need it? Is there a hidden message you'd like in it?"></textarea></div>
<input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">
<div class="full"><button class="btn" type="submit">Send to Scott {ARR}</button>
<p class="note">Your answers go to Scott by email through Formspree, a form service. They&rsquo;re used only to reply to you about your commission.</p>
<p class="form-status" role="status" aria-live="polite"></p></div>
</form>
</div>
</div>
</section>"""
    return page(P, "Commissions | Scott Beckman Art",
                "Commission an original oil painting from Scott Michael Beckman, with an optional hidden message. Sizes, prices, process and FAQ.",
                body, "commissions", og="white-flowers")


# ------------------------------------------------------------------ ABOUT
def about():
    P, A = "../", "../../assets/"
    body = f"""<section class="section c-scott" data-field style="padding-top:0">
<div class="wrap about-hero">
<figure class="portrait">{img(A, "scott", "Portrait of Scott Beckman outdoors among trees", lazy=False, sizes="(max-width: 860px) 90vw, 42vw")}</figure>
<div class="about-copy">
<p class="kicker">Oil painter · Central Arkansas</p>
<h1 class="h2" style="font-size:clamp(2.8rem,1.2rem + 5vw,6.6rem)">Scott Michael <em>Beckman</em></h1>
<p class="lead" style="margin-top:28px">Born in Cincinnati, Ohio, and now living in Central Arkansas, Scott Michael Beckman is a versatile artist whose work spans landscapes, animals, florals and portraits.</p>
<p>With a deep passion for the expressive nature of oil painting, Scott&rsquo;s work reflects both his artistic vision and his connection to the world around him.</p>
<p>His artistic journey has been shaped by a variety of life experiences. He proudly served in the U.S. military and later became a registered nurse. During the Covid-19 pandemic, Scott traveled to some of Texas&rsquo; hardest-hit areas, working in the ICU caring for those most in need. These experiences left a lasting impact on his approach to both life and art.</p>
<p>Scott has been married to his wife for 23 years and is the proud father of a son and daughter. His family remains a strong source of inspiration and support throughout his creative work.</p>
<p>Through his art, Scott captures the beauty and complexity of the world, inviting viewers to appreciate the small and significant moments in life. Whether it&rsquo;s the calm of a landscape, the strength and beauty of an animal, or the intimate details of a portrait, his paintings evoke emotion and invite reflection.</p>
<blockquote class="bigquote" style="margin:56px 0">Art is my lifelong pursuit. Each new work is an opportunity to grow and challenge myself. I strive to make every painting the best I&rsquo;ve ever done.</blockquote>
<p class="muted">Follow along for new work and painting videos:</p>
{social()}
<p style="margin-top:36px"><a class="textlink" href="{P}work/">See the paintings {ARR}</a></p>
</div>
</div>
</section>"""
    return page(P, "About | Scott Beckman Art",
                "About Scott Michael Beckman: oil painter in Central Arkansas, U.S. military veteran and registered nurse.", body, "about", og="scott")


# ------------------------------------------------------------------ CONTACT
def contact():
    P, A = "../", "../../assets/"
    body = f"""<section class="section c-lady" data-field style="padding-top:clamp(30px,5vw,70px)">
<div class="wrap contact-grid">
<div>
<p class="kicker">Contact</p>
<h1 class="display" style="font-size:clamp(3rem,1.2rem + 6.4vw,8rem)">Say <em>hello</em>.</h1>
<p class="lead" style="margin-top:28px">Questions about a painting, a commission, or just want to say hello? Scott would love to hear from you.</p>
<p class="muted" style="margin-top:32px">Or find Scott here:</p>
{social()}
<p style="margin-top:36px">Thinking about a painting made just for you? <a class="textlink" href="{P}commissions/#start">Commission details {ARR}</a></p>
</div>
<div id="message" class="form-card">
<form class="form" data-form="Message from scottbeckmanart.com" style="grid-template-columns:1fr">
<div><label for="m-name">Your name *</label><input id="m-name" name="name" autocomplete="name" required></div>
<div><label for="m-email">Your email *</label><input id="m-email" name="email" type="email" autocomplete="email" required></div>
<div><label for="m-msg">Message *</label><textarea id="m-msg" name="message" required></textarea></div>
<input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">
<div><button class="btn" type="submit">Send message {ARR}</button>
<p class="note">Your name, email and message go to Scott by email through Formspree, a form service. They&rsquo;re used only to reply to you.</p>
<p class="form-status" role="status" aria-live="polite"></p></div>
</form>
</div>
</div>
</section>"""
    return page(P, "Contact | Scott Beckman Art",
                "Get in touch with oil painter Scott Michael Beckman about a painting or a commission.", body, "contact", og="lady")


def main():
    out = {"index.html": home(), "work/index.html": work(), "commissions/index.html": commissions(),
           "about/index.html": about(), "contact/index.html": contact()}
    for rel, txt in out.items():
        p = V3 / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")
        print("wrote", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
