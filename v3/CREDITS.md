# v3 "Color Field": credits

## Fonts (self-hosted in `v3/fonts/`)
| Font | Files | License | Source |
|---|---|---|---|
| Bricolage Grotesque (variable, weight + optical size), by Mathieu Triay | `bricolage-grotesque-latin-opsz-normal.woff2` | SIL Open Font License 1.1 (commercial use OK; keep license notice if redistributed as a font) | https://fonts.google.com/specimen/Bricolage+Grotesque · downloaded from https://cdn.jsdelivr.net/npm/@fontsource-variable/bricolage-grotesque@5.3.0/ |
| Instrument Serif, by Rodrigo Fuenzalida and Jordan Egstad | `instrument-serif-latin-400-italic.woff2`, `instrument-serif-latin-400-normal.woff2` | SIL Open Font License 1.1 | https://fonts.google.com/specimen/Instrument+Serif · downloaded from https://cdn.jsdelivr.net/npm/@fontsource/instrument-serif@5.3.0/ |

## Shared, used read-only
- PhotoSwipe 5 (MIT) from `../assets/vendor/photoswipe/`, via `../assets/js/gallery.js`.
- `../assets/js/site.js` for forms, reveal slider, filters, footer year.

## Build-only tools (not shipped to visitors)
- `tools/colors.py`: Pillow + NumPy pick each painting's colors into `tools/colors.json` and `css/colors.css`.
- `tools/build.py`: writes the five pages from `content/artworks.json` and the colors.
