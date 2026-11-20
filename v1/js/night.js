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
    function show(n) {
      slides[i].classList.remove("is-on"); if (caps[i]) caps[i].classList.remove("is-on");
      i = (n + slides.length) % slides.length;
      var img = slides[i].querySelector("img");
      if (img && img.loading === "lazy") img.loading = "eager";
      slides[i].classList.add("is-on"); if (caps[i]) caps[i].classList.add("is-on");
      if (count) count.textContent = ("0" + (i + 1)).slice(-2) + " / " + ("0" + slides.length).slice(-2);
    }
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

  /* ---- Hidden message: the light follows the mouse, and sweeps in once ---- */
  document.querySelectorAll(".reveal").forEach(function (box) {
    var input = box.querySelector("input[type=range]");
    if (!input) return;
    var touched = false, pending = false, pct = Number(input.value);
    function apply() { pending = false; box.style.setProperty("--pos", pct + "%"); }
    function set(v) { pct = Math.max(0, Math.min(100, v)); input.value = Math.round(pct); if (!pending) { pending = true; requestAnimationFrame(apply); } }
    input.addEventListener("input", function () { touched = true; pct = Number(input.value); });
    box.addEventListener("pointermove", function (e) {
      if (e.pointerType !== "mouse" || e.buttons) return;
      touched = true;
      var r = box.getBoundingClientRect();
      set(((e.clientX - r.left) / r.width) * 100);
    });
    if (reduce || !("IntersectionObserver" in window)) return;
    var target = Number(input.value);
    box.style.setProperty("--pos", "0%");
    var seen = new IntersectionObserver(function (en) {
      if (!en[0].isIntersecting) return;
      seen.disconnect();
      var t0 = null, dur = 1800;
      function step(t) {
        if (touched) return;
        if (t0 === null) t0 = t;
        var k = Math.min(1, (t - t0) / dur);
        var e = 1 - Math.pow(1 - k, 3);
        pct = target * e; input.value = Math.round(pct);
        box.style.setProperty("--pos", pct + "%");
        if (k < 1) requestAnimationFrame(step);
      }
      setTimeout(function () { requestAnimationFrame(step); }, 350);
    }, { threshold: 0.5 });
    seen.observe(box);
  });
})();
