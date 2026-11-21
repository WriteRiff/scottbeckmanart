/* Scott Beckman Art — small site helpers (no cookies). */
(function () {
  // ---- Form service: the one place to change it. ----
  // Formspree form address, like "https://formspree.io/f/abcdwxyz" (shown on the form's page in Formspree).
  // Not a secret: it's meant to sit in a public web page.
  var FORM_ENDPOINT = "https://formspree.io/f/xdeglzoa";

  // ---- Year in the footer ----
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  // ---- "Ask about this painting" opens the contact form with the title filled in ----
  var params = new URLSearchParams(location.search);
  var painting = params.get("painting");
  var msg = document.getElementById("m-msg");
  if (painting && msg && !msg.value) msg.value = "Hi Scott, I'm interested in \"" + painting + "\". ";

  // ---- Forms: send to Formspree, show the result on the page ----
  document.querySelectorAll("form[data-form]").forEach(function (form) {
    var status = form.querySelector(".form-status");
    var button = form.querySelector("button[type=submit]");
    function say(text, ok) {
      if (!status) return;
      status.textContent = text;
      status.className = "form-status " + (ok ? "ok" : "err");
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      if (!FORM_ENDPOINT) {
        say("The message form is being set up. Please reach Scott on Instagram or Facebook for now.", false);
        return;
      }
      var data = new FormData(form);
      var name = data.get("name") || "";
      data.append("_subject", form.getAttribute("data-form") + (name ? " from " + name : ""));
      button.disabled = true;
      say("Sending…", true);
      fetch(FORM_ENDPOINT, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          form.reset();
          say("Thank you! Your message is on its way to Scott, and he'll reply by email.", true);
        })
        .catch(function () {
          say("Sorry, that didn't send. Please try again in a minute, or reach Scott on Instagram or Facebook.", false);
        })
        .then(function () { button.disabled = false; });
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
