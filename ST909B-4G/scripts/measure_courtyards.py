# measure_courtyards.py — วัด courtyard bbox จริงของ footprint ที่ชนกัน + nets ของ TP
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)

TARGETS = ["TP4", "TP5", "TP6", "TP7", "TP8", "R1", "R2", "U2", "U4", "SW1", "J1", "J3", "J4", "U3"]

def mm(v):
    return v / 1e6

def courtyard_bbox(fp):
    lo_x = lo_y = 1e9
    hi_x = hi_y = -1e9
    found = False
    for gi in fp.GraphicalItems():
        if gi.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            found = True
            bb = gi.GetBoundingBox()
            lo_x = min(lo_x, bb.GetLeft()); hi_x = max(hi_x, bb.GetRight())
            lo_y = min(lo_y, bb.GetTop()); hi_y = max(hi_y, bb.GetBottom())
    return (found, mm(lo_x), mm(lo_y), mm(hi_x), mm(hi_y)) if found else (False, 0, 0, 0, 0)

def pad_bbox(fp):
    lo_x = lo_y = 1e9
    hi_x = hi_y = -1e9
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        lo_x = min(lo_x, bb.GetLeft()); hi_x = max(hi_x, bb.GetRight())
        lo_y = min(lo_y, bb.GetTop()); hi_y = max(hi_y, bb.GetBottom())
    return mm(lo_x), mm(lo_y), mm(hi_x), mm(hi_y)

for fp in b.GetFootprints():
    ref = fp.GetReference()
    if ref not in TARGETS:
        continue
    has_c, x0, y0, x1, y1 = courtyard_bbox(fp)
    px0, py0, px1, py1 = pad_bbox(fp)
    nets = ",".join(sorted({p.GetNetname().lstrip("/") for p in fp.Pads() if p.GetNetname()}))
    c = fp.GetPosition()
    print(f"{ref:4s} fp={fp.GetFPIDAsString().split(':')[-1]:24s} layer={fp.GetLayerName():5s} "
          f"pos=({mm(c.x):.2f},{mm(c.y):.2f})")
    if has_c:
        print(f"      courtyard: x {x0:.2f}..{x1:.2f}  y {y0:.2f}..{y1:.2f}  ({x1-x0:.2f}x{y1-y0:.2f})")
    else:
        print("      courtyard: NONE")
    print(f"      pads     : x {px0:.2f}..{px1:.2f}  y {py0:.2f}..{py1:.2f}  nets=[{nets}]")
