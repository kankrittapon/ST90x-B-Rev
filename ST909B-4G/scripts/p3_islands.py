# p3_islands.py — find isolated GND zone-fill islands after P3 refill.
# For every zone fill outline (per layer), count GND vias/pads/tracks inside it.
# A fill region with zero connections is the island DRC complains about.
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


# collect GND primitives
gnd_vias, gnd_tracks, gnd_pads = [], [], []
for t in b.GetTracks():
    net = t.GetNetname()
    if net != "/GND":
        continue
    if t.GetClass() == "PCB_VIA":
        p = t.GetPosition()
        gnd_vias.append((p.x / MM, p.y / MM))
    else:
        s, e = t.GetStart(), t.GetEnd()
        gnd_tracks.append((s.x / MM, s.y / MM, e.x / MM, e.y / MM))
for fp in b.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() != "/GND":
            continue
        p = pad.GetPosition()
        sz = pad.GetSize()
        gnd_pads.append((p.x / MM, p.y / MM, sz.x / MM, sz.y / MM,
                         pad.IsOnLayer(pcbnew.F_Cu), pad.IsOnLayer(pcbnew.B_Cu)))
print("gnd vias=%d tracks=%d pads=%d" % (len(gnd_vias), len(gnd_tracks), len(gnd_pads)))

for z in b.Zones():
    nets = z.GetNetname()
    for layer in z.GetLayerSet().Seq():
        if layer not in (pcbnew.F_Cu, pcbnew.B_Cu):
            continue
        ps = z.GetFilledPolysList(layer)
        ln = "F" if layer == pcbnew.F_Cu else "B"
        for i in range(ps.OutlineCount()):
            chain = ps.COutline(i)
            pts = [(chain.GetPoint(j).x / MM, chain.GetPoint(j).y / MM)
                   for j in range(chain.PointCount())]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            bx = (min(xs), min(ys), max(xs), max(ys))
            nv = sum(1 for (vx, vy) in gnd_vias if pt_in_poly(vx, vy, pts))
            nt = sum(1 for (x1, y1, x2, y2) in gnd_tracks
                     if pt_in_poly((x1 + x2) / 2, (y1 + y2) / 2, pts))
            npd = sum(1 for (px, py, sx, sy, f, bb) in gnd_pads
                      if (f if ln == "F" else bb) and
                      pt_in_poly(px, py, pts))
            print("zone net=%s layer=%s poly#%d bbox=(%.2f,%.2f)-(%.2f,%.2f) "
                  "w=%.2f h=%.2f vias=%d trk-mid=%d pads=%d"
                  % (nets, ln, i, bx[0], bx[1], bx[2], bx[3],
                     bx[2] - bx[0], bx[3] - bx[1], nv, nt, npd))
