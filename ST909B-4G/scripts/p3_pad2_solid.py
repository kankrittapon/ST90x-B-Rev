# p3_pad2_solid.py — set U1 pad 2 (/GND) zone connection to SOLID (FULL).
# Root cause: PKEY F lane must traverse the 0.70-wide west corridor (x 0.50..1.20)
# past pad2 (y 10.20..10.80); any continuous lane there kills the pad's west spoke
# (no fill west of the lane: zone edge 0.50, lane anti 0.30..0.90), and N/S spokes
# are structurally sealed by adjacent pad antis (thermal gap 0.3 > 0.40 inter-pad
# gap). East spoke alone -> actual 1 < min 2 -> starved_thermal.
# Fix: solid pour connection for this GND pad (standard practice for GND pads);
# starved_thermal does not apply to non-thermal (solid) pad connections.
import pcbnew

BOARD = r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
print('board loaded')

u1 = b.FindFootprintByReference('U1')
assert u1, 'U1 missing'
pad = None
for p in u1.Pads():
    if p.GetPadName() == '2':
        pad = p
        break
assert pad is not None, 'U1 pad 2 missing'
print('U1.2 net=%s local_zone_conn(before)=%s' % (
    pad.GetNetname(), pad.GetLocalZoneConnection()))
pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
print('U1.2 local_zone_conn(after)=%s' % pad.GetLocalZoneConnection())
b.Save(BOARD)
print('saved')
