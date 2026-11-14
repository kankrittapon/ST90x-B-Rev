# Anchor the 7.90 / 9.70 / 11.50 / 10.10 dims of Figure 15 to pad edges or centers.
import numpy as np
from PIL import Image

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\l76k_p28_400dpi.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
dark = (R < 150) & (G < 150) & (B < 150)

def dim_anchor(name, yline, ytop, xlo, xhi):
    # dim line row: horizontal dark run at ~yline
    best = None
    for y in range(yline - 25, yline + 25):
        n = dark[y, xlo:xhi].sum()
        if best is None or n > best[1]:
            best = (y, n, xlo + int(np.median(np.nonzero(dark[y, xlo:xhi])[0])) if n else -1)
    yb = best[0]
    # ext lines: columns with tall vertical dark runs between ytop and yb
    reg = dark[ytop:yb - 2, xlo:xhi]
    colsum = reg.sum(axis=0)
    need = (yb - ytop) * 0.55
    xs = np.nonzero(colsum > need)[0]
    groups = []
    for x in xs:
        if groups and x - groups[-1][-1] <= 3:
            groups[-1].append(x)
        else:
            groups.append([x])
    print('%s: dim-line y=%d (n=%d); ext lines at x:' % (name, yb, best[1]),
          ['%d (n=%d)' % (xlo + int(np.mean(g)), int(colsum[g[0]])) for g in groups])
    return yb

# figure area: pads x 1053..2177, y 1043..2119; dims below
y79 = dim_anchor('7.90 ', 2075, 2110, 1000, 2250)
y97 = dim_anchor('9.70 ', 2235, 2140, 1000, 2250)
y115 = dim_anchor('11.50', 2325, 2160, 1000, 2250)

# 10.10 vertical dim on the right: horizontal ext lines pointing left to pad rows
reg = dark[950:2300, 2250:2500]
rowsum = reg.sum(axis=1)
ys = np.nonzero(rowsum > 80)[0]
groups = []
for y in ys:
    if groups and y - groups[-1][-1] <= 3:
        groups[-1].append(y)
    else:
        groups.append([y])
print('10.10 ext rows (page-y):', [int(np.mean(g)) + 950 for g in groups])

# also: left-side dims (0.90 etc labels on the left of figure): vertical dims
reg = dark[900:2300, 700:1050]
rowsum = reg.sum(axis=1)
ys = np.nonzero(rowsum > 60)[0]
groups = []
for y in ys:
    if groups and y - groups[-1][-1] <= 3:
        groups[-1].append(y)
    else:
        groups.append([y])
print('left-side horizontal ext rows (page-y):', [int(np.mean(g)) + 900 for g in groups])
