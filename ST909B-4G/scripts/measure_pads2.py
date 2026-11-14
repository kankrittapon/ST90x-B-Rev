# Directed pad measurement: calibrate each figure from its inner grid (pitch 3.80,
# first row/col at 4.40), then measure edge pads via strip profiles.
# Figures: fig4 footprint (p20), stencil (p21 img1), bot view (p19).
import numpy as np
from PIL import Image
from scipy import ndimage
import os, json

D = r"D:\Tracker\ST909B-4G\Datasheet\pdf_render"

def load(path):
    img = np.array(Image.open(path).convert("L"))
    return img < 128

def comp_boxes(bw, min_area=40):
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

def find_inner_corners(bw, kind):
    """Return pixel centers of inner-grid corner pads (r1c1, r1c5, r5c1, r5c5)."""
    boxes = comp_boxes(bw)
    if kind == "stencil":
        # aperture blobs solid; group into pads: cluster blobs whose centers < 1.6mm apart
        # first pass with unknown scale: cluster by proximity in px using expected 0.85mm size
        solid = [b for b in boxes if (b[2]-b[0]) < 90 and (b[3]-b[1]) < 90 and b[4] > 0.55*(b[2]-b[0])*(b[3]-b[1])]
        cen = np.array([((b[0]+b[2])/2, (b[1]+b[3])/2) for b in solid])
        # cluster
        used = np.zeros(len(solid), bool)
        groups = []
        for i in range(len(solid)):
            if used[i]:
                continue
            d = np.hypot(cen[:, 0]-cen[i, 0], cen[:, 1]-cen[i, 1])
            near = np.where((d < 75) & ~used)[0]
            if len(near) >= 3:
                used[near] = True
                groups.append(cen[near].mean(axis=0))
        # groups = inner pads (20) ; find the 4 extreme corners of the 5x5 grid
        g = np.array(groups)
        return g, solid, boxes
    if kind == "bot":
        rings = [b for b in boxes if 40 < (b[2]-b[0]) < 160 and 40 < (b[3]-b[1]) < 160
                 and 0.10 < b[4]/((b[2]-b[0])*(b[3]-b[1])) < 0.45]
        cen = np.array([((b[0]+b[2])/2, (b[1]+b[3])/2) for b in rings])
        return cen, rings, boxes
    if kind == "fig4":
        # inner pads: hatched squares with border; large square-ish comps
        cands = []
        for b in boxes:
            w, h = b[2]-b[0], b[3]-b[1]
            if 120 < w < 260 and 120 < h < 260 and 0.10 < b[4]/(w*h) < 0.75:
                cands.append(((b[0]+b[2])/2, (b[1]+b[3])/2, b))
        cen = np.array([(c[0], c[1]) for c in cands])
        return cen, cands, boxes

def fit_grid(cen):
    """Find 4 corner points of a ~5x5 grid with pitch P (unknown) -> return S, TL px."""
    # take the extreme points: min x+y etc. Use robust: find pitch via min unique distances
    pts = cen[:, :2]
    # pitch = median of nearest-neighbor distances among the dense cluster
    from scipy.spatial import cKDTree
    t = cKDTree(pts)
    dd, _ = t.query(pts, k=2)
    nn = np.sort(dd[:, 1])
    nn = nn[nn < np.percentile(nn, 60)]
    P = np.median(nn)
    # TL corner pad = point with min(x+y); TR = min(y-x); BL = min(x-y); BR = max(x+y)
    s = pts[:, 0] + pts[:, 1]
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(pts[:, 1] - pts[:, 0])]
    bl = pts[np.argmin(pts[:, 0] - pts[:, 1])]
    return P, tl, tr, bl, br

def strip_runs(bw, S, TL, edge, band=(0.05, 1.45), span=(0.0, 24.0), min_w_mm=0.42, thr_frac=0.22):
    """Detect pad runs along an edge via profile."""
    tlx, tly = TL
    if edge in ("T", "B"):
        ya = int(tly + band[0]*S) if edge == "T" else int(tly + (24-band[1])*S)
        yb = int(tly + band[1]*S) if edge == "T" else int(tly + (24-band[0])*S)
        xa = int(tlx + span[0]*S)
        xb = int(tlx + span[1]*S)
        strip = bw[ya:yb, xa:xb]
        prof = strip.sum(axis=0).astype(float)
        depth_prof = None
    else:
        xa = int(tlx + band[0]*S) if edge == "L" else int(tlx + (24-band[1])*S)
        xb = int(tlx + band[1]*S) if edge == "L" else int(tlx + (24-band[0])*S)
        ya = int(tly + span[0]*S)
        yb = int(tly + span[1]*S)
        strip = bw[ya:yb, xa:xb]
        prof = strip.sum(axis=1).astype(float)
    n = len(prof)
    thr = thr_frac * (band[1]-band[0]) * S
    min_w = int(min_w_mm * S)
    on = prof > thr
    runs = []
    i = 0
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            if j - i >= min_w:
                # pad depth: perpendicular profile inside run
                seg = strip[:, i:j]
                rp = seg.sum(axis=1).astype(float)
                rthr = 0.30 * (j - i)
                rows = np.where(rp > rthr)[0]
                d0 = rows.min() / S + band[0] if len(rows) else -1
                d1 = rows.max() / S + band[0] if len(rows) else -1
                runs.append(((i + j) / 2 / S + span[0], (j - i) / S, d0, d1, int(prof[i:j].max())))
            i = j
        else:
            i += 1
    return runs

def report(name, path, kind):
    bw = load(path)
    cen, cands, boxes = find_inner_corners(bw, kind)
    P, tl, tr, bl, br = fit_grid(cen)
    # S from corner diagonals: pitch*4 = 15.20mm between adjacent corners? no:
    # corner-to-corner along edge = 15.20mm (r1c1 to r1c5)
    Sx = (tr[0] - tl[0]) / 15.20
    Sy = (bl[1] - tl[1]) / 15.20
    S = (Sx + Sy) / 2
    TL = (tl[0] - 4.40 * S, tl[1] - 4.40 * S)
    print(f"== {name}: P={P:.1f}px Sx={Sx:.2f} Sy={Sy:.2f} S={S:.2f} px/mm; TL=({TL[0]:.0f},{TL[1]:.0f})")
    print(f"   inner corners: TL({tl[0]:.0f},{tl[1]:.0f}) TR({tr[0]:.0f},{tr[1]:.0f}) BL({bl[0]:.0f},{bl[1]:.0f}) BR({br[0]:.0f},{br[1]:.0f})")
    for edge in ("T", "B", "L", "R"):
        runs = strip_runs(bw, S, TL, edge)
        cs = [r[0] for r in runs]
        pits = [f"{b-a:.2f}" for a, b in zip(cs, cs[1:])]
        sizes = [f"{r[1]:.2f}" for r in runs]
        deps = [f"{r[2]:.2f}-{r[3]:.2f}" for r in runs]
        print(f"   edge {edge}: n={len(runs)}")
        print(f"      centers: {['%.2f' % c for c in cs]}")
        print(f"      pitch:   {pits}")
        print(f"      width:   {sizes}")
        print(f"      depth:   {deps}")
    return S, TL

print("### FIGURE 4 footprint (p20)")
report("fig4", os.path.join(D, "a7670_p20_fig600.png"), "fig4")
print()
print("### FIGURE 5 stencil (p21 img1)")
report("stencil", os.path.join(D, "a7670_p21_img1.png"), "stencil")
print()
print("### FIGURE 3 bot view (p19)")
report("bot", os.path.join(D, "a7670_p19_fig600.png"), "bot")
