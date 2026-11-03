"""Trace a chosen Weave output into a Print set SVG (IC-R65).

Flattens the PNG onto white, thresholds it, traces it with potrace, and
fits the drawing inside 2-22 of the 24-unit box, coordinates rounded to
0.05 unit. Prints the ink share of the whole box (IC-R33).

    .venv/bin/python tools/trace.py work/drill-run2.png print/drill.svg
"""
import re
import subprocess
import sys
import tempfile
from PIL import Image

BOX, LO, HI = 24, 2, 22


def main(src, dst):
    im = Image.open(src).convert('RGBA')
    flat = Image.new('RGB', im.size, (255, 255, 255))
    flat.paste(im, mask=im.split()[3])
    bw = flat.convert('L').point(lambda v: 0 if v < 128 else 255, '1')
    ink = bw.point(lambda v: 255 - v)
    x0, y0, x1, y1 = ink.getbbox()
    with tempfile.TemporaryDirectory() as tmp:
        bw.save(tmp + '/in.bmp')
        subprocess.run(['potrace', '-s', '--flat', '-t', '40', '-k', '0.5', tmp + '/in.bmp', '-o', tmp + '/out.svg'], check=True)
        svg = open(tmp + '/out.svg').read()
    d = ' '.join(re.findall(r'<path d="([^"]+)"', svg, flags=re.S)).replace('\n', ' ')
    # potrace draws in tenths of a pixel with y flipped; fit the ink box into 2-22.
    w, h = x1 - x0, y1 - y0
    s = (HI - LO) / max(w, h)
    tx = LO + ((HI - LO) - w * s) / 2 - x0 * s
    ty = LO + ((HI - LO) - h * s) / 2 - y0 * s
    t = f'translate({tx:.2f} {ty:.2f}) scale({s / 10:.6f} {-s / 10:.6f}) translate(0 {-im.height * 10})'
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BOX} {BOX}">'
           f'<path fill="currentColor" fill-rule="evenodd" transform="{t}" d="{d}"/></svg>\n')
    open(dst, 'w').write(out)
    inked = ink.crop((x0, y0, x1, y1)).histogram()[255]
    share = inked * s * s / (BOX * BOX)
    print(f'{dst}  ink {share:.0%}  {len(out) // 1024} KB')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
