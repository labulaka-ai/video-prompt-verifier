#!/usr/bin/env python3
"""Compare two videos frame-by-frame at normalized timestamps.

Metrics per matched frame pair (all 0..1, higher = more similar):
  - hist: RGB histogram correlation
  - ssim: global grayscale SSIM (mean/var/cov form)
  - phash: perceptual-hash similarity (DCT low-frequency)
Total = mean of frame scores * 100. Pure PIL + numpy, no cv2 needed.
Usage: score_pair.py REF.mp4 GEN.mp4 [--frames 6]
"""
import argparse, json, subprocess, sys, tempfile, os
import numpy as np
from PIL import Image

def extract_frames(video, n, tmp):
    dur = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", video]).decode().strip())
    frames = []
    for i in range(n):
        t = dur * (0.05 + 0.92 * i / max(n - 1, 1))
        out = os.path.join(tmp, f"f{i}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", video,
                        "-frames:v", "1", out], check=True)
        frames.append(Image.open(out).convert("RGB").resize((320, 180)))
    return frames, dur

def hist_corr(a, b):
    def h(img):
        arr = np.asarray(img, dtype=np.float64)
        hs = []
        for c in range(3):
            hist, _ = np.histogram(arr[:, :, c], bins=32, range=(0, 256))
            hs.append(hist / (hist.sum() + 1e-9))
        return np.concatenate(hs)
    ha, hb = h(a), h(b)
    return float(np.corrcoef(ha, hb)[0, 1])

def ssim_global(a, b):
    x = np.asarray(a.convert("L"), dtype=np.float64)
    y = np.asarray(b.convert("L"), dtype=np.float64)
    mx, my = x.mean(), y.mean()
    vx, vy = x.var(), y.var()
    cov = ((x - mx) * (y - my)).mean()
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    s = ((2 * mx * my + c1) * (2 * cov + c2)) / ((mx**2 + my**2 + c1) * (vx + vy + c2))
    return float(max(0.0, min(1.0, s)))

def phash(img):
    g = img.convert("L").resize((32, 32))
    px = np.asarray(g, dtype=np.float64)
    # 2D DCT via matrix multiply
    def dct_mat(n):
        m = np.zeros((n, n))
        for k in range(n):
            for j in range(n):
                m[k, j] = np.cos(np.pi * (2 * j + 1) * k / (2 * n))
        return m
    M = dct_mat(32)
    d = M @ px @ M.T
    low = d[:8, :8]
    med = np.median(low[1:, :])
    return (low > med).flatten()

def phash_sim(a, b):
    ha, hb = phash(a), phash(b)
    return float(1.0 - np.mean(ha != hb))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref"); ap.add_argument("gen")
    ap.add_argument("--frames", type=int, default=6)
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
        rf, rd = extract_frames(args.ref, args.frames, t1)
        gf, gd = extract_frames(args.gen, args.frames, t2)
        per = []
        for i, (a, b) in enumerate(zip(rf, gf)):
            hc, ss, ph = hist_corr(a, b), ssim_global(a, b), phash_sim(a, b)
            per.append({"frame": i, "hist": round(hc, 3), "ssim": round(ss, 3),
                        "phash": round(ph, 3), "score": round((hc + ss + ph) / 3 * 100, 1)})
        total = round(float(np.mean([p["score"] for p in per])), 1)
        print(json.dumps({"ref_duration": rd, "gen_duration": gd,
                          "objective_score": total, "frames": per}, indent=2))

if __name__ == "__main__":
    main()
