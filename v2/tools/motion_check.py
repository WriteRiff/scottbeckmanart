"""Motion check for v2 (headless): frame timing during the hero brush wipes, during a wheel scroll
through each page (drift + reveals), during the hidden-message sweep, and that nothing is left half-way.
Usage: python v2/tools/motion_check.py [pages...]"""
import sys, subprocess, time, socket
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PORT = 8142
pages = sys.argv[1:] or ["", "work/", "commissions/", "about/", "contact/"]

REC = """
window.__f=[]; (function loop(t){ window.__f.push(t); if(window.__f.length<100000) requestAnimationFrame(loop); })(performance.now());
"""
STATS = """
(() => { const f = window.__f; const d = []; for (let i = 1; i < f.length; i++) d.push(f[i]-f[i-1]);
 d.sort((a,b)=>a-b); const n=d.length; const long=d.filter(x=>x>25).length; const at=[]; for (let i=1;i<f.length;i++) if(f[i]-f[i-1]>25) at.push(Math.round(f[i-1])+"ms:"+Math.round(f[i]-f[i-1]));
 window.__f=[]; return {frames:n, median:+d[Math.floor(n/2)].toFixed(1), p95:+d[Math.floor(n*.95)].toFixed(1), max:+d[n-1].toFixed(1), over25ms:long, at:at.slice(0,4)}; })()
"""

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
        for w, h, tag in [(1440, 900, "desktop"), (390, 844, "phone")]:
            ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="no-preference")
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda ex: errs.append(str(ex)))
            pg.add_init_script(REC)
            for path in pages:
                pg.goto(f"http://127.0.0.1:{PORT}/v2/{path}", wait_until="load")
                pg.wait_for_timeout(2600)
                intro = pg.evaluate(STATS)
                # wheel-scroll through the page like a person
                H = pg.evaluate("document.documentElement.scrollHeight")
                pg.mouse.move(w / 2, h / 2)
                for _ in range(int(H / 120) + 10):
                    pg.mouse.wheel(0, 120); pg.wait_for_timeout(16)
                scroll = pg.evaluate(STATS)
                pg.wait_for_timeout(3600)
                left = pg.evaluate("""[...document.querySelectorAll('.wipe')].filter(e=>!e.classList.contains('is-done')).map(e=>{const r=e.getBoundingClientRect(); return (e.className+' @'+Math.round(r.top+scrollY))})""")
                rises = pg.evaluate("[...document.querySelectorAll('.rise')].filter(e=>getComputedStyle(e).opacity!=='1').length")
                drift = pg.evaluate("[...document.querySelectorAll('[data-drift]')].map(e=>e.style.transform).filter(Boolean).length")
                print(f"{tag:7} /{path:13} intro {intro}  scroll {scroll}  unfinished-wipes {left[:4]} hidden-rises {rises} drifting {drift} errors {errs[:3]}")
                errs.clear()
            ctx.close()
        b.close()
finally:
    if srv:
        srv.terminate()

