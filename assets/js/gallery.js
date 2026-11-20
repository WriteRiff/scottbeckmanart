// Large-image viewer (PhotoSwipe, MIT license). Any element with data-gallery becomes a viewer group.
import PhotoSwipeLightbox from "../vendor/photoswipe/photoswipe-lightbox.esm.min.js";

document.querySelectorAll("[data-gallery]").forEach((gallery) => {
  const lightbox = new PhotoSwipeLightbox({
    gallery,
    children: "a[data-pswp-width]:not(.is-hidden)",
    pswpModule: () => import("../vendor/photoswipe/photoswipe.esm.min.js"),
    bgOpacity: 1,
    showHideAnimationType: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "none" : "zoom",
    imageClickAction: "zoom",
    tapAction: "toggle-controls",
    paddingFn: (vp) => (vp.x < 700 ? { top: 16, bottom: 72, left: 0, right: 0 } : { top: 40, bottom: 88, left: 60, right: 60 }),
  });
  lightbox.on("uiRegister", () => {
    lightbox.pswp.ui.registerElement({
      name: "custom-caption",
      appendTo: "root",
      onInit: (el, pswp) => {
        pswp.on("change", () => {
          const a = pswp.currSlide.data.element;
          el.textContent = "";
          if (!a) return;
          const t = a.getAttribute("data-title");
          const m = a.getAttribute("data-meta");
          if (t) { const s = document.createElement("strong"); s.textContent = t; el.appendChild(s); }
          if (m) el.appendChild(document.createTextNode(m));
        });
      },
    });
  });
  lightbox.init();
});
