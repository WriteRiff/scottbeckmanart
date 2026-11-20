# Scott Beckman Art website

Scott Michael Beckman's art portfolio, scottbeckmanart.com. A plain static site (HTML, CSS, a little JavaScript) hosted free on GitHub Pages. It replaced the old Squarespace site in November 2026.

## How it's organized

- `index.html`, `work/`, `commissions/`, `about/`, `contact/`: the pages. Each keeps its own text.
- `content/artworks.json`: the list of paintings (title, size, subject, description, available or not, price).
- `assets/`: styles, scripts, fonts, images. `assets/js/site.js` holds the Formspree form address (top of the file); `assets/js/night.js` runs the animations.
- `portfolio/`, `availableart/`, `home/`, `new-page/`: forward old Squarespace links to the new pages.
- `tools/make_images.py`: makes web-sized copies of paintings. `tools/build.py`: writes every page (home, work, commissions, about, contact) from `artworks.json`. The folders `v1/`, `v2/`, `v3/` and `versions/` are the three trial looks, kept for comparison until Scott is happy.
- `archive/` (on Scott's PC only, not in git): full saved copy of the old Squarespace site.

## Adding a painting

1. Put the original photo in `archive/images/` (or anywhere) and add a line for it in `tools/make_images.py`.
2. Run `python tools/make_images.py`.
3. Add the painting to `content/artworks.json`.
4. Run `python tools/build.py`, check locally, commit and push. GitHub Pages updates in a minute or two.

## Previewing locally

`python -m http.server 8130` in this folder, then open http://127.0.0.1:8130.
