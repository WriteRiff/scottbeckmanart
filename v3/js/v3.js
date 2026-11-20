/* Look v3 "Color Field": color rooms, scroll rises, playful hidden-message toggles, work-page views. */
(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasIO = "IntersectionObserver" in window;

  // ---- 1. Page color follows the painting in view: fixed layers cross-fade (opacity only) ----
  var rooms = Array.prototype.slice.call(document.querySelectorAll("[data-field]"));
  var fieldsOff = false, setField = function () {};
  if (rooms.length && hasIO) {
    var box = document.createElement("div");
    box.className = "fields";
    box.setAttribute("aria-hidden", "true");
    document.body.insertBefore(box, document.body.firstChild);
    var cache = {}, layers = [];
    var layerFor = rooms.map(function (r) {
      var c = getComputedStyle(r).getPropertyValue("--field").trim() || "#fbfbf9";
      if (!(c in cache)) {
        var i = document.createElement("i");
        i.style.background = c;
        box.appendChild(i);
        cache[c] = layers.push(i) - 1;
      }
      return cache[c];
    });
    var cur = -2;
    setField = function (n) {
      var li = n < 0 ? -1 : layerFor[n];
      if (li === cur) return;
      cur = li;
      layers.forEach(function (l, k) { l.classList.toggle("on", k === li); });
    };
    // Start on the first room without a fade, so nothing flickers on load.
    box.classList.add("instant");
    layers.forEach(function (l) { l.style.transition = "none"; });
    setField(0);
    requestAnimationFrame(function () { requestAnimationFrame(function () { layers.forEach(function (l) { l.style.transition = ""; }); }); });
    var fio = new IntersectionObserver(function (es) {
      if (fieldsOff) return;
      es.forEach(function (e) { if (e.isIntersecting) setField(rooms.indexOf(e.target)); });
    }, { rootMargin: "-50% 0px -50% 0px" });
    rooms.forEach(function (r) { fio.observe(r); });
  } else {
    document.documentElement.classList.add("no-fields");
  }

  // ---- 2. Things rise gently into place as they scroll in ----
  var risers = document.querySelectorAll(".rise, .chips.pop, .prices");
  if (!hasIO || reduce) {
    risers.forEach(function (el) { el.classList.add("in"); });
  } else {
    var rio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); rio.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    risers.forEach(function (el) { rio.observe(el); });
  }

  // ---- 3. Hidden message: crisp "Painting / Message" toggles and a one-time playful peek ----
  document.querySelectorAll(".reveal").forEach(function (rv) {
    var input = rv.querySelector("input[type=range]");
    var group = rv.parentNode.querySelector(".toggle");
    if (!input) return;
    var t;
    function press(v) {
      if (!group) return;
      group.querySelectorAll("button").forEach(function (b) {
        var to = +b.getAttribute("data-to");
        b.setAttribute("aria-pressed", String((to === 0 && v <= 2) || (to === 100 && v >= 98)));
      });
    }
    function snapTo(v) {
      if (!reduce) rv.classList.add("snap");
      input.value = v;
      input.dispatchEvent(new Event("input"));
      press(v);
      clearTimeout(t);
      t = setTimeout(function () { rv.classList.remove("snap"); }, 760);
    }
    if (group) group.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (b) { touched = true; snapTo(+b.getAttribute("data-to")); }
    });
    // Dragging follows the finger directly: no easing.
    var touched = false;
    ["pointerdown", "keydown", "touchstart"].forEach(function (ev) {
      input.addEventListener(ev, function () { touched = true; clearTimeout(t); rv.classList.remove("snap"); }, { passive: true });
    });
    input.addEventListener("input", function () { if (!rv.classList.contains("snap")) press(+input.value); });
    press(+input.value);
    if (!reduce && hasIO && rv.hasAttribute("data-peek")) {
      var start = +input.value;
      var pio = new IntersectionObserver(function (es) {
        if (!es[0].isIntersecting) return;
        pio.disconnect();
        setTimeout(function () {
          if (touched) return;
          snapTo(12);
          setTimeout(function () { if (!touched) snapTo(start); }, 1500);
        }, 500);
      }, { threshold: 0.6 });
      pio.observe(rv);
    }
  });

  // ---- 4. Work page: Rooms / Grid view and a live count ----
  var list = document.querySelector(".rooms");
  if (list) {
    var count = document.querySelector("[data-count]");
    var updateCount = function () {
      var n = list.querySelectorAll(".room:not([hidden])").length;
      if (count) count.textContent = n + (n === 1 ? " painting" : " paintings");
    };
    var bar = document.querySelector(".filters");
    if (bar) bar.addEventListener("click", function () { setTimeout(function () {
      updateCount();
      list.querySelectorAll(".room:not([hidden]) .rise").forEach(function (el) { el.classList.add("in"); });
    }, 0); });
    var sw = document.querySelector(".viewsw");
    if (sw) sw.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      var grid = b.getAttribute("data-view") === "grid";
      sw.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      list.classList.toggle("is-grid", grid);
      list.querySelectorAll(".rise").forEach(function (el) { el.classList.add("in"); });
      fieldsOff = grid;
      if (grid) setField(0);
    });
    updateCount();
  }
})();
