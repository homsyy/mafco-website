# MAFCO website

The website for www.mafcotrading.com. A static site hosted free on GitHub Pages.

## What is where

| Path | What it is |
|---|---|
| `docs/` | The finished website. GitHub Pages serves this folder. Do not edit by hand; it is rebuilt. |
| `data/brands.json` | Every brand: name, logo file, exclusive or stocked, description, ranges, facts. |
| `data/site.json` | Phone, email, location, domain. |
| `build.py` | Page text and layout for home, brands, story, suppliers and contact. Builds `docs/`. |
| `src/style.css` | Design: colours, type and layout, following the MAFCO Brand Guidelines. |
| `src/assets/` | MAFCO logo, road line, fonts, photos and brand logos. |

## Making a change

1. Edit the file (for example add a brand to `data/brands.json` and drop its logo in `src/assets/brands/`).
2. Run `python3 build.py`.
3. Commit and push. The live site updates in about a minute.

`"exclusive": true` puts a brand under "Exclusive agencies"; `false` puts it under "Also in our range".

## GitHub Pages settings

Settings → Pages → Deploy from a branch → `main` → `/docs`. Custom domain: `www.mafcotrading.com`.
