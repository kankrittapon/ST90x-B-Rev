# p4_fix2.py — round 2 board fixes: J7 rect y -> +-0.80 (unify PADS_ROW_3), U6 ref move, LED refs 0.8 + LED2 row shift
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
NM = 1000000
b = pcbnew.LoadBoard(BOARD)


def V(x, y):
    return pcbnew.VECTOR2I(int(round(x * NM)), int(round(y * NM)))


def mm(v):
    return round(v / NM, 3)


# 1) J7 silk rect y 24.60/26.40 -> 24.70/26.30 (rel +-0.80, matches PADS_ROW_3 lib)
J7_RECT = "abc0a08f-e98a-47e2-aced-565d265888ce"
for fp in b.GetFootprints():
    if fp.GetReference() != "J7":
        continue
    for d in fp.GraphicalItems():
        if d.m_Uuid.AsString() != J7_RECT:
            continue
        s, e = d.GetStart(), d.GetEnd()
        print("J7RECT old (%.2f,%.2f)-(%.2f,%.2f)" % (mm(s.x), mm(s.y), mm(e.x), mm(e.y)))
        d.SetStart(V(26.20, 24.70))
        d.SetEnd(V(31.80, 26.30))
        s2, e2 = d.GetStart(), d.GetEnd()
        print("J7RECT new (%.2f,%.2f)-(%.2f,%.2f)" % (mm(s2.x), mm(s2.y), mm(e2.x), mm(e2.y)))

# 2) U6 ref -> (5.00,38.95) (clears J3 rect bottom stroke 41.25..41.35 and U6 silk top 42.53)
# 3) LED refs 0.7 -> 0.8 (min height); LED2 ref -> (15.50,10.50) to break the 3.0 pitch row collision
for fp in b.GetFootprints():
    ref = fp.GetReference()
    for f in fp.GetFields():
        if f.GetName() != "Reference":
            continue
        if ref == "U6":
            p = f.GetPosition()
            print("U6REF old (%.2f,%.2f)" % (mm(p.x), mm(p.y)))
            f.SetPosition(V(5.00, 38.95))
            q = f.GetPosition()
            print("U6REF new (%.2f,%.2f)" % (mm(q.x), mm(q.y)))
        if ref in ("LED1", "LED2", "LED3"):
            f.SetTextSize(V(0.8, 0.8))
            if ref == "LED2":
                f.SetPosition(V(15.50, 10.50))
            q = f.GetPosition()
            print("%sREF (%.2f,%.2f) h=%.2f" % (ref, mm(q.x), mm(q.y), mm(f.GetTextHeight())))

print("save:", b.Save(BOARD))
