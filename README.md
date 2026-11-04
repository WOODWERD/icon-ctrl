# Icon Ctrl

Icons for tools and shop things, drawn to read on a label. 129 solid silhouettes, from circular saws and drill bits to pliers, clamps, a soldering iron and a work van, each on a 24 × 24 box and tested at label sizes down to 10 mm.

Part of the WOODWERD Toolkit. Status: x0.0.4, public beta.

**Browse the icons:** [woodwerd.github.io/icon-ctrl](https://woodwerd.github.io/icon-ctrl/). Search them, see each one at label size beside its family, and download it. To ask for a new one, use [Request an icon](https://github.com/WOODWERD/icon-ctrl/issues/new?template=request-an-icon.yml).

- Every icon is one filled path, drawn with the even-odd rule, in a single ink.
- Families with variants that read apart at small size: seven sanders, eight drills and drivers, three extractors, three screwdrivers, three pliers and more.
- `dist/print/icons.js` is a drop-in module for Box Ctrl and Tool Ctrl: `ICONS`, `ICON_GROUPS`, `searchIcons`, and `FALLBACK`, which maps a variant to its family.
- `dist/print/svg/` holds one SVG per icon. `dist/print/png/` holds PNGs at 22.7 mm and 10 mm at 300 dpi, and 10 mm at 203 dpi for thermal label printers.
- `print/icons.json` is the record of every icon: key, name, group, family, search words, telling feature, and the versions it was added and last changed in.
- `site/` is the gallery. It reads `icons.js` and `icons.json` from the same release.

## About these icons

These are generic icons for kinds of tools and shop things. Each one was made by WOODWERD with AI help from the common shape of several makers' versions of that tool. They are not drawings of any one product. They are not matched to every product of their type, and they are not intended to represent, copy or stand in for any maker's product or design.

No toolmaker made, endorsed or is affiliated with these icons. Tool, brand and product names, trademarks and product designs belong to their owners.

If you make a tool and think an icon is too close to your product, open an issue and we will redraw or remove it.

MIT licence · by WOODWERD LLC
