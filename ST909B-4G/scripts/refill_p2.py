# refill_p2.py — refill zone หลัง swap (ต้องรันคนละ process กับการแก้บอร์ด — pattern add_zones_v1.py)
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
print('zones:')
for z in b.Zones():
    try:
        ko = z.GetIsKeepout()
    except Exception:
        ko = '?'
    print('   net=%-10s layer=%-5s keepout=%s' % (z.GetNetname(), z.GetLayerName(), ko))

ok = pcbnew.ZONE_FILLER(b).Fill(b.Zones())
print('fill ok:', ok)
if ok:
    filled = 0
    for z in b.Zones():
        try:
            if z.IsFilled():
                filled += 1
        except Exception:
            pass
    print('filled zones after:', filled)
    b.Save(BOARD)
    print('saved')
else:
    print('NOT saved (fill failed)')
