# Definitive pad measurement for A7670 figures 3 (bot view), 4 (footprint), 5 (stencil)
# Strategy: detect pad-like components, calibrate scale from inner-grid pitch (3.80 mm),
# report pad centers in mm relative to module TL corner (fitted from pad clusters).
import numpy as np
from PIL import Image
from scipy import ndimage
import os

D = r"D:\Tracker\ST909B-4G\Datasheet\pdf_render"

def comps(img_path, mode, min_px=8):
    img = np.array(Image.open(img_path).convert("L"))
    bw = img < 128
    lab, n = ndimage.label(bw)
    sl = ndimage.find_objects(lab)
    out = []
    for i, s in enumerate(sl, 1):
        y0, y1 = s[0].start, s[0].stop
        x0, x1 = s[1].start, s[1].stop
        w, h = x1 - x0, y1 - y0
        a = int((lab[s] == i).sum())
        if w < min_px or h < min_px or a < 40:
            continue
        fill = a / (w * h)
        out.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, w=w, h=h, a=a, fill=fill))
    return out

def cluster_report(name, path, sel, expect_inner_pitch=3.80):
    cs = comps(path, sel)
    # inner pads are the biggest squares; find pitch from them
    # first coarse filter: keep comps with 0.45mm..3.2mm bbox (needs scale guess ~ any)
    # estimate scale: try all pairs? simpler: assume biggest square-ish comps are inner pads
    sq = [c for c in cs if 0.7 < c["w"] / c["h"] < 1.4 and c["w"] > 25]
    sq.sort(key=lambda c: -c["w"])
    # take median gap of the top ~30 biggest squares' x-centers differences
    big = sq[:32]
    cen = sorted((c["x0"] + c["x1"]) / 2 for c in big)
    diffs = [b - a for a, b in zip(cen, cen[1:]) if b - a > 40]
    if not diffs:
        print(name, "FAIL: no pitch")
        return
    diffs.sort()
    pitch_px = np.median(diffs)
    S = pitch_px / expect_inner_pitch
    print(f"== {name}: pitch_px={pitch_px:.1f} scale={S:.2f} px/mm, comps={len(cs)}")

    # classify all comps in mm
    mm = []
    for c in cs:
        w, h = c["w"] / S, c["h"] / S
        if not (0.30 < w < 3.4 and 0.30 < h < 3.4):
            continue
        cx = (c["x0"] + c["x1"]) / 2 / S
        cy = (c["y0"] + c["y1"]) / 2 / S
        mm.append(dict(x=cx, y=cy, w=w, h=h, fill=c["fill"], a=c["a"]))
    # fit module TL: use inner grid: pads at 4.40+k*3.80. Find best offset via median of (x mod 3.80)
    # simpler: known model centers 4.40..19.60 -> use the 20 biggest square comps
    bigmm = sorted([m for m in mm if 0.8 < m["w"] < 3.2 and 0.8 < m["h"] < 3.2],
                   key=lambda m: -m["w"] * m["h"])[:26]
    if len(bigmm) < 10:
        print("  too few big comps")
        return
    xs = sorted(m["x"] for m in bigmm)
    ys = sorted(m["y"] for m in bigmm)
    # offset so that cluster of 5 distinct x values starts at 4.40
    # find the leftmost dense cluster
    def grid_offset(vals):
        # vals are px/mm centers; expected set {4.40,8.20,12.00,15.80,19.60}+o
        best = None
        for o in np.arange(min(vals) - 5.2, min(vals) + 0.2, 0.02):
            err = 0.0
            for v in vals:
                d = min(abs(v - (o + t)) for t in (4.40, 8.20, 12.00, 15.80, 19.60))
                err += d
            if best is None or err < best[1]:
                best = (o, err)
        return best
    ox, ex = grid_offset(xs)
    oy, ey = grid_offset(ys)
    print(f"  module TL fit: ox={ox:.2f} (err {ex:.2f}) oy={oy:.2f} (err {ey:.2f})")

    # shift all comps to module coords
    for m in mm:
        m["x"] -= ox
        m["y"] -= oy

    # report by region
    def region(m):
        x, y, w, h = m["x"], m["y"], m["w"], m["h"]
        if x < 2.0 and 0.0 < y < 24.0:
            return "L"
        if x > 22.0 and 0.0 < y < 24.0:
            return "R"
        if y < 2.0 and 0.0 < x < 24.0:
            return "T"
        if y > 22.0 and 0.0 < x < 24.0:
            return "B"
        if 3.0 < x < 21.0 and 3.0 < y < 21.0:
            return "I"
        return "?"

    groups = {}
    for m in mm:
        groups.setdefault(region(m), []).append(m)
    for r in ["T", "B", "L", "R", "I", "?"]:
        lst = groups.get(r, [])
        if not lst:
            continue
        lst.sort(key=lambda m: (m["y"], m["x"]) if r in "TB" else (m["x"], m["y"]))
        print(f"  -- region {r}: {len(lst)}")
        for m in lst:
            print(f"     c=({m['x']:6.2f},{m['y']:6.2f})  size {m['w']:4.2f}x{m['h']:4.2f} fill {m['fill']:.2f}")

print("### FIGURE 4 footprint (p20)")
cluster_report("fig4", os.path.join(D, "a7670_p20_fig600.png"), "hatch")
print()
print("### FIGURE 5 stencil (p21 img1)")
cluster_report("stencil", os.path.join(D, "a7670_p21_img1.png"), "solid")
print()
print("### FIGURE 3 bot view (p19)")
cluster_report("bot", os.path.join(D, "a7670_p19_fig600.png"), "ring")
