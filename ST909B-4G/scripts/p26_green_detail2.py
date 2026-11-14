# Precise green-band measurement, fixed mm conversion (indices are tv-relative).
import numpy as np
from PIL import Image

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\C2916234_p26_300dpi.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
green = (G > 120) & (R < 120) & (B < 120)

SX = 636 / 9.70
SY = 680 / 10.10
X0, Y0 = 860, 1631
tv = green[Y0:Y0 + 681, X0:X0 + 637]

def mx(i): return i / SX
def my(i): return i / SY

# 1) LEFT pad strip: rows with green in x [3..12] px
band = tv[:, 3:12]
rowsum = band.sum(axis=1)
rows = np.nonzero(rowsum >= 5)[0]
print('LEFT strip rows present: y %.3f..%.3f mm (n=%d)' % (my(rows.min()), my(rows.max()), len(rows)))
# per-row x extent: for those rows, how far does green extend from x=0?
ext = []
for y in rows:
    xs = np.nonzero(tv[y, :60])[0]
    if len(xs):
        ext.append(xs.max())
ext = np.array(ext)
print('  per-row left green max-x: median %.3f mm (p10 %.3f, p90 %.3f)' % (
    np.median(ext) / SX, np.percentile(ext, 10) / SX, np.percentile(ext, 90) / SX))

# 2) RIGHT pad strip
band = tv[:, 637 - 12:637 - 3]
rowsum = band.sum(axis=1)
rows = np.nonzero(rowsum >= 5)[0]
print('RIGHT strip rows present: y %.3f..%.3f mm (n=%d)' % (my(rows.min()), my(rows.max()), len(rows)))
ext = []
for y in rows:
    xs = np.nonzero(tv[y, 577:])[0]
    if len(xs):
        ext.append(xs.min())
ext = np.array(ext)
print('  per-row right green min-x from right edge: median %.3f mm (p10 %.3f, p90 %.3f)' % (
    (637 - np.median(ext)) / SX, (637 - np.percentile(ext, 10)) / SX, (637 - np.percentile(ext, 90)) / SX))

# 3) TOP band: rows 0..60: x-extent excluding the side strips (x 30..590)
band = tv[0:60, 30:600]
rowsum = band.sum(axis=1)
rows = np.nonzero(rowsum > 10)[0]
print('TOP band rows: %s (y %.3f..%.3f)' % (rows, my(rows.min()) if len(rows) else -1, my(rows.max()) if len(rows) else -1))
for y in rows:
    xs = np.nonzero(tv[y, :])[0]
    print('   row %d (y=%.3f): x %.3f..%.3f n=%d' % (y, my(y), mx(xs.min()), mx(xs.max()), len(xs)))

# 4) BOTTOM band rows 620..680
band = tv[620:681, 30:600]
rowsum = band.sum(axis=1)
rows = np.nonzero(rowsum > 10)[0] + 620
print('BOTTOM band rows: %s' % rows)
for y in rows:
    xs = np.nonzero(tv[y, :])[0]
    # find runs
    runs = []
    prev = -10
    for x in xs:
        if x - prev > 3:
            runs.append([x, x])
        else:
            runs[-1][1] = x
        prev = x
    print('   row %d (y=%.3f): runs %s' % (y, my(y), [('%.3f..%.3f' % (mx(s), mx(e))) for s, e in runs]))

# 5) circle center/diameter
reg = tv[int(0.6 * SY):int(2.8 * SY), int(0.6 * SX):int(3.0 * SX)]
ys, xs = np.nonzero(reg)
print('circle: x %.3f..%.3f (d %.3f)  y %.3f..%.3f (d %.3f)  center (%.3f, %.3f)' % (
    mx(0.6 * SX + xs.min()), mx(0.6 * SX + xs.max()), (xs.max() - xs.min()) / SX,
    my(0.6 * SY + ys.min()), my(0.6 * SY + ys.max()), (ys.max() - ys.min()) / SY,
    mx(0.6 * SX + (xs.min() + xs.max()) / 2), my(0.6 * SY + (ys.min() + ys.max()) / 2)))
