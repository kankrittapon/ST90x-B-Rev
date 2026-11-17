# p4_lib_sync.py — sync library footprints with the edited board instances
# (clears the 14 new lib_footprint_mismatch warnings: board silk was fixed, lib was stale)
import pcbnew

LIBDIR = r"D:\Tracker\ST909B-4G\lib\ST909B.pretty"
NM = 1000000

# name -> silk rect rel coords (stroke centers)
RECT_SYNC = {
    "TP_PAD_1.2":   (-0.85, -0.85, 0.85, 0.85),    # TP1-4
    "TP_PAD_1.5":   (-1.00, -1.00, 1.00, 1.00),    # TP5-8
    "PADS_ROW_3":   (-2.80, -0.80, 2.80, 0.80),    # J3, J4, J7
    "ANT_4G_PADS":  (-2.70, -0.80, 2.70, 0.80),    # ANT1
    "SW_SOS":       (-3.90, -1.30, 3.90, 1.30),    # SW2
}
# A7670SA_LGA88 pin-1 poly new points (rel)
U1_POLY_PTS = [(-12.40, -8.30), (-12.40, -7.70), (-11.90, -8.00)]

print("has FootprintLoad:", hasattr(pcbnew, "FootprintLoad"), " has FootprintSave:", hasattr(pcbnew, "FootprintSave"))

for name, (x1, y1, x2, y2) in RECT_SYNC.items():
    fp = pcbnew.FootprintLoad(LIBDIR, name)
    if fp is None:
        print("!! lib not found:", name)
        continue
    n = 0
    for d in fp.GraphicalItems():
        if d.GetLayer() not in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            continue
        if d.GetShape() != 1:  # RECTANGLE
            continue
        s, e = d.GetStart(), d.GetEnd()
        print("%-14s silk rect old (%7.2f,%7.2f)-(%7.2f,%7.2f)" % (name, s.x / NM, s.y / NM, e.x / NM, e.y / NM))
        d.SetStart(pcbnew.VECTOR2I(int(x1 * NM), int(y1 * NM)))
        d.SetEnd(pcbnew.VECTOR2I(int(x2 * NM), int(y2 * NM)))
        s2, e2 = d.GetStart(), d.GetEnd()
        print("               new (%7.2f,%7.2f)-(%7.2f,%7.2f)" % (s2.x / NM, s2.y / NM, e2.x / NM, e2.y / NM))
        n += 1
    if n == 0:
        print("!! no silk rect found in", name)
        continue
    try:
        pcbnew.FootprintSave(LIBDIR, fp)
        print("   saved lib:", name)
    except Exception as ex:
        print("!! FootprintSave failed for %s: %s" % (name, ex))

# U1 poly
fp = pcbnew.FootprintLoad(LIBDIR, "A7670SA_LGA88")
if fp is None:
    print("!! lib not found: A7670SA_LGA88")
else:
    n = 0
    for d in fp.GraphicalItems():
        if d.GetLayer() not in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            continue
        poly = d.GetPolyShape()
        if poly.OutlineCount() == 0:
            continue
        ch = poly.Outline(0)
        old = " ".join("(%.2f,%.2f)" % (ch.GetPoint(i).x / NM, ch.GetPoint(i).y / NM) for i in range(ch.PointCount()))
        print("U1 lib poly old pts:", old)
        if hasattr(d, "SetPolyPoints"):
            d.SetPolyPoints([pcbnew.VECTOR2I(int(x * NM), int(y * NM)) for x, y in U1_POLY_PTS])
            ch2 = d.GetPolyShape().Outline(0)
            print("U1 lib poly new pts:", " ".join("(%.2f,%.2f)" % (ch2.GetPoint(i).x / NM, ch2.GetPoint(i).y / NM) for i in range(ch2.PointCount())))
            n += 1
    if n:
        try:
            pcbnew.FootprintSave(LIBDIR, fp)
            print("   saved lib: A7670SA_LGA88")
        except Exception as ex:
            print("!! FootprintSave failed: %s" % ex)
    else:
        print("!! no silk poly found in A7670SA_LGA88")
