"""Functional checks for v2 (headless): links, viewer, filters, slider, prefill, no-JS visibility,
tap-target sizes, and frame timing of the slider sweep and a drag."""
import sys, subprocess, time, socket, re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PORT = 8142
BASE = f"http://127.0.0.1:{PORT}/v2/"
PAGES = ["", "work/", "commissions/", "about/", "contact/"]

def up():
    try:
        socket.create_connection(("127.0.0.1", PORT), 0.3).close(); return True
    except OSError:
        return False

srv = None
if not up():
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1", "--directory", str(ROOT)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        if up(): break
        time.sleep(0.1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, channel="msedge")
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        # 1. links
        bad = []
        seen = set()
        for path in PAGES:
            pg.goto(BASE + path)
            hrefs = pg.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
            for h in hrefs:
                u = urljoin(BASE + path, h).split("#")[0]
                if urlparse(u).netloc != f"127.0.0.1:{PORT}" or u in seen: continue
                seen.add(u)
                r = ctx.request.get(u)
                if r.status >= 400: bad.append((path, h, r.status))
                if "/v2/" not in u and "/assets/" not in u: bad.append((path, h, "leaves v2"))
        print("links checked", len(seen), "bad", bad)
        # 2. viewer opens
        pg.goto(BASE + "work/"); pg.wait_for_timeout(800)
        pg.click(".gallery .art a >> nth=2"); pg.wait_for_timeout(1200)
        print("viewer open:", pg.locator(".pswp").count() > 0, "caption:", pg.locator(".pswp__custom-caption").first.inner_text() if pg.locator(".pswp__custom-caption").count() else None)
        pg.keyboard.press("Escape"); pg.wait_for_timeout(600)
        # 3. filters
        pg.click(".filters button[data-filter=animals]"); pg.wait_for_timeout(200)
        vis = pg.eval_on_selector_all(".gallery .art", "els => els.filter(e=>!e.hidden).map(e=>e.querySelector('.t').textContent + (e.classList.contains('is-alt')?'(alt)':''))")
        print("animals filter:", vis)
        pg.click(".filters button[data-filter=available]"); pg.wait_for_timeout(200)
        print("available filter:", pg.eval_on_selector_all(".gallery .art", "els => els.filter(e=>!e.hidden).map(e=>e.querySelector('.t').textContent)"))
        # 4. prefill
        pg.goto(BASE + "contact/?painting=Old%20Barn#message"); pg.wait_for_timeout(300)
        print("prefill:", pg.input_value("#m-msg"))
        # 5. slider keyboard
        pg.goto(BASE); pg.wait_for_timeout(300)
        pg.focus(".reveal input"); pg.keyboard.press("ArrowLeft"); pg.keyboard.press("ArrowLeft"); pg.wait_for_timeout(100)
        print("slider --pos after keys:", pg.eval_on_selector(".reveal", "e => e.style.getPropertyValue('--pos')"))
        # 6. small tap targets
        small = pg.evaluate("""[...document.querySelectorAll('a,button,input,select,textarea,summary')].filter(e=>{const r=e.getBoundingClientRect(); const s=getComputedStyle(e); return r.width>0 && s.visibility!=='hidden' && e.type!=='hidden' && e.name!=='_gotcha' && (r.height<44) && !e.closest('.pswp')}).map(e=>e.tagName+':'+(e.textContent||e.name||'').trim().slice(0,24)+':'+Math.round(e.getBoundingClientRect().height))""")
        print("under-44px targets (desktop home):", small[:12])
        ctx.close()
        # 7. frame timing: slider sweep + drag, phone + motion
        ctx = b.new_context(viewport={"width": 390, "height": 844}, reduced_motion="no-preference", has_touch=False)
        pg = ctx.new_page()
        pg.goto(BASE); pg.wait_for_timeout(1500)
        pg.evaluate("document.querySelector('.reveal').scrollIntoView({block:'center'})")
        pg.evaluate("window.__f=[]; (function l(t){window.__f.push(t); if(window.__f.length<5000) requestAnimationFrame(l)})(performance.now())")
        pg.wait_for_timeout(2600)
        st = pg.evaluate("(()=>{const f=__f,d=[];for(let i=1;i<f.length;i++)d.push(f[i]-f[i-1]);d.sort((a,b)=>a-b);__f=[];return {n:d.length,p95:+d[Math.floor(d.length*.95)].toFixed(1),max:+d[d.length-1].toFixed(1)}})()")
        pos = pg.eval_on_selector(".reveal", "e => e.style.getPropertyValue('--pos')")
        print("sweep frames", st, "ended at", pos)
        box = pg.locator(".reveal").bounding_box()
        y = box["y"] + box["height"] / 2
        pg.mouse.move(box["x"] + box["width"] * .6, y); pg.mouse.down()
        for i in range(40):
            pg.mouse.move(box["x"] + box["width"] * (.6 - i * .012), y); pg.wait_for_timeout(16)
        pg.mouse.up()
        st = pg.evaluate("(()=>{const f=__f,d=[];for(let i=1;i<f.length;i++)d.push(f[i]-f[i-1]);d.sort((a,b)=>a-b);__f=[];return {n:d.length,p95:+d[Math.floor(d.length*.95)].toFixed(1),max:+d[d.length-1].toFixed(1)}})()")
        print("drag frames", st, "pos now", pg.eval_on_selector(".reveal", "e => e.style.getPropertyValue('--pos')"))
        ctx.close()
        # 8. no-JS: everything visible
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, java_script_enabled=False)
        pg = ctx.new_page()
        for path in PAGES:
            pg.goto(BASE + path)
            hidden = pg.evaluate("[...document.querySelectorAll('.wipe,.rise')].filter(e=>{const s=getComputedStyle(e); return s.opacity==='0' || (s.maskImage && s.maskImage!=='none') || (s.webkitMaskImage && s.webkitMaskImage!=='none')}).length")
            print("no-JS hidden on", path or "home", hidden)
        ctx.close()
        b.close()
finally:
    if srv:
        srv.terminate()
