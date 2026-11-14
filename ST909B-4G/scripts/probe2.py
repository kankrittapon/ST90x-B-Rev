# Probe pad rows/cols per figure with gap-filling via density check.
# Answers: how many pads per edge, span (16.00 vs 22.00), sizes, depths.
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree
import os

D = r"D:\Tracker\ST909B-4G\Datasheet\pdf_render"

def load(path):
    return np.array(Image.open(path).convert("L")) < 128

def boxes(bw, min_area=40):
    lab, n = ndimage.label(bw)
    sl = ndimage.find_objects(lab)
    out = []
    for i, s in enumerate(sl, 1):
        y0, y1 = s[0].start, s[0].stop
        x0, x1 = s[1].start, s[1].stop
        a = int((lab[s] == i).sum())
        if a < min_area:
            continue
        out.append((x0, y0, x1, y1, a))
    return out

def density(bw, cx, cy, r):
    x0, x1 = max(0, int(cx - r)), int(cx + r)
    y0, y1 = max(0, int(cy - r)), int(cy + r)
    win = bw[y0:y1, x0:x1]
    if win.size == 0:
        return 0.0
    return win.mean()

def cluster_1d(vals, tol):
    vals = sorted(vals)
    groups = []
    cur = [vals[0]]
    for v in vals[1:]:
        if v - cur[-1] <= tol:
            cur.append(v)
        else:
            groups.append(cur)
            cur = [v]
    groups.append(cur)
    return groups

def probe(name, path, filt, tol_mm=0.45):
    bw = load(path)
    bb = boxes(bw)
    cands = []
    for (x0, y0, x1, y1, a) in bb:
        w, h = x1 - x0, y1 - y0
        f = a / (w * h)
        if filt(w, h, f):
            cands.append(((x0 + x1) / 2, (y0 + y1) / 2, w, h))
    # --- find pitch scale: use nearest-neighbor distance mode among candidates
    pts = np.array([(c[0], c[1]) for c in cands])
    t = cKDTree(pts)
    dd, _ = t.query(pts, k=2)
    nn = np.sort(dd[:, 1])
    nn = nn[(nn > 8) & (nn < np.percentile(nn, 55))]
    P = float(np.median(nn)) if len(nn) else 0.0
    print(f"== {name}: cands={len(cands)} nn_pitch={P:.1f}px")
    # --- cluster into rows (y-bands) and cols (x-bands)
    ys = [c[1] for c in cands]
    yrows = cluster_1d(ys, tol_mm * P)
    rows = []
    for g in yrows:
        members = [c for c in cands if min(g) - 1 <= c[1] <= max(g) + 1]
        if len(members) >= 4:
            rows.append(members)
    xs = [c[0] for c in cands]
    xcols = cluster_1d(xs, tol_mm * P)
    cols = []
    for g in xcols:
        members = [c for c in cands if min(g) - 1 <= c[0] <= max(g) + 1]
        if len(members) >= 4:
            cols.append(members)
    def show(struct, axis, label):
        # axis 0: rows (sorted by x), axis 1: cols (sorted by y)
        for m in struct:
            key = (lambda c: c[0]) if axis == 0 else (lambda c: c[1])
            m = sorted(m, key=key)
            cs = [c[axis] for c in m]
            span = cs[-1] - cs[0]
            pits = [f"{b-a:.0f}" for a, b in zip(cs, cs[1:])]
            sizes = [f"{c[2]}x{c[3]}" for c in m]
            print(f"   {label} y~{int(np.mean([c[1] for c in m])) if axis==0 else int(np.mean([c[0] for c in m]))}: n={len(m)} span={span:.0f}px pitch={pits}")
            print(f"      px: {[f'{c:.0f}' for c in cs]}")
            print(f"      sizes: {sizes}")
    show(rows, 0, "ROW")
    show(cols, 1, "COL")
    return bw, cands, P

print("########## STENCIL (p21 img1)")
bw_s, c_s, P_s = probe("stencil", os.path.join(D, "a7670_p21_img1.png"),
                       lambda w, h, f: 12 <= w <= 130 and 12 <= h <= 130 and f > 0.60)
print()
print("########## BOT VIEW (p19 fig600)")
bw_b, c_b, P_b = probe("bot", os.path.join(D, "a7670_p19_fig600.png"),
                       lambda w, h, f: 30 <= w <= 160 and 30 <= h <= 160 and 0.08 <= f <= 0.50)
