import pcbnew
b = pcbnew.LoadBoard(r"D:\Tracker\ST909B-4G\ST909B-4G.kicad_pcb")
tr = vi = 0
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        vi += 1
    else:
        tr += 1
print('tracks', tr, 'vias', vi, 'fps', len(list(b.GetFootprints())))
