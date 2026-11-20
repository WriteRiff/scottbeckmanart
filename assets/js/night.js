/* Night Gallery — small motion helpers. Everything is visible without this file. */
(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Header: background appears once you scroll ---- */
  var header = document.querySelector(".site-header");
  var ticking = false;
  function onScroll() {
    ticking = false;
    if (header) header.classList.toggle("scrolled", window.scrollY > 40);
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* ---- Phone menu ---- */
  var btn = document.querySelector(".menu-btn");
  if (btn && header) {
    function setMenu(open) {
      header.classList.toggle("menu-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.querySelector(".txt").textContent = open ? "Close" : "Menu";
      document.body.style.overflow = open ? "hidden" : "";
    }
    btn.addEventListener("click", function () { setMenu(!header.classList.contains("menu-open")); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && header.classList.contains("menu-open")) { setMenu(false); btn.focus(); } });
    header.querySelectorAll(".nav a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    window.matchMedia("(min-width: 761px)").addEventListener("change", function (m) { if (m.matches) setMenu(false); });
  }

  /* ---- Lights come on as paintings reach the viewport ---- */
  var lit = document.querySelectorAll(".lit, .fade");
  if (reduce || !("IntersectionObserver" in window)) {
    lit.forEach(function (el) { el.classList.add("is-lit"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-lit"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.12 });
    lit.forEach(function (el) { io.observe(el); });
  }

  /* ---- Home: slow crossfade between paintings under the spotlight ---- */
  var hero = document.querySelector("[data-hero]");
  if (hero) {
    var slides = hero.querySelectorAll(".slide");
    var caps = document.querySelectorAll(".now .cap-item");
    var count = document.querySelector(".count");
    var pauseBtn = document.querySelector("[data-pause]");
    var i = 0, timer = null, paused = reduce, visible = true;
    // Only the painting on show can be clicked or tabbed to (it opens the large view).
    function linkState() {
      slides.forEach(function (s, k) { var a = s.querySelector("a"); if (a) a.tabIndex = k === i ? 0 : -1; });
    }
    function show(n) {
      slides[i].classList.remove("is-on"); if (caps[i]) caps[i].classList.remove("is-on");
      i = (n + slides.length) % slides.length;
      var img = slides[i].querySelector("img");
      if (img && img.loading === "lazy") img.loading = "eager";
      slides[i].classList.add("is-on"); if (caps[i]) caps[i].classList.add("is-on");
      if (count) count.textContent = ("0" + (i + 1)).slice(-2) + " / " + ("0" + slides.length).slice(-2);
      linkState();
    }
    linkState();
    // Hold the slideshow while the large view is open.
    hero.addEventListener("click", function (e) { if (e.target.closest(".slide a")) { paused = true; setPauseLabel(); schedule(); } });
    function schedule() { clearTimeout(timer); if (!paused && visible) timer = setTimeout(function () { show(i + 1); schedule(); }, 7000); }
    hero.querySelectorAll("[data-step]").forEach(function (b) {
      b.addEventListener("click", function () { show(i + Number(b.getAttribute("data-step"))); schedule(); });
    });
    function setPauseLabel() {
      if (!pauseBtn) return;
      pauseBtn.setAttribute("aria-label", paused ? "Play slideshow" : "Pause slideshow");
      pauseBtn.innerHTML = paused
        ? '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 1.5v11l9-5.5z"/></svg>'
        : '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 1.5h2.6v11H3zM8.4 1.5H11v11H8.4z"/></svg>';
    }
    if (pauseBtn) pauseBtn.addEventListener("click", function () { paused = !paused; setPauseLabel(); schedule(); });
    setPauseLabel();
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { visible = en[0].isIntersecting; schedule(); }).observe(hero);
    }
    document.addEventListener("visibilitychange", function () { visible = !document.hidden; schedule(); });
    // warm the next images after load
    window.addEventListener("load", function () {
      slides.forEach(function (s) { var im = s.querySelector("img"); if (im) im.loading = "eager"; });
    });
    schedule();
  }

  /* ---- Desktop: a soft spotlight follows the pointer across the wall ---- */
  if (!reduce && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    var torch = document.createElement("div");
    torch.className = "torch"; torch.setAttribute("aria-hidden", "true");
    document.body.appendChild(torch);
    var x = 0, y = 0, queued = false;
    function place() { queued = false; torch.style.transform = "translate3d(" + x + "px," + y + "px,0)"; }
    document.addEventListener("pointermove", function (e) {
      if (e.pointerType !== "mouse") return;
      x = e.clientX; y = e.clientY;
      if (!torch.classList.contains("on")) { place(); torch.classList.add("on"); }
      if (!queued) { queued = true; requestAnimationFrame(place); }
    }, { passive: true });
    document.documentElement.addEventListener("mouseleave", function () { torch.classList.remove("on"); });
  }

  /* ---- Hidden message: drag the beam of light, or tap "The painting" / "The message"
         and the light glides all the way across. On first view the light sweeps over
         the whole painting, then settles part-way. ---- */
  document.querySelectorAll(".reveal").forEach(function (box) {
    var input = box.querySelector("input[type=range]");
    if (!input) return;
    var wrap = box.closest(".reveal-wrap");
    var group = wrap && wrap.querySelector(".toggle");
    var rest = Number(input.value);
    var raf = 0, touched = false, pending = false, pct = rest;

    function press(v) {
      if (!group) return;
      group.querySelectorAll("button").forEach(function (b) {
        var to = Number(b.getAttribute("data-to"));
        b.setAttribute("aria-pressed", String((to === 0 && v <= 2) || (to === 100 && v >= 98)));
      });
    }
    function paint() { pending = false; box.style.setProperty("--pos", pct + "%"); box.style.setProperty("--k", pct / 100); }
    function set(v) {
      pct = Math.max(0, Math.min(100, v)); input.value = Math.round(pct); press(pct);
      if (!pending) { pending = true; requestAnimationFrame(paint); }
    }
    // Glide the light to a spot: one rAF loop, transform-only beam and a mask on the top image.
    function glide(to, dur, done) {
      cancelAnimationFrame(raf);
      if (reduce) { set(to); if (done) done(); return; }
      var from = pct, t0 = null;
      function step(t) {
        if (t0 === null) t0 = t;
        var k = Math.min(1, (t - t0) / dur);
        var e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
        pct = from + (to - from) * e; input.value = Math.round(pct); press(pct);
        box.style.setProperty("--pos", pct + "%"); box.style.setProperty("--k", pct / 100);
        if (k < 1) raf = requestAnimationFrame(step); else if (done) done();
      }
      raf = requestAnimationFrame(step);
    }
    function stopAuto() { touched = true; cancelAnimationFrame(raf); }

    // Dragging follows the finger or mouse directly: no easing.
    ["pointerdown", "keydown", "touchstart"].forEach(function (ev) { input.addEventListener(ev, stopAuto, { passive: true }); });
    input.addEventListener("input", function () { touched = true; cancelAnimationFrame(raf); set(Number(input.value)); });
    if (group) group.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (b) { stopAuto(); glide(Number(b.getAttribute("data-to")), 900); }
    });
    press(pct);

    if (reduce || !box.hasAttribute("data-peek") || !("IntersectionObserver" in window)) return;
    set(0); paint();
    var seen = new IntersectionObserver(function (en) {
      if (!en[0].isIntersecting) return;
      seen.disconnect();
      setTimeout(function () {
        if (touched) return;
        glide(100, 1700, function () {
          setTimeout(function () { if (!touched) glide(rest, 1100); }, 900);
        });
      }, 450);
    }, { threshold: 0.55 });
    seen.observe(box);
  });
})();
