"""r/dataisbeautiful collage for Rings in the Rock. Run from this folder: python3 collage.py
All data are parsed from ../index.html (the DATA object and the Scotland outcrop counts in the page script)."""
import json, re, os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle, Rectangle
HERE = os.path.dirname(os.path.abspath(__file__))
F = '/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/'
for f in ['FrauncesVar.ttf', 'IBMPlexMono-Regular.ttf', 'IBMPlexMono-Medium.ttf', 'SourceSerif4-Regular.ttf', 'SourceSerif4-Semibold.ttf', 'SourceSerif4-It.ttf']:
    fm.fontManager.addfont(F + f)
DISP = fm.FontProperties(fname=F + 'FrauncesVar.ttf', weight=900)
SER = 'Source Serif 4'; MONO = 'IBM Plex Mono'

src = open(os.path.join(HERE, '..', 'index.html'), encoding='utf-8').read()
i = src.index('const DATA = ') + len('const DATA = ')
D = json.JSONDecoder().raw_decode(src[i:])[0]
m = re.search(r'\["On bedrock outcrops", (\d+), (\d+)\], \["On loose stones and slabs", (\d+), (\d+)\]', src)
OUT_R, OUT_N, LOOSE_R, LOOSE_N = map(int, m.groups())

# site dark palette
BG = '#CFCAC0'; FG = '#1A1816'; MUT = '#4F4A43'; LAND = '#BDB6A9'; ROCK = '#3A3733'; RULE = '#A39C90'
COL = {'ring': '#A3191B', 'cup': '#B06A00', 'rock': '#36577D', 'tomb': '#5E3A8C'}
NAME = {'ring': 'Cup and ring', 'cup': 'Cups only', 'rock': 'Carved rock, motifs not coded', 'tomb': 'Passage-tomb art'}
TYPES = D['types']; REGS = D['regs']
P = np.array([[p[0], p[1]] for p in D['pts']]); T = np.array([TYPES[p[2]] for p in D['pts']]); R = np.array([REGS[p[4]] for p in D['pts']])

def svgpath(d):
    v, c = [], []
    for cmd, body in re.findall(r'([MLZ])([^MLZ]*)', d):
        if cmd == 'Z':
            v.append((0, 0)); c.append(Path.CLOSEPOLY); continue
        n = list(map(float, re.findall(r'-?\d+\.?\d*', body)))
        for j in range(0, len(n), 2):
            v.append((n[j], n[j + 1])); c.append(Path.MOVETO if (cmd == 'M' and j == 0) else Path.LINETO)
    return Path(v, c)
PAN = D['panels']; LANDP = [svgpath(p['land']) for p in PAN]
def geo(lon, lat):
    p = PAN[0] if lat > 49.5 else PAN[1]
    return p['ox'] + (lon - p['lon0']) * p['k'] * D['S'], p['oy'] + (p['lat1'] - lat) * D['S']

rng = np.random.default_rng(7)
XMAX = 875
def stipple(a, n, s, alpha, box=None):
    """stone texture: random peck marks on the land"""
    for p, lp in zip(PAN, LANDP):
        x0, y0, w, h = p['ox'], p['oy'], p['w'], p['h']
        if box is not None:
            x0, y0, w, h = box
        q = np.column_stack([rng.uniform(x0, x0 + w, n), rng.uniform(y0, y0 + h, n)])
        q = q[lp.contains_points(q)]
        a.scatter(q[:, 0], q[:, 1], s=s, c='#8C8475', lw=0, alpha=alpha, rasterized=True, zorder=1)

def draw_land(a, clip=None):
    for p, lp in zip(PAN, LANDP):
        pp = PathPatch(lp, fc=LAND, ec='#968E80', lw=.5, zorder=0)
        a.add_patch(pp)
        if clip is not None:
            pp.set_clip_path(clip)
        else:
            rect = Rectangle((p['ox'], p['oy']), min(p['w'], XMAX - p['ox']), p['h'], transform=a.transData)
            pp.set_clip_path(rect)

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)
fig.text(0.04, 0.968, 'The rings that hug the sea', fontproperties=DISP, fontsize=50, color=FG, va='top')
fig.text(0.04, 0.913, 'Cups and rings pecked into stone, 4000 BC onwards, on Europe\'s Atlantic edge. Every carved rock\n'
         'in the open records for Britain, Ireland, Brittany, Galicia and northern Portugal: 4,584 of them.',
         family=SER, fontsize=15, color=FG, va='top', linespacing=1.4)

# ---------- hero: the folded seaboard ----------
ax = fig.add_axes([0.0, 0.345, 0.645, 0.52]); ax.set_facecolor(BG); ax.axis('off')
draw_land(ax)
stipple(ax, 26000, .35, .55)
order = ['rock', 'cup', 'ring', 'tomb']
for t in order:
    q = P[T == t]
    ax.scatter(q[:, 0], q[:, 1], s=26, c=COL[t], lw=0, alpha=.10, zorder=3, rasterized=True)
for t in order:
    q = P[T == t]
    ax.scatter(q[:, 0], q[:, 1], s=3.2, c=COL[t], lw=0, alpha=.95, zorder=4, rasterized=True)
ax.set_xlim(0, XMAX); ax.set_ylim(D['H'] + 5, -5); ax.set_aspect('equal')
# panel dividers and labels
ax.plot([485, 485], [0, D['H']], color=RULE, lw=1)
ax.text(56, 12, 'BRITAIN AND IRELAND', family=MONO, fontsize=11, color=FG, va='top')
ax.text(PAN[1]['ox'] + 8, 12, 'BRITTANY, GALICIA,\nNORTHERN PORTUGAL', family=MONO, fontsize=11, color=FG, va='top', linespacing=1.3)
ax.text(PAN[1]['ox'] + 8, 600, 'Same scale. The map is folded\nat the Bay of Biscay: the two\nends are about 1,200 km apart.',
        family=SER, fontsize=11, color=MUT, va='top', linespacing=1.3)
# place labels
for name, lon, lat, dx, dy, ha in [('Kilmartin', -5.49, 56.13, -14, 0, 'right'), ('Ilkley', -1.83, 53.92, 12, 0, 'left'),
                                  ('Iveragh', -10.0, 51.95, 26, 22, 'left'), ('Inishowen', -7.3, 55.25, -6, -16, 'center'),
                                  ('Mogor', -8.73, 42.37, -10, 12, 'right'), ('Northumberland', -1.95, 55.55, 14, 0, 'left'),
                                  ('Perthshire', -3.9, 56.6, 30, -22, 'left')]:
    x, y = geo(lon, lat)
    ax.annotate(name, xy=(x, y), xytext=(x + dx, y + dy), family=MONO, fontsize=10.5, color=FG, ha=ha, va='center',
                arrowprops=dict(arrowstyle='-', color=FG, lw=.6, shrinkA=1, shrinkB=2) if (dx or dy) else None, zorder=6)
# legend
lx = 0.04; ly = 0.335
for i, t in enumerate(['ring', 'cup', 'rock', 'tomb']):
    xx = lx + [0, 0.20, 0.38, 0.73][i] * 0.9
    n = int((T == t).sum())
    fig.lines.append(plt.Line2D([xx], [ly], marker='o', ms=7, mfc=COL[t], mec=COL[t], ls='', transform=fig.transFigure))
    fig.text(xx + 0.011, ly, f'{NAME[t]}  {n:,}', family=MONO, fontsize=10, color=FG, va='center')

# ---------- right column: numbers ----------
ire = D['coast']['Ireland']
gal_known = [k for k in D['known'] if k['region'] == 'Galicia'][0]
scot = D['scot']
tx = fig.add_axes([0.67, 0.312, 0.31, 0.54]); tx.axis('off')
notes = [(f"{ire['within5']:.0f}%", f"of Irish rock art lies within 5 km of\nthe sea, against {ire['within5_random']:.0f}% of Irish land.\nScotland and Galicia show the same pull."),
         (f"{100 * OUT_R / OUT_N:.0f}% v {100 * LOOSE_R / LOOSE_N:.0f}%", 'of Scottish records carry rings on fixed\noutcrops, against loose stones and slabs.\nRings belonged to places.'),
         (f"{scot['n']:,}", f"cup-marked rocks in Scotland's register;\n{100 * scot['ring'] / scot['n']:.0f}% of them also carry rings.\nCups are everywhere, rings are special."),
         ('1 in 7', f"Galician rock-art stations in the open\ndata ({gal_known['mapped']} of {gal_known['known']:,}). Outside Scotland and\nIreland, treat the map as a minimum.")]
for (big, small), y in zip(notes, [1.0, 0.75, 0.50, 0.25]):
    tx.text(0, y, big, fontproperties=DISP, fontsize=30, color=COL['ring'], va='top', transform=tx.transAxes)
    tx.text(0, y - 0.075, small, family=SER, fontsize=12.5, color=FG, va='top', transform=tx.transAxes, linespacing=1.3)

# ---------- bottom left: circular insets (the "cups") ----------
def inset(rect, lon, lat, rad_deg, title, sub):
    a = fig.add_axes(rect); a.set_facecolor(BG); a.axis('off')
    cx, cy = geo(lon, lat); r = rad_deg * D['S']
    a.set_xlim(cx - r * 1.32, cx + r * 1.32); a.set_ylim(cy + r * 1.32, cy - r * 1.32); a.set_aspect('equal')
    clip = Circle((cx, cy), r, transform=a.transData)
    draw_land(a, clip=clip)
    sea = Circle((cx, cy), r, fc='#C6C3BC', ec='none', zorder=-1); a.add_patch(sea)
    q = np.column_stack([rng.uniform(cx - r, cx + r, 9000), rng.uniform(cy - r, cy + r, 9000)])
    inside = ((q[:, 0] - cx) ** 2 + (q[:, 1] - cy) ** 2) < r * r
    lp = LANDP[0] if lat > 49.5 else LANDP[1]
    q = q[inside & lp.contains_points(q)]
    a.scatter(q[:, 0], q[:, 1], s=.6, c='#8C8475', lw=0, alpha=.6, zorder=1, rasterized=True)
    d2 = (P[:, 0] - cx) ** 2 + (P[:, 1] - cy) ** 2
    sel = d2 < r * r
    for t in order:
        k = sel & (T == t)
        a.scatter(P[k, 0], P[k, 1], s=55, c=COL[t], lw=0, alpha=.15, zorder=3)
        a.scatter(P[k, 0], P[k, 1], s=9, c=COL[t], lw=0, alpha=.95, zorder=4)
    # pecked rings around the cup
    for j, rr in enumerate([1.0, 1.12, 1.24]):
        th = np.linspace(0, 2 * np.pi, int(140 + 30 * j), endpoint=False)
        a.scatter(cx + r * rr * np.cos(th), cy + r * rr * np.sin(th), s=2.2 - .5 * j, c='#3A3631', lw=0, alpha=.85 - .25 * j, zorder=5)
    a.set_title(title, family=MONO, fontsize=11.5, color=FG, pad=2)
    a.text(cx, cy + r * 1.36, sub.format(n=int(sel.sum()), km=round(2 * rad_deg * 111)), family=MONO, fontsize=10, color=MUT, ha='center', va='top')
    return int(sel.sum())
nk = inset([0.02, 0.075, 0.22, 0.20], -5.5, 56.15, 0.22, 'KILMARTIN, ARGYLL', '{n} rocks, {km} km across')
ng = inset([0.25, 0.075, 0.22, 0.20], -8.62, 42.42, 0.30, 'PONTEVEDRA, GALICIA', '{n} rocks, {km} km across')

# ---------- bottom right: coast "carvings" ----------
fig.text(0.50, 0.287, 'DISTANCE TO THE SEA, AS A CARVING', family=MONO, fontsize=11, color=FG)
fig.text(0.50, 0.270, 'Centre is the coast. Rings run outwards: 0 to 2, 2 to 5, 5 to 10,\n10 to 20, 20 to 40 and 40 to 80 km from the sea. Dark pecks: share\nof carved rocks in that band. Blue arc: share of random land.\nFigures: share within 5 km of the sea, rocks v random land.',
         family=MONO, fontsize=9, color=MUT, va='top', linespacing=1.4)
regions = [('Ireland', 'IRELAND'), ('Scotland', 'SCOTLAND'), ('Galicia', 'GALICIA'), ('England', 'ENGLAND')]
for i, (rk, lab) in enumerate(regions):
    c = D['coast'][rk]
    a = fig.add_axes([0.50 + i * 0.122, 0.085, 0.115, 0.15]); a.set_aspect('equal'); a.axis('off'); a.set_facecolor(BG)
    a.set_xlim(-1.08, 1.08); a.set_ylim(-1.08, 1.08)
    a.scatter([0], [0], s=60, c=COL['ring'], lw=0, zorder=5)
    for b in range(6):
        rr = 0.24 + b * 0.15
        share = c['hist'][b] / 100; rshare = c['hist_random'][b] / 100
        th_all = np.linspace(0, 2 * np.pi, 400)
        a.plot(rr * np.cos(th_all), rr * np.sin(th_all), color=RULE, lw=.6, zorder=1)
        npk = max(1, int(round(share * 2 * np.pi * rr / 0.035)))
        th = np.pi / 2 - np.linspace(0, share * 2 * np.pi, npk)
        if share > 0:
            a.scatter(rr * np.cos(th), rr * np.sin(th), s=5, c='#2A2622', lw=0, zorder=3)
        if rshare > 0:
            th2 = np.pi / 2 - np.linspace(0, rshare * 2 * np.pi, 200)
            a.plot((rr - .055) * np.cos(th2), (rr - .055) * np.sin(th2), color=COL['rock'], lw=1.1, zorder=2)
    a.text(0, -1.12, f"{lab}\n{c['within5']:.0f}% v {c['within5_random']:.0f}%", family=MONO, fontsize=10.5, color=FG, ha='center', va='top', linespacing=1.3)

fig.text(0.04, 0.010,
         'Data: Historic Environment Scotland, Canmore; National Monuments Service rock-art layer (Ireland, data.gov.ie); Wikidata; OpenStreetMap\n'
         '(© OpenStreetMap contributors, ODbL); Natural Earth 1:10m coastline. Published counts: Scotland\'s Rock Art Project; Rodríguez Rellán et al. 2018.\n'
         'Analysis and chart: Tristan Hotham, with Python and matplotlib. Survey effort is uneven, so densities are minimums.',
         family=MONO, fontsize=9, color=MUT, linespacing=1.45)
fig.savefig(os.path.join(HERE, 'rings_in_the_rock.png'), facecolor=BG, dpi=200)
print('ok', nk, ng)
