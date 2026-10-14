#!/usr/bin/env python3
"""Prepare review assets from the original, local-only media.

Requires OpenCV, NumPy, ffmpeg, ffprobe and pdftoppm. The manual head tracks
are specific to the supplied dynamic clip; never reuse them on another edit.
Published files contain only rendered pixels, no source media or audio.
"""
from pathlib import Path
import hashlib
import subprocess

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
SOURCE_HASHES = {
    "dynamic_scene": "ed2ce62cdee324125b2eae28f7330c2082a7a04f71b76393425f43b5a6e1212b",
    "static_scene": "38e18f73d35166e32a6dea990a251c45b5dfa36f15296d25046a7d58dc0a601c",
    "simulation": "9368629b9c08699224231e49769b00d67db3a60bee23088338a104d3cf1baf6e",
}

# Coordinates on a 640 x 360 reference frame, sampled every half-second.
# Each mask covers the full head with a generous margin, including profiles.
BROWN_X = [420,385,350,330,316,313,314,316,318,318,319,319,319,315,316,316,320,332,349,363,375,383,390,400,407,411,425,441,477,534,615,690,730,730]
BROWN_Y = [126,130,130,133,135,135,135,135,135,135,135,135,135,135,137,136,134,131,130,128,126,127,127,126,126,124,120,115,115,104,95,70,70,70]
GREEN_X = [740,680,525,440,386,327,301,274,250,242,213,172,143,123,110,155,224,311,374,411,437,463,458,441,367,269,175,136,132,183,222,230,209,185]
GREEN_Y = [50,60,90,113,124,128,131,133,133,135,131,129,123,123,118,107,105,110,119,120,123,126,122,120,112,103,100,112,121,125,130,132,133,133]


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def obscure(frame, box, cells=2, ellipse=False):
    """Irreversibly discard fine detail, then interpolate to a soft blur."""
    left, top, right, bottom = box
    x1, y1, x2, y2 = [int(v) for v in box]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
    if x2 <= x1 or y2 <= y1:
        return
    roi = frame[y1:y2, x1:x2]
    tiny = cv2.resize(roi, (cells, cells), interpolation=cv2.INTER_AREA)
    blurred = cv2.resize(tiny, (x2-x1, y2-y1), interpolation=cv2.INTER_LINEAR)
    if ellipse:
        yy, xx = np.mgrid[y1:y2, x1:x2]
        radius = np.sqrt(((xx-(left+right)/2)/((right-left)/2))**2
                         + ((yy-(top+bottom)/2)/((bottom-top)/2))**2)
        # Full redaction in the central 85%; feather only the outer margin.
        alpha = np.clip((1-radius)/.15, 0, 1)[..., None]
        blurred = (blurred * alpha + roi * (1-alpha)).astype(np.uint8)
    frame[y1:y2, x1:x2] = blurred


def sanitize(frame, name, time):
    # Posters, boards and small signs in the stationary external camera view.
    if name == "dynamic_scene":
        bev = frame[:381, :333].copy()
        for box in [(0,360,180,520),(350,380,590,535),(960,435,1080,550)]:
            obscure(frame, box)
        samples = np.arange(len(BROWN_X)) / 2
        for xs, ys in [(BROWN_X, BROWN_Y), (GREEN_X, GREEN_Y)]:
            x = np.interp(time, samples, xs) * 3
            y = np.interp(time, samples, ys) * 3
            obscure(frame, (x-108, y-126, x+108, y+126), ellipse=True)
        # Restore the opaque map overlay; no camera imagery exists in it.
        frame[:381, :333] = bev
    elif name == "static_scene":
        # The moving onboard-camera inset can expose distant signs/people.
        # Blur it completely while retaining the adjacent semantic BEV map.
        obscure(frame, (0,0,362,418), cells=5)
        for box in [(0,418,80,490),(880,370,930,450)]:
            obscure(frame, box)
    return frame


def video(name, output_name):
    source = ROOT / "videos" / f"{name}.mp4"
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_HASHES[name]:
        raise RuntimeError(f"{name} changed; its redactions must be reviewed again.")
    cap = cv2.VideoCapture(str(source))
    width, height = [int(cap.get(p)) for p in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT)]
    fps = cap.get(cv2.CAP_PROP_FPS)
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if (width, height, fps) != (1920, 1080, 30.0):
        raise RuntimeError("Source dimensions/rate changed; review redaction coordinates.")
    target = OUT / "videos" / f"{output_name}.mp4"
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{width}x{height}",
               "-r", str(fps), "-i", "-", "-an", "-map_metadata", "-1",
               "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-threads", "4",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    frame_no = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = sanitize(frame, name, frame_no / fps)
            process.stdin.write(frame.tobytes())
            frame_no += 1
        process.stdin.close()
        if process.wait() != 0 or frame_no != count:
            raise RuntimeError(f"Incomplete export: {name}, {frame_no}/{count} frames")
    finally:
        cap.release()
        if process.poll() is None:
            process.kill()
    # Poster comes from the final, compressed and sanitized video only.
    poster_name = {"dynamic_scene": "dynamic", "static_scene": "static", "simulation": "simulation"}[name]
    poster_time = {"dynamic_scene": "10", "static_scene": "3", "simulation": "2"}[name]
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", poster_time,
        "-i", target, "-frames:v", "1", "-vf", "scale=1280:-1", "-q:v", "3",
        "-update", "1", OUT / "images" / f"{poster_name}-poster.jpg")
    print(f"Prepared {target.name}: {frame_no} frames, {frame_no/fps:.2f}s", flush=True)


def main():
    for folder in ("images", "videos"):
        (OUT / folder).mkdir(parents=True, exist_ok=True)
    for source, target in [("architecture_overview", "architecture"), ("sim_snapshots", "simulation-snapshots")]:
        # Rasterize rather than shipping editable PDF/SVG metadata and layers.
        run("pdftoppm", "-scale-to", "2800", "-png", "-singlefile",
            ROOT / "images" / f"{source}.pdf", OUT / "images" / target)
    for source, target in [("dynamic_scene", "dynamic-scene"), ("static_scene", "static-scene"), ("simulation", "simulation")]:
        video(source, target)


if __name__ == "__main__":
    main()
