# p4_silk_report.py — dump all silk violations from current DRC JSON (stdlib only)
import json

d = json.load(open('ST909B-4G_drc_violations.json', encoding='utf-8'))
n = 0
for v in d['violations']:
    if not v['type'].startswith('silk'):
        continue
    n += 1
    print('--- #%d %s (%s)' % (n, v['type'], v['severity']))
    print('   desc:', v['description'])
    for it in v['items']:
        p = it.get('pos', {})
        print('   item @ (%.2f, %.2f) %s' % (p.get('x', -99), p.get('y', -99), it['description']))
        print('      uuid', it['uuid'])
print('total silk violations:', n)
