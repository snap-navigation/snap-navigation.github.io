# SNAP

A local draft of the project page for **SNAP: Semantic Navigation Among Pedestrians**, using the restrained, centered presentation of the Nerfies template. The page includes all three videos, the paper abstract, a method overview, simulation snapshots, a reward summary, and a benchmark excerpt.

## Inspect the draft

From the repository directory:

```bash
python3 scripts/build.py
python3 scripts/preview.py
```

Open **http://127.0.0.1:8000** in your browser. Stop the server with Ctrl+C. After changing HTML/CSS/JS, rerun the build command and refresh the browser.

## Files

- `index.html`: page content.
- `static/css/index.css`: responsive layout and styling.
- `static/js/index.js`: pauses other videos when one starts playing and suppresses the videos’ context menus.
- `assets/`: prepared images, posters, and silent anonymized MP4s used by the page.
- `scripts/build.py`: creates `dist/` using an explicit file allowlist.
- `scripts/preview.py`: serves only `dist/` on loopback, with video byte-range support.
- `scripts/prepare_media.py`: reproducible, source-specific media redaction and export.
- `paper/`, `images/`, `videos/`: original local input files, excluded from Git and the build.

## Template credit and license

Website adapted from [Nerfies](https://nerfies.github.io/) and its [website source](https://github.com/nerfies/nerfies.github.io). The original template and this adaptation are licensed under [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This template notice does not grant rights to the supplied paper or research media.
