# p4_silk_fix.py — P4: fix 42 silk warnings + delete dangling via /M3V3 (16.50,58.50)
# Strategy (designed against edge_clearance 0.5, pad_to_mask_clearance 0, min_silk_clearance 0):
#   1) move Reference fields off their footprint silk rects / pad mask openings
#   2) enlarge silk rects of TP1-8/ANT1/J3/J4/J7/SW2 so strokes clear pad mask openings by 0.15-0.20
#   3) reshape U1 pin-1 poly into the [0.5 .. 1.2] west-edge window
#   4) shrink LED1-3 refs to 0.7 mm (they collide with each other at pitch 3.0)
#   5) delete via_dangling /M3V3 at (16.50,58.50)
# Every edit is read back and printed for verification.
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
NM = 1000000
b = pcbnew.LoadBoard(BOARD)


def V(x, y):
    return pcbnew.VECTOR2I(int(round(x * NM)), int(round(y * NM)))


def mm(v):
    return round(v / NM, 3)


def fpbb(fp):
    bb = fp.GetBoundingBox()
    return "(%.2f..%.2f, %.2f..%.2f)" % (mm(bb.GetLeft()), mm(bb.GetRight()), mm(bb.GetTop()), mm(bb.GetBottom()))


# ---------------- 1) reference moves ----------------
REF_MOVES = {
    "J2":   (10.00, 69.60),
    "J3":   (8.50, 38.90),
    "J4":   (7.50, 60.40),
    "J5":   (5.00, 64.40),
    "J6":   (29.00, 17.95),
    "J7":   (29.00, 23.75),
    "SW1":  (19.00, 69.50),
    "SW2":  (17.00, 5.90),
    "ANT1": (5.00, 1.40),
    "C1":   (29.50, 9.30),
    "TP1":  (7.00, 35.40),
    "TP2":  (9.50, 35.40),
    "TP3":  (3.00, 58.40),
    "TP4":  (2.20, 39.00),
    "TP5":  (28.30, 69.75),
    "TP6":  (19.60, 69.75),
    "TP7":  (22.50, 69.75),
    "TP8":  (25.40, 69.75),
    "U4":   (21.60, 52.65),
    "R1":   (8.50, 53.45),
    "R2":   (12.38, 54.00),
}
REF_RESIZE = {"LED1", "LED2", "LED3"}

done_moves = set()
done_resize = set()
for fp in b.GetFootprints():
    ref = fp.GetReference()
    for f in fp.GetFields():
        if f.GetName() != "Reference":
            continue
        p = f.GetPosition()
        if ref in REF_MOVES:
            tx, ty = REF_MOVES[ref]
            print("REF %-5s (%7.2f,%7.2f) -> (%7.2f,%7.2f)" % (ref, mm(p.x), mm(p.y), tx, ty))
            f.SetPosition(V(tx, ty))
            q = f.GetPosition()
            print("     readback (%.2f,%.2f)" % (mm(q.x), mm(q.y)))
            done_moves.add(ref)
        elif ref in REF_RESIZE:
            print("REF %-5s resize 1.0 -> 0.7 (was %.2f x %.2f)" % (ref, mm(f.GetTextHeight()), mm(f.GetTextWidth())))
            if hasattr(f, "SetTextSize"):
                f.SetTextSize(V(0.7, 0.7))
            else:
                f.SetTextHeight(int(0.7 * NM))
                f.SetTextWidth(int(0.7 * NM))
            print("     readback h=%.2f w=%.2f" % (mm(f.GetTextHeight()), mm(f.GetTextWidth())))
            done_resize.add(ref)

missing = (set(REF_MOVES) | REF_RESIZE) - done_moves - done_resize
print("REF missing:", sorted(missing) if missing else "none")

# ---------------- 2) silk rect fixes by uuid ----------------
RECT_FIX = {
    "2076e1cb-3a46-4d77-a59f-c8594e417cb0": (6.15, 36.15, 7.85, 37.85),    # TP1
    "1e76b0be-0954-4c32-a47d-8f209b125cec": (8.65, 36.15, 10.35, 37.85),   # TP2
    "782e044c-2c43-4a9b-9b7d-2be183f48f65": (2.15, 59.15, 3.85, 60.85),    # TP3
    "bf94723b-6a31-4eed-85f1-877dbad5cc3e": (1.35, 39.75, 3.05, 41.45),    # TP4
    "8ee0d4ad-9873-4ef8-977a-ebaf89ff1cd9": (27.30, 70.50, 29.30, 72.50),  # TP5
    "8e997351-0d05-4aad-bba1-d5e3615219d1": (18.60, 70.50, 20.60, 72.50),  # TP6
    "86413e62-f768-459b-a7fe-16f14e97e735": (21.50, 70.50, 23.50, 72.50),  # TP7
    "c474567a-152b-4b5d-9dd2-6837a314e553": (24.40, 70.50, 26.40, 72.50),  # TP8
    "3bfd5854-8f54-4981-bfc1-b021ebf2540c": (2.30, 2.20, 7.70, 3.80),      # ANT1
    "88172f9d-6606-4b72-949f-d7d649d1bf40": (5.70, 39.70, 11.30, 41.30),   # J3
    "dd6ec032-ba68-426b-a61a-14343824c67c": (4.70, 61.20, 10.30, 62.80),   # J4
    "abc0a08f-e98a-47e2-aced-565d265888ce": (26.20, None, 31.80, None),    # J7 keep y
    "ed52015c-0ff3-4fbe-9c82-a882c387b628": (13.10, 6.70, 20.90, 9.30),    # SW2
}
done_rects = set()
for fp in b.GetFootprints():
    for d in fp.GraphicalItems():
        u = d.m_Uuid.AsString()
        if u not in RECT_FIX:
            continue
        if d.GetShape() != 1:  # 1 = RECTANGLE
            print("!! %s expected RECTANGLE got %s" % (u[:8], d.GetShape()))
            continue
        s, e = d.GetStart(), d.GetEnd()
        x1, y1, x2, y2 = RECT_FIX[u]
        ny1 = mm(s.y) if y1 is None else y1
        ny2 = mm(e.y) if y2 is None else y2
        print("RECT %-4s %s (%7.2f,%7.2f)-(%7.2f,%7.2f) -> (%7.2f,%7.2f)-(%7.2f,%7.2f)" % (
            fp.GetReference(), u[:8], mm(s.x), mm(s.y), mm(e.x), mm(e.y), x1, ny1, x2, ny2))
        d.SetStart(V(x1, ny1))
        d.SetEnd(V(x2, ny2))
        s2, e2 = d.GetStart(), d.GetEnd()
        print("     readback (%.2f,%.2f)-(%2.f,%.2f) layer=%s" % (
            mm(s2.x), mm(s2.y), mm(e2.x), mm(e2.y), d.GetLayerName()))
        done_rects.add(u)
missing = set(RECT_FIX) - done_rects
print("RECT missing:", sorted(missing) if missing else "none")

# ---------------- 3) U1 pin-1 poly reshape ----------------
U1_POLY = "2bef0481-1d49-46c0-8b8e-4657b3eb1c3b"
U1_PTS = [(0.60, 9.20), (0.60, 9.80), (1.10, 9.50)]
for fp in b.GetFootprints():
    if fp.GetReference() != "U1":
        continue
    for d in fp.GraphicalItems():
        if d.m_Uuid.AsString() != U1_POLY:
            continue
        poly = d.GetPolyShape()
        ch = poly.Outline(0)
        print("U1POLY old pts:", " ".join("(%.2f,%.2f)" % (mm(ch.GetPoint(i).x), mm(ch.GetPoint(i).y)) for i in range(ch.PointCount())))
        if hasattr(d, "SetPolyPoints"):
            d.SetPolyPoints([V(x, y) for x, y in U1_PTS])
            poly2 = d.GetPolyShape()
            ch2 = poly2.Outline(0)
            print("U1POLY new pts:", " ".join("(%.2f,%.2f)" % (mm(ch2.GetPoint(i).x), mm(ch2.GetPoint(i).y)) for i in range(ch2.PointCount())))
        else:
            print("!! SetPolyPoints not available - U1 poly left unchanged (needs manual script)")

# ---------------- 4) delete dangling via ----------------
ndel = 0
for t in list(b.GetTracks()):
    if not isinstance(t, pcbnew.PCB_VIA):
        continue
    p = t.GetPosition()
    if abs(mm(p.x) - 16.50) < 0.05 and abs(mm(p.y) - 58.50) < 0.05 and "/M3V3" in t.GetNetname():
        print("VIA delete net=%s @ (%.2f,%.2f)" % (t.GetNetname(), mm(p.x), mm(p.y)))
        b.Delete(t)
        ndel += 1
print("via deleted:", ndel)

# ---------------- summary + save ----------------
print("== footprint bbox spot check")
for r in ("U1", "J3", "J4", "J7", "SW2", "TP1", "TP5", "ANT1"):
    for fp in b.GetFootprints():
        if fp.GetReference() == r:
            print("   %-5s %s" % (r, fpbb(fp)))
ok = b.Save(BOARD)
print("save:", ok)
