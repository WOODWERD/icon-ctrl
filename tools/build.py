"""Build the Print set release from the approved icons (IC-R70, IC-R71).

    .venv/bin/python tools/build.py x0.0.1

Reads print/plan.json, print/results/*.json and print/<key>.svg (all kept
local), and writes the public files:
  print/icons.json            the record of every icon, no maker details
  dist/print/icons.js         Box Ctrl's module shape, with filled paths
  dist/print/svg/<key>.svg    one flat SVG per icon on the 24-unit box
  dist/print/png/<size>/      300 dpi at 22.7 and 10 mm, 203 dpi at 10 mm
  dist/print/fallback.json    variant -> family
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUPS = ['Power, cutting', 'Power, shaping', 'Power, drill and drive', 'Shop and site', 'Plumbing and electrical',
          'Test and measure', 'Outdoor', 'Hand tools', 'Consumables', 'Kits', 'Shop places']
TRADEMARKS = {'domino', 'rotex', 'systainer', 'sortainer', 'packout', 'tstak', 'quick-grip'}
PNGS = [('22.7mm-300dpi', 268, False), ('10mm-300dpi', 118, False), ('10mm-203dpi', 80, True)]
NOTICE = open(os.path.join(ROOT, 'NOTICE.md')).read().split('\n', 2)[2].strip()


def flatten(svg):
    """potrace path data plus its transform -> absolute path in 24-unit space."""
    t = re.search(r'transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+) [-\d.]+\) translate\(0 ([-\d.]+)\)"', svg)
    tx, ty, a, h = (float(v) for v in t.groups())
    d = re.search(r' d="([^"]+)"', svg).group(1)
    pt = lambda x, y: (tx + a * x, ty - a * (y + h))
    toks = re.findall(r'[MmLlCcZz]|-?\d*\.?\d+(?:e-?\d+)?', d)
    out, i, cmd, cx, cy, sx, sy = [], 0, None, 0.0, 0.0, 0.0, 0.0
    f = lambda v: f'{v:.1f}'.rstrip('0').rstrip('.')
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]):
            cmd = toks[i]; i += 1
            if cmd in 'Zz':
                out.append('Z'); cx, cy = sx, sy
                continue
        n = {'M': 2, 'm': 2, 'L': 2, 'l': 2, 'C': 6, 'c': 6}[cmd]
        v = [float(x) for x in toks[i:i + n]]; i += n
        rel = cmd.islower()
        if cmd in 'Mm':
            x, y = (cx + v[0], cy + v[1]) if rel else (v[0], v[1])
            cx, cy, sx, sy = x, y, x, y
            out.append('M' + ' '.join(f(c) for c in pt(x, y)))
            cmd = 'l' if rel else 'L'
        elif cmd in 'Ll':
            x, y = (cx + v[0], cy + v[1]) if rel else (v[0], v[1])
            cx, cy = x, y
            out.append('L' + ' '.join(f(c) for c in pt(x, y)))
        else:
            ps = [(cx + v[k], cy + v[k + 1]) if rel else (v[k], v[k + 1]) for k in (0, 2, 4)]
            cx, cy = ps[2]
            out.append('C' + ' '.join(f(c) for p in ps for c in pt(*p)))
    return ''.join(out)


def png(svg_path, px, bits, dst):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['qlmanage', '-t', '-s', str(px * 4), '-o', tmp, svg_path], capture_output=True, check=True)
        im = Image.open(os.path.join(tmp, os.path.basename(svg_path) + '.png')).convert('RGBA')
    flat = Image.new('RGBA', im.size, (255, 255, 255, 255))
    flat.alpha_composite(im)
    g = flat.convert('L').resize((px, px), Image.LANCZOS)
    if bits:
        g = g.point(lambda v: 0 if v < 128 else 255, '1')
        g.save(dst)
    else:
        alpha = g.point(lambda v: 255 - v)
        out = Image.new('RGBA', (px, px), (12, 11, 9, 0))
        out.putalpha(alpha)
        out.save(dst)


def main(version):
    plan = json.load(open(os.path.join(ROOT, 'print/plan.json')))['icons']
    dist = os.path.join(ROOT, 'dist/print')
    shutil.rmtree(dist, ignore_errors=True)
    for sub in ['svg'] + [f'png/{name}' for name, _, _ in PNGS]:
        os.makedirs(os.path.join(dist, sub))
    records, icons, missing = [], {}, []
    for p in plan:
        rp = os.path.join(ROOT, 'print/results', p['key'] + '.json')
        r = json.load(open(rp)) if os.path.exists(rp) else {}
        if r.get('status') != 'approved':
            missing.append(p['key'])
            continue
        path = flatten(open(os.path.join(ROOT, 'print', p['key'] + '.svg')).read())
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
               f'<path fill="currentColor" fill-rule="evenodd" d="{path}"/></svg>\n')
        sp = os.path.join(dist, 'svg', p['key'] + '.svg')
        open(sp, 'w').write(svg)
        for name, px, bits in PNGS:
            png(sp, px, bits, os.path.join(dist, 'png', name, p['key'] + '.png'))
        # Trademarked product names stay out of the set (IC-R05).
        words = ' '.join(w for w in dict.fromkeys(f"{p['name']} {p['words']} {p['family'].replace('-', ' ')}".lower().split()) if w not in TRADEMARKS)
        icons[p['key']] = dict(key=p['key'], name=p['name'], group=p['group'], family=p['family'], words=words, f=path)
        records.append(dict(key=p['key'], name=p['name'], set='print', group=p['group'], family=p['family'], words=words,
                            status='approved', approved=r.get('approved'), added=version, changed=version, licence='MIT'))
    json.dump(dict(version=version, icons=records), open(os.path.join(ROOT, 'print/icons.json'), 'w'), indent=1)
    fallback = {k: i['family'] for k, i in icons.items() if i['family'] != k and i['family'] in icons}
    json.dump(fallback, open(os.path.join(dist, 'fallback.json'), 'w'), indent=1)
    groups = [(g, [k for k, i in icons.items() if i['group'] == g]) for g in GROUPS]
    rows = ',\n'.join(f"  {json.dumps(k)}: {json.dumps(dict(key=k, name=i['name'], d='', f=i['f'], family=i['family'], words=i['words'], rot=0))}"
                      for k, i in icons.items())
    js = f'''// Icon Ctrl Print set {version}. Generated by tools/build.py; do not edit by hand.
// Each icon is a filled path on a 24 x 24 box (`f`, drawn with the even-odd rule). `d` stays empty.
// MIT licence. {NOTICE.replace(chr(10), ' ')}
export const ICONS = {{
{rows}
}};
export const ICON_GROUPS = {json.dumps([dict(group=g, keys=ks) for g, ks in groups if ks])};
export const FALLBACK = {json.dumps(fallback)};

// A word over five letters also matches on its first part, so "oscillator" finds "oscillating".
export const stem = (w) => (w.length > 5 ? w.slice(0, Math.max(5, w.length - 3)) : w);
export const searchWords = (q) => String(q).trim().toLowerCase().split(/\\s+/).filter(Boolean).map(stem);

export function searchIcons(q) {{
  const t = searchWords(q);
  return Object.values(ICONS).filter((i) => t.every((w) => i.words.includes(w) || i.key.includes(w)));
}}
'''
    open(os.path.join(dist, 'icons.js'), 'w').write(js)
    print(f'{len(icons)} icons built, {len(missing)} not approved: {missing}')
    print(f'icons.js {os.path.getsize(os.path.join(dist, "icons.js")) // 1024} KB')


if __name__ == '__main__':
    main(sys.argv[1])
