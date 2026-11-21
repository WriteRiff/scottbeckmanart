# Scott Beckman Art website

Scott Michael Beckman's art portfolio, scottbeckmanart.com. A plain static site (HTML, CSS, a little JavaScript) hosted free on GitHub Pages. It replaced the old Squarespace site in November 2026.

## How it's organized

- `index.html`, `work/`, `commissions/`, `about/`, `contact/`: the pages. Each keeps its own text.
- `content/artworks.json`: the list of paintings (title, size, subject, description, available or not, price).
- `assets/`: styles, scripts, fonts, images. `assets/js/site.js` holds the Formspree form address (top of the file); `assets/js/night.js` runs the animations.
- `portfolio/`, `availableart/`, `home/`, `new-page/`: forward old Squarespace links to the new pages.
- `tools/make_images.py`: makes web-sized copies of paintings. `tools/build.py`: writes every page (home, work, commissions, about, contact) from `artworks.json`. (The three trial looks were removed when the site went live; they're in git history, commit 91d56bf.)
- `CNAME`: tells GitHub Pages the site's address (scottbeckmanart.com).
- `privacy/`: privacy page. `sitemap.xml`, `robots.txt` and the old-address forwards are also written by `tools/build.py`.
- `.github/workflows/uptime.yml`: downtime alarm, every 5 minutes on GitHub (Pushover emergency alert, repeats until acknowledged; one message when it's back). `.github/workflows/monthly-report.yml`: report to Scott's phone on the 1st of each month. Both need the repo secrets `PUSHOVER_USER`, `PUSHOVER_TOKEN` (and `CF_API_TOKEN` for visitor numbers), entered by Scott in Settings → Secrets and variables → Actions.

## Accounts and dates

- Domain: GoDaddy, **renews Jan 10, 2027** ($22.99/yr), auto-renew on, domain lock on, privacy on. DNS at GoDaddy: 4 A records to GitHub Pages, `www` CNAME to writeriff.github.io, Google verification TXT record (keep it).
- Hosting: GitHub Pages (WriteRiff account, free). HTTPS certificate renewed by GitHub automatically.
- Forms: Formspree (free plan, Scott's account). Visitor counts: Cloudflare Web Analytics (Scott's account). Search: Google Search Console (Scott's Google account).
- `archive/` (on Scott's PC only, not in git): full saved copy of the old Squarespace site.

## Adding a painting

1. Put the original photo in `archive/images/` (or anywhere) and add a line for it in `tools/make_images.py`.
2. Run `python tools/make_images.py`.
3. Add the painting to `content/artworks.json`.
4. Run `python tools/build.py`, check locally, commit and push. GitHub Pages updates in a minute or two.

## Previewing locally

`python -m http.server 8130` in this folder, then open http://127.0.0.1:8130.
