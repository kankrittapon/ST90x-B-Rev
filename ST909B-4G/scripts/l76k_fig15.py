# Measure Figure 15 (L76K recommended footprint) precisely.
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\l76k_p28_400dpi.png').convert('RGB')
a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
black = (R < 100) & (G < 100) & (B < 100)
green = (G > 120) & (R < 120) & (B < 120)

# green rect of the footprint figure
ys, xs = np.nonzero(green[1400:3400, 500:2900])
print('green bbox: x %d..%d y %d..%d' % (xs.min() + 500, xs.max() + 500, ys.min() + 1400, ys.max() + 1400))

# black pads: solid comps
lab, n = ndimage.label(black[1400:3400, 500:2900])
sl = ndimage.find_objects(lab)
pads = []
for i, s in enumerate(sl, 1):
    y0, y1 = s[0].start, s[0].stop
    x0, x1 = s[1].start, s[1].stop
    area = int((lab[s] == i).sum())
    if area < 2000:
        continue
    pads.append((y0 + 1400, y1 + 1400, x0 + 500, x1 + 500, area))
print('solid black comps (pads):', len(pads))
for p in sorted(pads):
    print('  y %d..%d (h %d) x %d..%d (w %d) area %d' % (p[0], p[1], p[1] - p[0], p[2], p[3], p[3] - p[2], p[4]))
