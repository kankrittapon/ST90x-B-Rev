# Locate the 1.50-PITCH ext lines + middle forbidden-area rect precisely in fig4.
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\a7670_p20_fig600.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
dark = (R < 130) & (G < 130) & (B < 130)

S = (3281.0 - 1171.0) / 24.0
X0, Y0 = 1171.0, 1180.0
def px(x, y): return (int(X0 + S * (x + 12.0)), int(Y0 + S * (y + 12.0)))
def mx(px): return (px - X0) / S - 12.0
def my(py): return (py - Y0) / S - 12.0

# --- vertical lines in band module-x +1..+6, module-y +9..+17 (below bottom pad row, incl keepout) ---
ya, yb = px(0, 9)[1], px(0, 17)[1]
xa, xb = px(1, 0)[0], px(6, 0)[0]
reg = dark[ya:yb, xa:xb]
vl = ndimage.binary_opening(reg, structure=np.ones((60, 1)))
lab, n = ndimage.label(vl)
print('vertical lines (module-x, y-range):')
for i, s in enumerate(ndimage.find_objects(lab), 1):
    x0, x1 = s[1].start, s[1].stop
    y0, y1 = s[0].start, s[0].stop
    if (x1 - x0) > 40:  # thin line: width small
        continue
    print('  x %.3f  y %.3f..%.3f  (len %.2f mm)' % (mx(xa + (x0 + x1) / 2.0), my(ya + y0), my(ya + y1), (y1 - y0) / S))

# --- horizontal lines in same band (the dim line row) ---
hl = ndimage.binary_opening(reg, structure=np.ones((1, 60)))
lab2, n2 = ndimage.label(hl)
print('horizontal lines (y, x-range):')
for i, s in enumerate(ndimage.find_objects(lab2), 1):
    x0, x1 = s[1].start, s[1].stop
    y0, y1 = s[0].start, s[0].stop
    if (y1 - y0) > 40:
        continue
    print('  y %.3f  x %.3f..%.3f' % (my(ya + (y0 + y1) / 2.0), mx(xa + x0), mx(xa + x1)))

# --- middle forbidden rect border: strong solid rect edges in x +0..+4.5, y +0.5..+4.5 ---
ya2, yb2 = px(0, 0.2)[1], px(0, 5.0)[1]
xa2, xb2 = px(-0.5, 0)[0], px(5.0, 0)[0]
reg2 = dark[ya2:yb2, xa2:xb2]
# vertical borders: columns with long continuous dark run (>1.8mm)
colrun = np.zeros(reg2.shape[1], int)
for c in range(reg2.shape[1]):
    col = reg2[:, c]
    # longest run of True
    best = cur = 0
    for v in col:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    colrun[c] = best
cands = np.nonzero(colrun > 0.9 * S)[0]
gr = []
for c in cands:
    if gr and c - gr[-1][-1] <= 4:
        gr[-1].append(c)
    else:
        gr.append([c])
print('middle-area vertical borders (x mm, run %.2f mm):' % (0.9,))
for g in gr:
    x = xa2 + int(np.mean(g))
    col = reg2[:, g[0]:g[-1] + 1].any(axis=1)
    ys = np.nonzero(col)[0]
    print('  x %.3f  y %.3f..%.3f' % (mx(x), my(ya2 + ys.min()), my(ya2 + ys.max())))
rowrun = np.zeros(reg2.shape[0], int)
for r in range(reg2.shape[0]):
    row = reg2[r, :]
    best = cur = 0
    for v in row:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    rowrun[r] = best
cands = np.nonzero(rowrun > 0.9 * S)[0]
gr = []
for r in cands:
    if gr and r - gr[-1][-1] <= 4:
        gr[-1].append(r)
    else:
        gr.append([r])
print('middle-area horizontal borders (y mm):')
for g in gr:
    y = ya2 + int(np.mean(g))
    row = reg2[g[0]:g[-1] + 1, :].any(axis=0)
    xs = np.nonzero(row)[0]
    print('  y %.3f  x %.3f..%.3f' % (my(y), mx(xa2 + xs.min()), mx(xa2 + xs.max())))
