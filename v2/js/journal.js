/* v2 "Studio Journal": brushstroke reveals, slow parallax drift, numerals filling in,
   a one-time "wipe" hint on the hidden-message slider, and the Work page's alternating layout.
   Everything is visible without this file (the html.js class gates the hiding). */
(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var root = document.documentElement;

  // ---- Scroll reveals: brush wipe (.wipe), gentle rise (.rise), step numerals (.steps li) ----
  var targets = document.querySelectorAll(".wipe, .rise, .steps li");
  function finish(el) {
    el.classList.add("is-in");
    if (el.classList.contains("wipe")) {
      // drop the mask once the stroke has fully crossed, so nothing is left half-way
      var done = function (e) { if (e && e.target !== el) return; el.classList.add("is-done"); el.removeEventListener("transitionend", done); };
      el.addEventListener("transitionend", done);
      setTimeout(done, 3200);
    }
  }
  if (reduce || !("IntersectionObserver" in window)) {
    targets.forEach(function (el) { el.classList.add("is-in", "is-done"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { io.unobserve(en.target); finish(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    // Start only once the fonts are in and the first frames are painted, so a stroke never
    // stutters on page load or re-flows mid-wipe when the web font swaps in.
    var started = false;
    var start = function () {
      if (started) return; started = true;
      requestAnimationFrame(function () { requestAnimationFrame(function () {
        targets.forEach(function (el) { io.observe(el); });
      }); });
    };
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(start);
    setTimeout(start, 1200);
  }

  // ---- Slow parallax drift between overlapping layers (transform only, once per frame) ----
  var drifters = Array.prototype.slice.call(document.querySelectorAll("[data-drift]"));
  if (!reduce && drifters.length) {
    var visible = new Set();
    var vis = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) visible.add(en.target); else visible.delete(en.target); });
      queue();
    }, { rootMargin: "20% 0px 20% 0px" });
    drifters.forEach(function (el) { vis.observe(el); });
    var ticking = false;
    function queue() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
    function update() {
      ticking = false;
      var vh = window.innerHeight;
      var scale = window.innerWidth < 760 ? 0.5 : 1;
      visible.forEach(function (el) {
        var r = el.getBoundingClientRect();
        // offsetTop-independent: measure without our own transform
        var current = el._driftY || 0;
        var center = r.top - current + r.height / 2;
        var y = (center - vh / 2) * parseFloat(el.getAttribute("data-drift")) * scale;
        y = Math.round(y * 10) / 10;
        if (y !== current) { el._driftY = y; el.style.transform = "translate3d(0," + y + "px,0)"; }
      });
    }
    window.addEventListener("scroll", queue, { passive: true });
    window.addEventListener("resize", queue);
  }

  // ---- Hidden-message slider: one slow sweep the first time it is seen, to show it moves ----
  if (!reduce && "IntersectionObserver" in window) {
    document.querySelectorAll(".reveal").forEach(function (box) {
      var input = box.querySelector("input[type=range]");
      if (!input) return;
      var touched = false;
      ["pointerdown", "keydown", "input"].forEach(function (t) { input.addEventListener(t, function () { touched = true; }); });
      var once = new IntersectionObserver(function (entries) {
        if (!entries[0].isIntersecting) return;
        once.disconnect();
        var end = parseFloat(input.value), start = 96, t0 = null, dur = 1700;
        box.style.setProperty("--pos", start + "%");
        function step(ts) {
          if (touched) return;
          if (t0 === null) t0 = ts;
          var p = Math.min(1, (ts - t0) / dur);
          var e = p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
          box.style.setProperty("--pos", (start + (end - start) * e).toFixed(2) + "%");
          if (p < 1) requestAnimationFrame(step);
          else box.style.setProperty("--pos", end + "%");
        }
        setTimeout(function () { requestAnimationFrame(step); }, 350);
      }, { threshold: 0.5 });
      once.observe(box);
    });
  }

  // ---- Work page: alternate sides for whatever paintings are showing ----
  var gallery = document.querySelector(".gallery");
  function relayout() {
    if (!gallery) return;
    var i = 0;
    gallery.querySelectorAll(".art").forEach(function (a) {
      if (a.hidden) return;
      a.classList.toggle("is-alt", i % 2 === 1);
      i++;
    });
  }
  relayout();
  var bar = document.querySelector(".filters");
  if (bar) bar.addEventListener("click", function () { setTimeout(relayout, 0); });
})();
