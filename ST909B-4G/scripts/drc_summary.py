# drc_summary.py — สรุปไฟล์ DRC JSON จาก kicad-cli (อ่านอย่างเดียว) — พิมพ์รายละเอียดครบ
import json
import collections

PATH = r"D:\Tracker\ST909B-4G\ST909B-4G_drc_violations.json"
d = json.load(open(PATH, encoding='utf-8-sig'))
viol = d.get('violations', [])
unc = d.get('unconnected_items', [])
par = d.get('schematic_parity', [])
print('violations: %d  unconnected: %d  parity: %d' % (len(viol), len(unc), len(par)))

cnt = collections.Counter((v.get('severity'), v.get('type')) for v in viol)
print('-- by severity/type --')
for (sev, typ), c in sorted(cnt.items()):
    print('   %-8s %-24s %d' % (sev, typ, c))

def show(v, prefix):
    pos = v.get('items', [{}])[0].get('pos') or {}
    print('%s%-22s (%.2f, %.2f)' % (prefix, v.get('type'), pos.get('x', 0), pos.get('y', 0)))
    print('%s   %s' % (prefix, (v.get('description') or '')[:150]))
    for it in v.get('items', []):
        p = it.get('pos') or {}
        print('%s     - %s @(%.2f, %.2f)' % (
            prefix, (it.get('description') or '')[:90], p.get('x', 0), p.get('y', 0)))

print('-- all ERROR details --')
for v in viol:
    if v.get('severity') == 'error':
        show(v, '  ')

print('-- unconnected details --')
for u in unc:
    show(u, '  ')
