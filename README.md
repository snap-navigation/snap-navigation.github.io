# SNAP — anonymous supplementary material

A local draft of the project page for **SNAP: Semantic Navigation Among Pedestrians**, using the restrained, centered presentation of the Nerfies template. The page includes all three videos, the paper abstract, a method overview, simulation snapshots, a reward summary, and a benchmark excerpt.

## Inspect the draft

From the repository directory:

```bash
python3 scripts/build.py
python3 scripts/preview.py
```

Open **http://127.0.0.1:8000** in your browser. Stop the server with Ctrl+C. After changing HTML/CSS/JS, rerun the build command and refresh the browser. No package installation is needed for building or previewing prepared assets. Alternatively, open `dist/index.html` directly; the HTTP preview is preferable for video playback and seeking.

## Files

- `index.html`: page content.
- `static/css/index.css`: responsive layout and styling.
- `static/js/index.js`: pauses other videos when one starts playing and suppresses the videos’ context menus.
- `assets/`: prepared images, posters, and silent anonymized MP4s used by the page.
- `scripts/build.py`: creates `dist/` using an explicit file allowlist.
- `scripts/preview.py`: serves only `dist/` on loopback, with video byte-range support.
- `scripts/prepare_media.py`: reproducible, source-specific media redaction and export.
- `paper/`, `images/`, `videos/`: original local input files, excluded from Git and the build.

## Media preparation

The page offers no video download links and requests that browsers hide native download controls. Video context menus are suppressed. These measures remove common download shortcuts, but anyone able to play a video can still retrieve its media URL or record playback.

Prepared exports preserve the original frame rate and all frames; no additional speedup is applied. The real-world captions label **1.5×** for the dynamic scene and **5×** for the static scene. The simulation speed is not asserted. All audio tracks and source metadata are removed. H.264/yuv420p exports have their MP4 index at the start for streaming. Posters are extracted from the final sanitized exports.

The dynamic clip uses manually specified full-head tracks with conservative margins, interpolated for every frame. Detail is discarded by reducing each masked region to 2 × 2 samples and smoothly interpolating it back, making the blur irreversible. Background posters/signs are also obscured. In the static clip, the moving onboard-camera inset is blurred to prevent disclosure through distant signage or people; the adjacent BEV map is preserved. The original input files are unchanged.

To regenerate exports, with Python OpenCV/NumPy, FFmpeg and Poppler installed:

```bash
python3 scripts/prepare_media.py
python3 scripts/build.py
```

The video source hashes are checked before processing because the masks are valid only for these exact edits. Changed source clips require new masks and a new visual review. Figures are rasterized from the supplied PDFs to avoid publishing editable layers, embedded source images, or document metadata.

## Before submission or deployment

**Publish only the contents of `dist/`, never the repository root.** Root-based GitHub Pages publishing could expose the original template assets. The local draft has not been published and no GitHub Pages settings have been changed.

Review the complete exported videos, including the first/last frames, at full resolution. Also check whether the visible venue, equipment, or clothing reveals affiliation to someone familiar with the location; face blurring alone cannot guarantee that. Verify the chosen hosting URL and any publicly accessible repository/history do not identify the submitting team. The paper is intentionally not linked or copied into the build. Search-engine exclusion is a request, not access control.

The page has no author names, affiliations, analytics, remote fonts, embeds, or external runtime dependencies. External links are limited to the template attribution and its license.

## Template credit and license

Website adapted from [Nerfies](https://nerfies.github.io/) and its [website source](https://github.com/nerfies/nerfies.github.io). The original template and this adaptation are licensed under [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This template notice does not grant rights to the supplied paper or research media.
