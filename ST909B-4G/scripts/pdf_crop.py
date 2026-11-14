# Crop + upscale regions of PDF figures for close reading
from PIL import Image
import os

D = r"D:\Tracker\ST909B-4G\Datasheet\pdf_img"
os.makedirs(os.path.join(D, "crop"), exist_ok=True)


def crop(src, box, out, scale=3):
    im = Image.open(os.path.join(D, src))
    c = im.crop(box)
    c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
    path = os.path.join(D, "crop", out)
    c.save(path)
    print(out, "src_size", im.size, "->", c.size)


# p19 bot view: figure occupies right half of image (from previous read: Bot View right side)
# image is ~912x541; bot view approx x 500..912, y 0..541
crop("A7670_Series_Hardware_Design_V1.00_p19_Im2.png", (500, 0, 912, 541), "p19_bot_full.png", 3)
# top edge of bot view
crop("A7670_Series_Hardware_Design_V1.00_p19_Im2.png", (500, 0, 912, 180), "p19_bot_top.png", 5)
# bottom edge of bot view
crop("A7670_Series_Hardware_Design_V1.00_p19_Im2.png", (500, 350, 912, 541), "p19_bot_bottom.png", 5)
# left+center of bot view
crop("A7670_Series_Hardware_Design_V1.00_p19_Im2.png", (500, 150, 720, 400), "p19_bot_left.png", 5)

# p20 recommended footprint (900x880 approx): top-left corner region
crop("A7670_Series_Hardware_Design_V1.00_p20_Im2.png", (230, 200, 620, 420), "p20_topleft.png", 3)
# p20 bottom-left + bottom edge
crop("A7670_Series_Hardware_Design_V1.00_p20_Im2.png", (230, 420, 720, 700), "p20_bottom.png", 3)
# p20 right edge
crop("A7670_Series_Hardware_Design_V1.00_p20_Im2.png", (620, 200, 900, 700), "p20_right.png", 3)

# p13 pin assignment: inner grid
crop("A7670_Series_Hardware_Design_V1.00_p13_Im2.png", (280, 380, 950, 980), "p13_inner.png", 2)
