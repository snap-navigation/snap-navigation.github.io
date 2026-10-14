#!/usr/bin/env python3
"""Build an allowlisted static site; never copy the repository wholesale."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
FILES = (
    "index.html", "static/css/index.css", "static/js/index.js", "assets/favicon.svg",
    "assets/images/architecture.png", "assets/images/simulation-snapshots.png",
    "assets/images/dynamic-poster.jpg", "assets/images/static-poster.jpg",
    "assets/images/simulation-poster.jpg", "assets/videos/dynamic-scene.mp4",
    "assets/videos/static-scene.mp4", "assets/videos/simulation.mp4",
)


def main():
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("Missing prepared assets. Run scripts/prepare_media.py first: " + ", ".join(missing))
    # Fail rather than accidentally serving files left by a different build.
    if DIST.is_symlink():
        raise SystemExit("dist must be a local directory, not a symlink.")
    if DIST.exists():
        extra = [str(p.relative_to(DIST)) for p in DIST.rglob("*")
                 if p.is_file() and str(p.relative_to(DIST)) not in (*FILES, ".nojekyll", "robots.txt")]
        if extra or any(p.is_symlink() for p in DIST.rglob("*")):
            raise SystemExit("Unexpected files/symlinks in dist. Review them before rebuilding: " + ", ".join(extra))
    for name in FILES:
        source = ROOT / name
        if source.is_symlink():
            raise SystemExit(f"Refusing symlink: {name}")
        target = DIST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (DIST / ".nojekyll").write_text("")
    (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    size = sum((DIST / name).stat().st_size for name in FILES)
    print(f"Built dist/: {len(FILES)} allowlisted files, {size/1_000_000:.1f} MB.")
    print("Preview: python3 scripts/preview.py")


if __name__ == "__main__":
    main()
