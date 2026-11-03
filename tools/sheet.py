"""Build a 1024 x 1024 reference sheet from makers' product photos (IC-R62).

Each photo is cropped (optional box), trimmed to the tool on its plain
background, and fitted. With --lead, the first photo fills the left two
thirds and the rest stack small on the right; without it, all four sit
two by two.

    .venv/bin/python tools/sheet.py --lead out.png lead.png a.png b.png c.png
    .venv/bin/python tools/sheet.py out.png a.png b.png c.png d.png
    a.png@x,y,w,h   crops to that box first
"""
import sys
from PIL import Image, ImageChops

W = 1024


def load(spec):
    path, _, box = spec.partition('@')
    im = Image.open(path)
    im = im.convert('RGBA')
    flat = Image.new('RGB', im.size, (255, 255, 255))
    flat.paste(im, mask=im.split()[3])
    if box:
        x, y, w, h = (int(v) for v in box.split(','))
        flat = flat.crop((x, y, x + w, y + h))
    return trim(flat)


def trim(im):
    # The corner colour is the background; keep everything that differs from it.
    bg = Image.new('RGB', im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg).convert('L').point(lambda v: 255 if v > 24 else 0)
    box = diff.getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    pad = int(max(x1 - x0, y1 - y0) * 0.04)
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def place(sheet, im, x, y, size):
    # Fit to the slot, enlarging small photos as well as shrinking big ones.
    k = size / max(im.width, im.height)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    sheet.paste(im, (x + (size - im.width) // 2, y + (size - im.height) // 2))


def main(argv):
    lead = argv[0] == '--lead'
    if lead:
        argv = argv[1:]
    out, photos = argv[0], [load(p) for p in argv[1:]]
    sheet = Image.new('RGB', (W, W), (255, 255, 255))
    if lead:
        place(sheet, photos[0], 8, 176, 672)
        for i, im in enumerate(photos[1:4]):
            place(sheet, im, 696, 16 + i * 336, 320)
    else:
        for i, im in enumerate(photos[:4]):
            place(sheet, im, (i % 2) * 512 + 16, (i // 2) * 512 + 16, 480)
    sheet.save(out)
    print(out)


if __name__ == '__main__':
    main(sys.argv[1:])
