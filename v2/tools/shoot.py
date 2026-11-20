"""Headless check for v2: screenshots at phone and desktop width, console errors, broken requests,
sideways scroll. Usage: python v2/tools/shoot.py OUTDIR [pages...] [--motion]"""
import sys, subprocess, time, socket
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
args = ["" if a == "home" else a for a in sys.argv[2:] if not a.startswith("--")]
pages = args or ["", "work/", "commissions/", "about/", "contact/"]
PORT = 8142

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
        for w, h, tag in [(1440, 900, "d"), (390, 844, "m")]:
            ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                                reduced_motion="reduce" if "--motion" not in sys.argv else "no-preference")
            pg = ctx.new_page()
            errs = []
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda ex: errs.append(str(ex)))
            pg.on("response", lambda r: errs.append(f"{r.status} {r.url}") if r.status >= 400 else None)
            for path in pages:
                pg.goto(f"http://127.0.0.1:{PORT}/v2/{path}", wait_until="networkidle")
                # scroll through to trigger lazy images and reveals
                H = pg.evaluate("document.documentElement.scrollHeight")
                y = 0
                while y < H:
                    pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(60); y += h // 2
                    H = pg.evaluate("document.documentElement.scrollHeight")
                pg.wait_for_timeout(2500)
                pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(400)
                sw = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                name = (path.strip("/") or "home").replace("/", "_")
                pg.screenshot(path=str(out / f"{name}-{tag}.png"), full_page=True)
                print(tag, name, "H", H, "sideways", sw, "errors", errs[:6])
                errs.clear()
            ctx.close()
        b.close()
finally:
    if srv:
        srv.terminate()
