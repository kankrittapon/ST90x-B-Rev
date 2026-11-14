# Crop fig4 (a7670 p20, 600dpi) regions around the two Forbidden Areas + bottom dims.
import numpy as np
from PIL import Image

im = Image.open(r'D:\Tracker\ST909B-4G\Datasheet\pdf_render\a7670_p20_fig600.png').convert('RGB')
a = np.array(im).astype(int)
H, W = a.shape[:2]
print('image', W, 'x', H)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
dark = (R < 120) & (G < 120) & (B < 120)

# find module solid outline: rows/cols with long dark runs
rows = np.nonzero(dark.sum(axis=1) > 0.55 * W)[0]
cols = np.nonzero(dark.sum(axis=0) > 0.55 * H)[0]
print('long dark rows:', rows[:5], '...', rows[-5:] if len(rows) > 5 else '')
print('long dark cols:', cols[:5], '...', cols[-5:] if len(cols) > 5 else '')

# group rows into bands
def groups(idx, gap=5):
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(i)
        else:
            out.append([i])
    return [int(np.mean(g)) for g in out]

rg = groups(rows)
cg = groups(cols)
print('row bands:', rg)
print('col bands:', cg)
