/* Scott Beckman Art — small site helpers (no tracking, no outside services). */
(function () {
  // ---- Contact email: the one place to change it. Split in two so simple spam bots don't read it. ----
  var EMAIL_USER = "";   // e.g. "hello"
  var EMAIL_DOMAIN = ""; // e.g. "scottbeckmanart.com"
  var EMAIL = EMAIL_USER && EMAIL_DOMAIN ? EMAIL_USER + "@" + EMAIL_DOMAIN : "";
  window.SBA_EMAIL = EMAIL;

  function mailto(subject, body) {
    var q = [];
    if (subject) q.push("subject=" + encodeURIComponent(subject));
    if (body) q.push("body=" + encodeURIComponent(body));
    return "mailto:" + EMAIL + (q.length ? "?" + q.join("&") : "");
  }

  document.querySelectorAll("[data-mail]").forEach(function (a) {
    if (!EMAIL) return; // falls back to the Contact page link in the HTML
    a.href = mailto(a.getAttribute("data-subject") || "");
    if (a.hasAttribute("data-show-address")) a.textContent = EMAIL;
  });

  // ---- Year in the footer ----
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  // ---- Forms that write an email instead of sending data to a server ----
  document.querySelectorAll("form[data-mailto]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var lines = [];
      var name = "";
      form.querySelectorAll("input, select, textarea").forEach(function (f) {
        if (!f.name || !f.value) return;
        var label = form.querySelector('label[for="' + f.id + '"]');
        var text = label ? label.textContent.replace(/\s*\*$/, "").trim() : f.name;
        if (f.name === "name") name = f.value;
        if (f.tagName === "TEXTAREA") lines.push("", f.value);
        else lines.push(text + ": " + f.value);
      });
      var subject = (form.getAttribute("data-mailto") || "Message from the website") + (name ? " — " + name : "");
      if (!EMAIL) {
        alert("The email address for this site hasn't been set up yet. Please reach Scott on Instagram or Facebook for now.");
        return;
      }
      window.location.href = mailto(subject, lines.join("\n"));
    });
  });

  // ---- Hidden-message reveal slider ----
  document.querySelectorAll(".reveal").forEach(function (box) {
    var input = box.querySelector("input[type=range]");
    if (!input) return;
    var pending = false;
    function apply() { pending = false; box.style.setProperty("--pos", input.value + "%"); }
    input.addEventListener("input", function () { if (!pending) { pending = true; requestAnimationFrame(apply); } });
    apply();
  });

  // ---- Subject filters on the Work page ----
  var bar = document.querySelector(".filters");
  if (bar) {
    var items = document.querySelectorAll(".gallery .art");
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      bar.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      var f = b.getAttribute("data-filter");
      items.forEach(function (it) {
        var show = f === "all" || it.getAttribute("data-subject") === f || (f === "available" && it.hasAttribute("data-available"));
        it.hidden = !show;
        var a = it.querySelector("a");
        if (a) a.classList.toggle("is-hidden", !show);
      });
    });
  }
})();
