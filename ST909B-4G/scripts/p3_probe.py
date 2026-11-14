# p3_probe.py — point-in-fill probe: which GND fill poly contains each test point
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
MM = 1e6


def pt_in_poly(px, py, pts):
    inside = False
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi + 1e-18) + xi:
            inside = not inside
        j = i
    return inside


polys = {"F": [], "B": []}
for z in b.Zones():
    if z.GetNetname() != "/GND":
        continue
    for layer in z.GetLayerSet().Seq():
        if layer == pcbnew.F_Cu:
            ln = "F"
        elif layer == pcbnew.B_Cu:
            ln = "B"
        else:
            continue
        ps = z.GetFilledPolysList(layer)
        for i in range(ps.OutlineCount()):
            chain = ps.COutline(i)
            pts = [(chain.GetPoint(j).x / MM, chain.GetPoint(j).y / MM)
                   for j in range(chain.PointCount())]
            polys[ln].append(pts)

pads = []
for fp in b.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() != "/GND":
            continue
        p = pad.GetPosition()
        pads.append((fp.GetReference(), pad.GetPadName(), p.x / MM, p.y / MM,
                     pad.IsOnLayer(pcbnew.F_Cu), pad.IsOnLayer(pcbnew.B_Cu)))

print("F polys=%d B polys=%d" % (len(polys["F"]), len(polys["B"])))


def which(ln, x, y):
    hits = [i for i, pts in enumerate(polys[ln]) if pt_in_poly(x, y, pts)]
    return ",".join(str(h) for h in hits) if hits else "-"


FPTS = [
    (2.50, 71.20, "stitch B-island site"),
    (3.00, 71.20, "stitch B-island site"),
    (29.00, 15.00, "F island NE alt"),
    (31.00, 15.00, "F island NE alt"),
    (32.00, 15.00, "F island NE alt"),
    (30.00, 12.00, "F island NE alt"),
    (30.00, 18.00, "F island NE alt"),
    (1.05, 15.00, "known main west"),
    (34.20, 50.00, "east strip"),
    (34.20, 60.00, "east strip"),
    (34.20, 70.00, "east strip"),
    (34.20, 15.00, "NE"),
    (34.20, 25.00, "NE"),
    (33.50, 45.00, "east of SOS"),
    (33.50, 10.00, "NE corner"),
    (32.00, 45.00, "center-east"),
    (30.00, 45.00, "center-east"),
    (28.00, 45.00, "center-east"),
    (26.50, 45.00, "sliver LED_EN/BOOT"),
    (30.00, 20.00, "NE block"),
    (30.00, 15.00, "NE block"),
    (30.00, 10.00, "NE block"),
    (27.00, 10.00, "NE block"),
    (26.50, 8.50, "NE block west"),
    (31.00, 10.00, "NE block"),
    (33.00, 20.00, "NE block"),
    (33.00, 30.00, "NE mid"),
    (33.00, 40.00, "east mid"),
    (30.00, 30.00, "NE south edge"),
    (29.00, 35.00, "south of y31.7"),
    (31.00, 55.00, "center-east low"),
    (29.00, 60.00, "center-east low"),
    (30.50, 60.00, "center-east low"),
    (33.00, 65.00, "SE"),
    (30.00, 70.00, "SE band"),
    (29.00, 70.00, "SE band"),
    (33.50, 72.00, "SE band"),
    (30.00, 72.00, "SE band"),
    (33.96, 73.30, "wiggle pad"),
    (26.50, 30.00, "sliver y30"),
    (26.50, 20.00, "sliver y20"),
    (26.50, 15.00, "sliver y15"),
    (27.00, 22.00, "between anti bands"),
    (29.00, 40.00, "center-east"),
]
BPTS = [
    (30.00, 15.00, "B under F-island via"),
    (30.00, 10.00, "B under F-island via"),
    (31.00, 10.00, "B under F-island via"),
    (33.00, 20.00, "B under F-island via"),
    (29.00, 15.00, "B under F-island via"),
    (32.00, 15.00, "B under F-island via"),
    (30.00, 12.00, "B under F-island via"),
    (30.00, 18.00, "B under F-island via"),
    (27.00, 10.00, "B NE"),
    (2.50, 71.20, "stitch candidate"),
    (2.00, 71.20, "stitch west"),
    (3.00, 71.20, "stitch east"),
    (2.50, 65.00, "B west low"),
    (2.50, 50.00, "B west mid"),
    (2.50, 45.00, "B west"),
    (10.00, 71.00, "B south band"),
    (15.00, 71.00, "B south band"),
    (30.00, 45.00, "B center-east"),
    (30.00, 40.00, "B center-east"),
    (30.00, 60.00, "B center-east low"),
    (31.00, 55.00, "B east"),
    (33.30, 55.00, "B far east"),
    (29.00, 20.00, "B NE"),
    (30.50, 50.00, "B center-east"),
    (33.00, 50.00, "B far east"),
    (33.96, 73.30, "wiggle pad B"),
]
for x, y, tag in FPTS:
    print("F (%6.2f,%6.2f) %-22s -> %s" % (x, y, tag, which("F", x, y)))
for x, y, tag in BPTS:
    print("B (%6.2f,%6.2f) %-22s -> %s" % (x, y, tag, which("B", x, y)))

print("-- pads inside island fills (F idx1 / B idx0) --")
for ref, pn, x, y, f, bb in pads:
    hf = which("F", x, y)
    hb = which("B", x, y)
    i_f = "1" in hf.split(",")
    i_b = "0" in hb.split(",")
    if i_f or i_b:
        print("  %s.%s @ (%6.2f,%6.2f) Fpoly=%s Bpoly=%s onF=%s onB=%s"
              % (ref, pn, x, y, hf, hb, f, bb))
