# Extract text WITH coordinates from PDFs (no external libs).
# Goal: package-dimension figures store pad numbers/labels as text at draw positions.
import re, zlib, os, sys

def pdf_streams(path):
    data = open(path, 'rb').read()
    out = []
    for m in re.finditer(rb'\bstream\r?\n', data):
        start = m.end()
        end = data.find(b'endstream', start)
        if end < 0:
            continue
        try:
            out.append(zlib.decompress(data[start:end]))
        except Exception:
            try:
                out.append(zlib.decompress(data[start:end].rstrip(b'\r\n')))
            except Exception:
                pass
    return out

NUM = rb'[-+]?\d*\.?\d+'

def parse_text(stream):
    items = []
    x = y = 0.0
    lx = ly = 0.0
    # token stream: match ops
    pos = 0
    txt_ops = re.finditer(
        NUM + rb'\s+' + NUM + rb'\s+Td|' + NUM + rb'\s+TD|' +
        (NUM + rb'\s+') * 5 + NUM + rb'\s+Tm|' +
        rb'<<.*?>>\s*Tj|' + rb'<[^>]*>\s*Tj|' + rb'\((?:[^()\\]|\\.)*\)\s*Tj|' +
        rb'\[(?:[^\[\]]|\\.)*\]\s*TJ', stream, re.S)
    for m in txt_ops:
        t = m.group(0)
        if t.endswith(b'Tm'):
            v = re.findall(NUM, t)
            x, y = float(v[4]), float(v[5])
            lx, ly = x, y
        elif t.endswith(b'Td') or t.endswith(b'TD'):
            v = re.findall(NUM, t)
            if len(v) >= 2:
                lx += float(v[0]); ly += float(v[1])
                x, y = lx, ly
        elif t.endswith(b'Tj') or t.endswith(b'TJ'):
            s = b''
            if t.startswith(b'('):
                s = re.sub(rb'\\([()\\])', rb'\1', t[1:t.rfind(b')')])
            elif t.startswith(b'<'):
                hx = re.sub(rb'\s', b'', t[1:t.rfind(b'>')])
                try:
                    bs = bytes.fromhex(hx.decode())
                except Exception:
                    continue
                # try 1-byte ascii, then 2-byte utf16/cid-ish where byte pairs printable
                if all(32 <= c < 127 for c in bs):
                    s = bs
                else:
                    # cid: take pairs; keep printable latin1 pairs
                    ps = b''
                    for i in range(0, len(bs) - 1, 2):
                        pair = bs[i:i + 2]
                        if 32 <= pair[0] < 127 and 32 <= pair[1] < 127:
                            ps += pair[1:2]
                    s = ps
                    if not s:
                        # single byte ascii subset (ascii codes map straight in some fonts)
                        s = bytes(c for c in bs if 32 <= c < 127)
            elif t.startswith(b'['):
                for pm in re.finditer(rb'\((?:[^()\\]|\\.)*\)|<[^>]*>', t):
                    s += parse_text(pm.group(0) + b' Tj')[0][1].encode('latin1', 'ignore')
                s = s.encode('latin1', 'ignore') if isinstance(s, str) else s
            text = s.decode('latin1', 'ignore').strip()
            if text:
                items.append((round(y, 2), round(x, 2), text))
    return items

def run(path, outdir):
    os.makedirs(outdir, exist_ok=True)
    streams = pdf_streams(path)
    allitems = []
    for i, st in enumerate(streams):
        if b'BT' not in st or b'ET' not in st:
            continue
        for chunk in re.split(rb'ET', st):
            if b'BT' not in chunk:
                continue
            try:
                allitems.extend(parse_text(chunk))
            except Exception as e:
                pass
    # dedupe + sort
    seen = set(); uniq = []
    for it in allitems:
        k = (it[0], it[1], it[2])
        if k not in seen:
            seen.add(k); uniq.append(it)
    with open(os.path.join(outdir, 'text_coords.txt'), 'w', encoding='utf-8') as f:
        for y, x, t in sorted(uniq):
            f.write(f'{y:9.2f} {x:9.2f} | {t}\n')
    digits = [t for _, _, t in uniq if re.fullmatch(r'\d{1,3}', t)]
    print(f'{os.path.basename(path)}: streams={len(streams)} text_items={len(uniq)} pure_numbers={len(digits)}')

for p in sys.argv[1:]:
    run(p, os.path.join(os.path.dirname(p), 'pdf_text'))
