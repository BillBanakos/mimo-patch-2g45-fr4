import os, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
MM = 1/25.4
L, W, y0, wf, g = 28.0, 37.23, 8.5, 3.06, 1.0
BX, BY, dx, yc = 160., 100., 40., 10.
OX, OY = 105., 205.          # page position of board centre (mm)
fig = plt.figure(figsize=(210*MM, 297*MM)); ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 210); ax.set_ylim(0, 297); ax.set_aspect('equal'); ax.axis('off')
P = lambda x, y: (OX+x, OY+y)
lw = 0.25  # pt  (~0.09 mm cut line)
ax.add_patch(Rectangle(P(-BX/2, -BY/2), BX, BY, fill=False, lw=lw, ec='k'))
for (sx, sy) in [(-1,-1),(-1,1),(1,-1),(1,1)]:   # crop marks
    x, y = P(sx*BX/2, sy*BY/2)
    ax.plot([x+sx*2, x+sx*8], [y, y], 'k', lw=lw); ax.plot([x, x], [y+sy*2, y+sy*8], 'k', lw=lw)
for s, name in [(-1, 'ANT 1 / PORT 1'), (1, 'ANT 2 / PORT 2')]:
    xc = s*dx; yb, yt = yc-L/2, yc+L/2; xl, xr = xc-W/2, xc+W/2
    pts = [(xc-wf/2,-BY/2),(xc-wf/2,yb+y0),(xc-wf/2-g,yb+y0),(xc-wf/2-g,yb),(xl,yb),(xl,yt),(xr,yt),
           (xr,yb),(xc+wf/2+g,yb),(xc+wf/2+g,yb+y0),(xc+wf/2,yb+y0),(xc+wf/2,-BY/2)]
    ax.add_patch(Polygon([P(*p) for p in pts], closed=False, fc='#e8a87c', ec='k', lw=lw))
    ax.plot(*zip(P(xc-wf/2,-BY/2), P(xc+wf/2,-BY/2)), color='#e8a87c', lw=1)  # open end at edge
    ax.text(*P(xc, yt+3), name, ha='center', fontsize=7, weight='bold')
    ax.text(*P(xc, -BY/2-4), f'SMA {s>0 and 2 or 1}\nx = {BX/2+xc:.1f} mm from left edge', ha='center', va='top', fontsize=6)
    ax.annotate('', P(xl, yt+7), P(xr, yt+7), arrowprops=dict(arrowstyle='<->', lw=.4))
    ax.text(*P(xc, yt+8), f'W = {W:.2f}', ha='center', fontsize=6)
    xa = xr+4 if s > 0 else xl-4
    ax.annotate('', P(xa, yb), P(xa, yt), arrowprops=dict(arrowstyle='<->', lw=.4))
    ax.text(*P(xa+(2 if s>0 else -2), yc), f'L = {L:.2f}', rotation=90, va='center', ha='center', fontsize=6)
ax.text(*P(-dx, -26), f'feed w = {wf:.2f}\ninset y0 = {y0:.2f}\nnotch gap g = {g:.2f}/side\n(notch width {wf+2*g:.2f})',
        ha='left', fontsize=5.5, transform=ax.transData, x=P(-dx+4,0)[0]) if False else None
ax.text(*P(-dx+3.5, -30), f'line w = {wf:.2f}\ninset y0 = {y0:.2f}\ngap g = {g:.2f} each side', fontsize=5.5, va='center')
ax.text(*P(dx+3.5, -30), f'line w = {wf:.2f}\ninset y0 = {y0:.2f}\ngap g = {g:.2f} each side', fontsize=5.5, va='center')
ax.text(105, 288, '2.45 GHz 1x2 MIMO inset-fed patch  -  TOP COPPER, 1:1 cutting template', ha='center', fontsize=10, weight='bold')
ax.text(105, 282, 'FR-4 1.6 mm, board 160 x 100 mm. Bottom side = full copper ground. All dims in mm. Cut on the CENTRE of the black lines.',
        ha='center', fontsize=7)
# scale check bars
for y0b, ln in [(130, 100.0), (122, 50.0)]:
    ax.plot([30, 30+ln], [y0b, y0b], 'k', lw=0.6)
    for t in range(0, int(ln)+1, 10): ax.plot([30+t]*2, [y0b, y0b+(2.5 if t % 50 == 0 else 1.5)], 'k', lw=0.4)
    ax.text(30+ln+3, y0b, f'= exactly {ln:.0f} mm  (measure it!)', va='center', fontsize=7)
ax.add_patch(Rectangle((150, 115), 40, 20, fill=False, lw=0.6)); ax.text(170, 125, '40 x 20 mm\ncheck box', ha='center', va='center', fontsize=7)
notes = [
 'PRINT: Adobe/any viewer -> "Actual size" / scale 100 %. NOT "fit to page". Verify both bars and the box with a ruler (+-0.3 mm) before cutting.',
 'Simulated (openEMS FDTD, er 4.4, tan d 0.02): f_res 2.444 GHz, S11 -35 dB, -10 dB BW 2.410-2.476 GHz,',
 '   S21 <= -30 dB across 2.400-2.4835 GHz, ECC 0.016 (far-field), gain 3.4 dBi/port (rad. eff. ~38 %).',
 'SENSITIVITY: L sets frequency: about -75 MHz per +1 mm. Inset y0 sets match (8.5 opt.; 9.0 still < -25 dB). W, g are uncritical.',
 'PROCEDURE: 1) Ground: cover bottom fully; lay strips along the 100 mm direction (parallel to the feed lines), overlap 3-5 mm',
 '   and solder every seam along its full length (tape adhesive is usually NOT conductive). Wrap/solder 2-3 mm onto the bottom edge',
 '   at each SMA position for the SMA ground legs.  2) Top: one piece of 50 mm tape per element, from the bottom edge up past the patch',
 '   (~75 mm long) so patch + line are ONE seamless piece.  3) Tape this sheet over the board aligned to the crop marks, cut with a',
 '   fresh blade and steel rule through paper + copper, peel the excess.  4) Edge-mount SMA: centre pin on line end, legs to ground,',
 '   keep the solder fillet small.  TUNING: FR-4 er varies 4.2-4.7. Trimming the top (radiating) edge shortens L and only RAISES f,',
 '   so if unsure of your FR-4, cut the top edge at L = 28.3 (~2.42 GHz), measure S11 on a VNA, then trim toward 28.0.',
]
for k, t in enumerate(notes): ax.text(14, 105-k*4.6, t, fontsize=6.3, family='DejaVu Sans')
ax.text(14, 46, 'Port numbering: viewed from copper (top) side, feed edge at bottom.', fontsize=6.3, style='italic')
HERE = os.path.dirname(os.path.abspath(__file__))
fig.savefig(os.path.join(HERE, 'MIMO_patch_2G45_template_A4_1to1.pdf'))
fig.savefig(os.path.join(HERE, '..', 'docs', 'template_preview.png'), dpi=110)
