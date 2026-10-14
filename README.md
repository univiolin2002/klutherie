# klutherie.com

A register of Korean makers of stringed instruments and bows.

- `makers.py` — all maker, dealer and news records. Edit this to add or change content.
- `build.py` — generates every HTML page from `makers.py`. Run `python3 build.py`.
- `images/makers/` — maker portraits (`slug-480.jpg`, `slug-960.jpg`, `slug-full.jpg`).
- `styles.css` — the one stylesheet.

Hosted on Cloudflare Pages from the `main` branch; no build step needed (output is committed).
