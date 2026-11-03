"""Build a private review sheet of every icon made so far.

Reads print/plan.json, print/results/*.json and print/<key>.svg, and writes
one static page with each icon at label and screen sizes, on white and on
a dark band, grouped as in the plan, with what is still to make.

    .venv/bin/python tools/review.py ~/WOODWERD-Claude/projects/icon-ctrl/assets/review/index.html
"""
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# What to look at first, from the batch reports. Each group shows its icons side by side.
FLAGS = [
    ('Likeness: leans on one maker', 'Check against the private reference sheet (IC-R55).', [
        ('router-trim', 'kept the lead maker\'s angled motor top'),
        ('router-edge', 'side view, follows the one maker closely; the weakest icon'),
        ('edge-bander', 'reads strongly as the one product it came from'),
        ('tool-bag', 'close to the lead maker\'s open tote'),
        ('sockets', 'close to the lead maker\'s socket rail'),
        ('bits', 'close to the lead maker\'s bit case'),
        ('screwdriver-cross', 'handle grip line leans to the lead'),
        ('hammer-mallet', 'three-part head from two makers\' soft-faced hammers'),
    ]),
    ('Look-alikes: must read apart at 10 mm', 'Shown side by side; check each row at label size (IC-R52).', [
        ('nailer', 'beside stapler'), ('stapler', 'beside nailer'),
        ('hammer-drill', 'both have a side handle'), ('rotary-hammer', 'both have a side handle'),
        ('screwdriver', 'base screwdriver'), ('screwdriver-flat', 'same handle as cross'), ('screwdriver-cross', 'same handle as flat'),
        ('wrench', 'came out as a combination wrench'), ('wrench-combo', 'the combination variant'),
        ('router-bit', 'may read as a drill bit'), ('drill-bit', 'beside router bit'),
        ('sander', 'base sander'), ('orbital-sander', 'rectangular pad'), ('sander-linear', 'may read as a pad sander'),
    ]),
    ('Small sizes: fine detail or very thin', 'Check the 10 mm and 24 px sizes and a real print.', [
        ('guide-rail', '6 % ink, a thin bar'), ('drywall-sander', '6 % ink'), ('fan', 'grille rings thinner than the gap'),
        ('wall', 'peg holes may fill in; 47 % ink'), ('trimmer', 'thin string ends'), ('expander', 'thin gaps in the nose'),
        ('step-bit', 'thin step gaps'), ('hardware', 'screws inside finer than the gap'), ('hose', 'fine ribs'),
        ('miter-saw', 'many small parts'),
    ]),
    ('Might read as something else', 'Name it without the label.', [
        ('insulation-saw', 'may read as a reciprocating saw with a long blade'),
        ('abrasive', 'may read as a sanding pad'),
        ('crimper', 'drawn as a battery lug crimper, not a hand crimper'),
        ('battery-set', 'two objects on purpose'),
        ('screw', 'cross drive, though the photos showed star and square'),
        ('kit', 'prompt told it to leave out cases'), ('organizer', 'prompt told it to leave out cases and grids'),
    ]),
    ('One run only', 'Made from a single good run; a second run could do better.', [
        ('sander', 'from the first lead-maker test'), ('delta-sander', 'from the first lead-maker test'),
        ('drill', 'from the first lead-maker test'), ('radio', 'second run blocked by the content check'),
        ('joiner', 'second run blocked by the content check'),
    ]),
]


def main(out):
    plan = json.load(open(os.path.join(ROOT, 'print/plan.json')))['icons']
    groups, made, todo = {}, 0, []
    for p in plan:
        rpath = os.path.join(ROOT, 'print/results', p['key'] + '.json')
        spath = os.path.join(ROOT, 'print', p['key'] + '.svg')
        r = json.load(open(rpath)) if os.path.exists(rpath) else None
        if r and r.get('status') in ('in-review', 'approved') and os.path.exists(spath):
            svg = open(spath).read().strip()
            groups.setdefault(p['group'], []).append((p, r, svg))
            made += 1
        else:
            todo.append((p, r))
    svgs = {p['key']: (p, r, svg) for items in groups.values() for p, r, svg in items}

    def strip(svg, sizes):
        return ''.join(f'<span class="s" style="width:{px}px;height:{px}px">{svg}</span>' for px in sizes)

    cards = ['<section class="flags"><h2>Look at these first</h2>']
    for title, how, keys in FLAGS:
        shown = [(k, why) for k, why in keys if k in svgs]
        cards.append(f'<h3>{html.escape(title)} <span>{len(shown)}</span></h3><p class="m">{html.escape(how)}</p><div class="frow">')
        for k, why in shown:
            p, r, svg = svgs[k]
            cards.append(f'<div class="fcard"><div class="row">{strip(svg, (86, 38))}</div><div class="row band">{strip(svg, (38, 24))}</div>'
                         f'<b>{html.escape(p["name"])}</b><code>{k}</code><small class="n">{html.escape(why)}</small></div>')
        cards.append('</div>')
    cards.append('</section><h2 class="all">Every icon</h2>')
    for g, items in groups.items():
        cards.append(f'<h2>{html.escape(g)} <span>{len(items)}</span></h2><div class="grid">')
        for p, r, svg in items:
            sizes = ''.join(f'<span class="s" style="width:{px}px;height:{px}px">{svg}</span>' for px in (86, 38, 24))
            band = ''.join(f'<span class="s" style="width:{px}px;height:{px}px">{svg}</span>' for px in (38, 24))
            note = html.escape(r.get('notes') or '')
            cards.append(f'<div class="card"><div class="row">{sizes}</div><div class="row band">{band}</div>'
                         f'<b>{html.escape(p["name"])}</b><code>{p["key"]}</code>'
                         f'<small>{html.escape(r.get("sheet", ""))} sheet · ink {html.escape(str(r.get("ink", "")))}</small>'
                         + (f'<small class="n">{note}</small>' if note else '') + '</div>')
        cards.append('</div>')
    rest = ''.join(f'<li><code>{p["key"]}</code> {html.escape(p["name"])}'
                   + (f' — {html.escape(r.get("status", ""))}: {html.escape(r.get("notes", ""))}' if r else '') + '</li>' for p, r in todo)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Icon Ctrl review</title><style>
body{{margin:0;background:#F9F7F3;color:#0C0B09;font:14px/1.5 Inter,-apple-system,sans-serif;padding:34px 21px}}
h1{{margin:0 0 5px;font-size:21px;letter-spacing:.06em;text-transform:uppercase}} p.m{{margin:0 0 21px;color:#5D6267}}
h2{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;border-bottom:1px solid #E2E0DA;padding-bottom:5px;margin:34px 0 13px}} h2 span{{color:#5D6267;font-weight:400}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:13px}}
.card{{background:#fff;border:1px solid #E2E0DA;border-radius:8px;padding:13px;display:flex;flex-direction:column;gap:5px}}
.row{{display:flex;align-items:flex-end;gap:13px;padding:8px;border-radius:5px}} .band{{background:#0C0B09;color:#fff}}
.s{{display:inline-block}} .s svg{{width:100%;height:100%;display:block}}
code{{font:12px "JetBrains Mono",monospace;color:#5D6267}} small{{color:#5D6267}} small.n{{color:#9A5A10}}
ul{{columns:3;font-size:13px}}
.flags{{background:#F0E2C8;border-radius:13px;padding:8px 21px 21px;margin-bottom:21px}} .flags h2{{border-color:#C4944A}}
h3{{font-size:13px;margin:21px 0 0}} h3 span{{color:#5D6267;font-weight:400}} .flags p.m{{margin:0 0 8px}}
.frow{{display:flex;flex-wrap:wrap;gap:8px}} .fcard{{background:#fff;border:1px solid #E2E0DA;border-radius:8px;padding:8px;width:170px;display:flex;flex-direction:column;gap:3px}}
h2.all{{margin-top:34px}}</style></head><body>
<h1>Icon Ctrl · review</h1><p class="m">{made} of {len(plan)} made. Print sizes drawn at screen size; the printed proof is the real test.</p>
{''.join(cards)}<h2>Still to make <span>{len(todo)}</span></h2><ul>{rest}</ul></body></html>'''
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(page)
    print(f'{out}: {made} made, {len(todo)} to go')


if __name__ == '__main__':
    main(os.path.expanduser(sys.argv[1]))
