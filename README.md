# Ametrix Technologies - website

Static marketing site for [ametrixtech.com](https://ametrixtech.com). No build step, no framework.

## Structure

```
index.html            Single-page site (hero, services, approach, about, contact)
404.html              Not-found page
css/styles.css        Styles; light and dark themes via CSS custom properties
js/main.js            Theme toggle, mobile nav, scroll reveal
assets/brand/         Logo lockups (horizontal + stacked, light, dark, mono), icon, favicon
tools/gen_logo.py     Regenerates the lockups from Inter outlines (see docstring)
robots.txt, sitemap.xml
```

## Run locally

Open `index.html` directly, or serve the folder:

```
python -m http.server 8080
```

## Brand implementation notes

- Colors, typography (Inter), and the gem/database symbol follow `ametrix-brandguidelines.md.txt`.
- Light theme: Deep Navy `#0F2D5B`, Electric Blue `#2497E8`, Medium Blue `#459DCE`. The header and hero sit on a near soft white `#F1F4F8`; the page body is a cool gray `#E6EAF0` with white cards, and a darker gray `#D9DFE8` marks alternate sections and the footer, so surfaces have depth.
- Dark theme: Midnight Charcoal `#0E1117`, Warm Cream `#FFEEDB`, Electric Cyan `#22B8E6`, Retro Orange `#FF8A52` (used sparingly for emphasis).
- The wordmark is Inter ExtraBold ("ametrix") and Inter Medium ("technologies") converted to vector outlines, so it renders identically everywhere without the webfont. "technologies" is sized to match the width of "ametrix", as in the logo concept.
- The symbol and the full lockup are inline SVG symbols (`#ametrix-mark`, `#ametrix-logo`) so they recolor with the theme. Geometry: six-sided top, three stacked sections, symmetrical faces, uniform 7-unit stroke, flat color.
- No gradients, shadows, or glow effects. The hero's technical grid is a supporting graphic made of flat lines.
- Theme follows the visitor's system preference and can be toggled; the choice is saved in `localStorage`.

## Before launch

- [ ] Confirm the public contact email (`hello@ametrixtech.com` is used in `index.html` and must be verified).
- [ ] Confirm the service list reflects what the company actively supports.
- [ ] Add `assets/brand/og-image.png` (1200x630) for social sharing, or remove the `og:image` tag.
- [ ] Review all company claims against the brand consistency checklist.

## Deploy

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, S3). Point the host at the repo root and set `404.html` as the not-found page.
