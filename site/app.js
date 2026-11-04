// Icon Ctrl gallery (IC-R80 to IC-R84). Reads the release: icons.js for the shapes, icons.json for the record.
import { ICONS, ICON_GROUPS, searchIcons } from './icons.js';

const REPO = 'https://github.com/WOODWERD/icon-ctrl';
const REQUEST = `${REPO}/issues/new?template=request-an-icon.yml`;
const PNGS = [['22.7mm-300dpi', 'PNG 22.7 mm'], ['10mm-300dpi', 'PNG 10 mm'], ['10mm-203dpi', 'PNG 10 mm thermal']];
const STRIP = [[86, '22.7 mm'], [48, '48 px'], [38, '10 mm'], [24, '24 px']];
const BAND = [[38, '10 mm'], [24, '24 px']];

const app = document.getElementById('app');
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const glyph = (i, px) => `<svg class="g" viewBox="0 0 24 24" width="${px}" height="${px}" aria-hidden="true"><path fill-rule="evenodd" d="${i.f}"/></svg>`;
// The same file the build writes to dist/print/svg (IC-R70).
const svgFile = (i) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" d="${i.f}"/></svg>\n`;

let record = {};
let review = [];
let version = '';
const state = { q: '', group: '', scroll: 0, closed: new Set() };

function tile(i) {
  return `<a class="tile" href="#i/${esc(i.key)}"><span class="art">${glyph(i, 48)}</span><b>${esc(i.name)}</b><span class="k">${esc(i.key)}</span></a>`;
}

function gallery() {
  const all = Object.keys(ICONS).length;
  const hits = state.q.trim() ? searchIcons(state.q) : Object.values(ICONS);
  const keys = new Set(hits.map((i) => i.key));
  const groups = ICON_GROUPS.filter((g) => !state.group || g.group === state.group)
    .map((g) => ({ name: g.group, items: g.keys.filter((k) => keys.has(k)).map((k) => ICONS[k]) }))
    .filter((g) => g.items.length);
  const shown = groups.reduce((n, g) => n + g.items.length, 0);
  const options = ICON_GROUPS.map((g) => `<option value="${esc(g.group)}"${g.group === state.group ? ' selected' : ''}>${esc(g.group)}</option>`).join('');
  const body = shown ? groups.map((g) => `<details class="group"${state.closed.has(g.name) ? '' : ' open'} data-group="${esc(g.name)}">
      <summary><span class="gn">${esc(g.name)}</span><span class="gc">${g.items.length}</span></summary>
      <div class="tiles">${g.items.map(tile).join('')}</div></details>`).join('')
    : `<div class="empty"><b>No icons match “${esc(state.q)}”${state.group ? ` in ${esc(state.group)}` : ''}</b>
      <span>Searched names, keys and search words in ${state.group ? 'this group' : `all ${all} icons`}.</span>
      <span class="row"><a class="key go" href="${REQUEST}">Request an icon</a><button class="key" type="button" id="clear">Clear search</button></span></div>`;
  app.innerHTML = `<div class="fbar">
      <label class="search"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg><input type="search" id="q" value="${esc(state.q)}" placeholder="Search icons, such as router, tenon or delta" aria-label="Search icons" autocomplete="off"></label>
      <label class="pick">Group <select id="group" aria-label="Group"><option value="">All</option>${options}</select></label>
      <span class="count">${shown === all ? '' : `<b class="mono">${shown}</b> of `}<b class="mono">${all}</b> icons</span>
    </div>${body}`;
  const q = document.getElementById('q');
  q.oninput = () => { state.q = q.value; redrawKeepingFocus(); };
  document.getElementById('group').onchange = (e) => { state.group = e.target.value; gallery(); };
  const clear = document.getElementById('clear');
  if (clear) clear.onclick = () => { state.q = ''; state.group = ''; gallery(); document.getElementById('q').focus(); };
  app.querySelectorAll('details.group').forEach((d) => { d.ontoggle = () => { if (d.open) state.closed.delete(d.dataset.group); else state.closed.add(d.dataset.group); }; });
}

function redrawKeepingFocus() {
  const pos = document.getElementById('q').selectionStart;
  gallery();
  const q = document.getElementById('q');
  q.focus();
  q.setSelectionRange(pos, pos);
}

function detail(key) {
  const i = ICONS[key];
  if (!i) { location.hash = ''; return; }
  const r = record[key] || {};
  const fam = Object.values(ICONS).filter((m) => m.family === i.family);
  const group = ICON_GROUPS.find((g) => g.keys.includes(key))?.group || '';
  const strip = (list, band) => list.map(([px, label]) => `<div class="sz">${glyph(i, px)}<span>${label}${band ? ' · on a band' : ''}</span></div>`).join('');
  const famRow = fam.length > 1 ? `<span class="cap">Family at 10 mm and 24 px</span>
      <div class="fam">${fam.map((m) => `<a class="mem${m.key === key ? ' here' : ''}" href="#i/${esc(m.key)}"${m.key === key ? ' aria-current="page"' : ''}>
        <span class="pair">${glyph(m, 38)}${glyph(m, 24)}</span><b>${esc(m.name)}</b><span class="k">${esc(m.key)}</span></a>`).join('')}</div>
      <span class="small">Every variant must read apart from its siblings at 10 mm. An app that doesn't know a variant shows its family's icon.</span>` : '';
  app.innerHTML = `<a class="back" href="#">‹ All icons</a>
    <div class="detail">
      <div class="hero">
        <div class="big">${glyph(i, 144)}</div>
        <span class="cap">Size strip</span>
        <div class="sizes">${strip(STRIP)}</div>
        <div class="sizes band">${strip(BAND, true)}</div>
        <span class="small">Print sizes are drawn at their size on a standard screen. The printed label is the real test.</span>
      </div>
      <div class="hero">
        <div class="dname"><h2>${esc(i.name)}</h2><span class="st ok">Approved</span></div>
        <dl class="facts">
          <dt>Key</dt><dd class="mono">${esc(key)}</dd>
          <dt>Family</dt><dd class="mono">${esc(i.family)}</dd>
          <dt>Group</dt><dd>${esc(group)}</dd>
          ${r.feature ? `<dt>Telling feature</dt><dd>${esc(r.feature)}</dd>` : ''}
          <dt>Search words</dt><dd>${esc(i.words)}</dd>
          <dt>Set</dt><dd>Print</dd>
          <dt>Version</dt><dd class="mono">Added ${esc(r.added || version)} · changed ${esc(r.changed || version)}</dd>
          ${r.approved ? `<dt>Approved</dt><dd class="mono">${esc(r.approved)}</dd>` : ''}
          <dt>Licence</dt><dd>MIT</dd>
        </dl>
        <div class="row"><button class="key go" type="button" id="svg">Download SVG</button>${PNGS.map(([dir, label]) => `<a class="key" href="${REPO}/blob/main/dist/print/png/${dir}/${esc(key)}.png">${label}</a>`).join('')}<button class="key" type="button" id="copy">Copy key</button></div>
        ${famRow}
      </div>
    </div>`;
  document.getElementById('svg').onclick = () => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([svgFile(i)], { type: 'image/svg+xml' }));
    a.download = `${key}.svg`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  };
  const copy = document.getElementById('copy');
  copy.onclick = () => navigator.clipboard.writeText(key).then(() => { copy.textContent = 'Key copied'; }, () => { copy.textContent = 'Copy failed'; });
  window.scrollTo(0, 0);
}

// Read only (IC-R83): approval is recorded in the repo, never on this page.
function reviewView() {
  app.innerHTML = `<div class="note"><b>Read only</b><span>Drew approves each icon in the repo. This page shows what is waiting.</span></div>
    ${review.length ? review.map((r) => `<div class="note"><b>${esc(r.name)}</b><span class="mono">${esc(r.key)}</span><span>In review</span></div>`).join('')
    : `<div class="empty"><b>Nothing in review</b><span>Every icon in ${esc(version)} is approved. New icons show here, with their size strip and family row, while they wait.</span><a class="key" href="${REQUEST}">Request an icon</a></div>`}`;
  window.scrollTo(0, 0);
}

function route() {
  const h = location.hash.slice(1);
  const view = h === 'review' ? 'review' : 'gallery';
  document.querySelectorAll('[data-view]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.view === view)));
  if (h.startsWith('i/')) return detail(decodeURIComponent(h.slice(2)));
  if (h === 'review') return reviewView();
  gallery();
  window.scrollTo(0, state.scroll);
}

document.querySelectorAll('[data-view]').forEach((b) => { b.onclick = () => { location.hash = b.dataset.view === 'review' ? 'review' : ''; }; });
// Keep the gallery's place when an icon is opened, so Back returns to it.
addEventListener('click', (e) => { if (e.target.closest('a.tile') && !location.hash) state.scroll = scrollY; });
addEventListener('hashchange', route);

fetch('icons.json').then((r) => r.json()).then((data) => {
  version = data.version;
  data.icons.forEach((i) => { record[i.key] = i; });
  review = data.icons.filter((i) => i.status === 'in-review');
}).catch(() => {}).finally(() => {
  document.getElementById('total').textContent = Object.keys(ICONS).length;
  document.getElementById('reviewCount').textContent = review.length;
  route();
});
