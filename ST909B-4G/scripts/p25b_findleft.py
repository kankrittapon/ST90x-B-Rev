# p25b_findleft.py — หา DEL_TRACKS ที่ยังอยู่บนบอร์ด (ลบไม่ครบ 33/34)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
TOL = pcbnew.FromMM(0.06)
LAYER = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu}

b = pcbnew.LoadBoard(BOARD)
codes = {}


def nc(name):
    if name not in codes:
        codes[name] = b.FindNet(name).GetNetCode()
    return codes[name]


def match(t, net, lay, seg):
    if t.GetNetCode() != nc(net) or t.GetLayer() != LAYER[lay]:
        return False
    (x1, y1), (x2, y2) = seg
    x1, y1, x2, y2 = (pcbnew.FromMM(x1), pcbnew.FromMM(y1),
                      pcbnew.FromMM(x2), pcbnew.FromMM(y2))
    s, e = t.GetStart(), t.GetEnd()
    return ((abs(s.x - x1) < TOL and abs(s.y - y1) < TOL and abs(e.x - x2) < TOL and abs(e.y - y2) < TOL) or
            (abs(s.x - x2) < TOL and abs(s.y - y2) < TOL and abs(e.x - x1) < TOL and abs(e.y - y1) < TOL))


SEGS = [
    ('/LED_GPS', 'B', [(21.16, 61.25), (23.60, 61.25)]),
    ('/LED_GPS', 'B', [(23.60, 61.25), (23.60, 58.00)]),
    ('/LED_GPS', 'B', [(23.60, 58.00), (23.60, 30.10)]),
    ('/LED_GPS', 'F', [(23.60, 30.10), (0.75, 30.10)]),
    ('/LED_GPS', 'F', [(0.75, 30.10), (0.75, 4.50)]),
    ('/LED_GPS', 'F', [(0.75, 4.50), (11.71, 4.50)]),
    ('/LED_GPS', 'B', [(11.71, 4.50), (11.71, 13.00)]),
    ('/LED_GPS', 'B', [(11.71, 11.40), (11.71, 13.00)]),
    ('/LED_4G', 'B', [(19.25, 68.25), (25.00, 68.25)]),
    ('/LED_4G', 'B', [(25.00, 68.25), (27.00, 68.25)]),
    ('/LED_4G', 'B', [(27.00, 68.25), (27.00, 14.90)]),
    ('/LED_4G', 'B', [(27.00, 14.90), (17.71, 14.90)]),
    ('/LED_4G', 'B', [(17.71, 14.90), (17.71, 14.65)]),
    ('/LED_4G', 'B', [(17.71, 14.65), (17.71, 13.00)]),
    ('/LED_CHR', 'F', [(26.30, 23.00), (26.30, 15.45)]),
    ('/LED_CHR', 'F', [(25.50, 23.00), (26.30, 23.00)]),
    ('/LED_CHR', 'F', [(25.50, 28.00), (25.50, 23.00)]),
    ('/LED_CHR', 'F', [(26.30, 28.00), (25.50, 28.00)]),
    ('/LED_CHR', 'F', [(26.30, 67.60), (26.30, 28.00)]),
    ('/LED_CHR', 'B', [(26.30, 15.45), (14.71, 15.45)]),
    ('/LED_CHR', 'B', [(19.75, 62.66), (19.75, 67.60)]),
    ('/LED_CHR', 'B', [(19.75, 67.60), (26.30, 67.60)]),
    ('/LED_EN', 'B', [(21.16, 59.75), (24.35, 59.75)]),
    ('/LED_EN', 'B', [(24.35, 12.20), (22.94, 12.20)]),
    ('/LED_EN', 'B', [(26.00, 12.20), (22.94, 12.20)]),
    ('/LED_EN', 'F', [(24.35, 59.75), (26.00, 59.75)]),
    ('/LED_EN', 'F', [(26.00, 59.75), (26.00, 12.20)]),
    ('/BOOT', 'B', [(18.75, 68.90), (34.00, 68.90)]),
    ('/BOOT', 'B', [(34.00, 27.20), (33.00, 27.20)]),
    ('/BOOT', 'B', [(34.00, 68.90), (34.00, 27.20)]),
    ('/BOOT', 'F', [(33.00, 27.20), (27.00, 27.20)]),
    ('/GPS_RX', 'F', [(9.50, 37.00), (9.50, 45.50)]),
    ('/GPS_RX', 'B', [(9.50, 45.50), (2.25, 45.50)]),
    ('/VBAT', 'F', [(6.50, 43.50), (1.00, 43.50)]),
]
tracks = list(b.GetTracks())
for i, (net, lay, seg) in enumerate(SEGS):
    found = [t for t in tracks if t.Type() == pcbnew.PCB_TRACE_T and match(t, net, lay, seg)]
    if found:
        s, e = found[0].GetStart(), found[0].GetEnd()
        print('STILL PRESENT idx %d: %s %s (%.2f,%.2f)->(%.2f,%.2f)' % (
            i, net, lay, pcbnew.ToMM(s.x), pcbnew.ToMM(s.y), pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)))
print('check done')
