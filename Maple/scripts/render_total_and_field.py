"""Render canonical total and aggregate pure field using the boss-tier layout.

This is a derived visualization, not a revision of the measured tier series.
"""
import csv
import json
from datetime import date
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Maple/data/now_20260910'
OUT = ROOT / 'Maple/figures/total_and_pure_field_20260912'

def read(path):
    with path.open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

rows = read(DATA / 'boss_tier_weekly.csv')
panel = {r['date']: r for r in read(ROOT / 'Maple/data/maple_production_calibration_inputs_weekly.csv')}
dates = [date.fromisoformat(r['date']) for r in rows]
production = np.array([float(panel[r['date']]['P_total_newage100']) * 6.495250069 for r in rows])
field_rows = {r['date']:r for r in read(ROOT/'Maple/data/field_share_reconstruction_20260912/weekly_field.csv')}
field = np.array([float(field_rows[r['date']]['F_field']) if r['date'] in field_rows and field_rows[r['date']]['F_field'] else np.nan for r in rows])
assert np.all(field[np.isfinite(field)] >= 0)
for name in ['NotoSansKR-Regular.ttf', 'NotoSansKR-Bold.ttf']:
    font_manager.fontManager.addfont(str(ROOT / 'Maple/assets/fonts' / name))
font = font_manager.FontProperties(fname=str(ROOT / 'Maple/assets/fonts/NotoSansKR-Regular.ttf')).get_name()
plt.rcParams.update({'font.family': font, 'axes.unicode_minus': False, 'svg.fonttype': 'path'})
fig = plt.figure(figsize=(20, 11.25), dpi=160, facecolor='#bfeeed')
for xy, w, h, color, rounding in [((.025,.095),.95,.81,'#05bce7',.020),
                                  ((.031,.107),.938,.772,'#ffdc32',.010),
                                  ((.037,.115),.926,.756,'white',.005)]:
    fig.add_artist(FancyBboxPatch(xy,w,h,boxstyle=f'round,pad=0.006,rounding_size={rounding}',
                                transform=fig.transFigure,fc=color,ec='#14353b',lw=2,zorder=0))
# Reuse the supplied, identical title artwork as a plot asset. This preserves
# the original glyphs, highlights and outline instead of approximating a font.
reference = plt.imread(ROOT / '총메소생산.png')
title_art = reference[220:405,125:1015]
title_width = .29
title_height = title_width * (20 / 11.25) * title_art.shape[0] / title_art.shape[1]
title_ax = fig.add_axes([.043,.765,title_width,title_height],zorder=3)
title_ax.imshow(title_art,interpolation='lanczos')
title_ax.set_axis_off()

def source_crop(box, image=reference, coordinate_width=2048):
    scale = image.shape[1] / coordinate_width
    x0,y0,x1,y1 = [round(v*scale) for v in box]
    return image[y0:y1,x0:x1]

def original_label(image, xy, coords, height, align=(.5,0), offset=(0,0)):
    """Place original lettering without substituting fonts or redrawing glyphs."""
    artist = AnnotationBbox(OffsetImage(image,zoom=height/image.shape[0],interpolation='lanczos'),
                           xy,xycoords=coords,xybox=offset,boxcoords='offset points',
                           box_alignment=align,frameon=False,pad=0,annotation_clip=False)
    ax.add_artist(artist)
    return artist

ax = fig.add_axes([.078,.205,.674,.405],zorder=2)
blue = '#087bea'
red = '#fa3044'
production_line, = ax.plot(dates,production,color=red,lw=3.4,label='총 메소 생산량',zorder=6)
ax.plot(dates,field,color=blue,lw=2.6,label='사냥 메소 생산량',zorder=5)
ax.set_xlim(dates[0],date(2026,8,28))
ax.set_ylim(0,1400)
ax.set_yticks(np.arange(0,1401,200))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,4,7,10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%y.%m'))
ax.grid(color='#e3edf0',lw=.85)
ax.set_axisbelow(True)
ax.spines[['top','right']].set_visible(False)
ax.spines[['left','bottom']].set_color('#a4b8bf')
ax.tick_params(colors='#455e6b',labelsize=12,length=0,pad=12)
for tick in ax.get_xticklabels() + ax.get_yticklabels():
    tick.set_visible(False)

# Exact original tick lettering, repositioned to the cropped data window.
for ds, center in [('2024-10-01',1008),('2025-01-01',1130),('2025-04-01',1253),
                   ('2025-07-01',1376),('2025-10-01',1499),('2026-01-01',1621),
                   ('2026-04-01',1744),('2026-07-01',1867)]:
    original_label(source_crop((center-32,919,center+32,944)),
                   (mdates.date2num(date.fromisoformat(ds)),0),ax.get_xaxis_transform(),
                   13,align=(.5,1),offset=(0,-10))
for val, cy in [(0,906),(200,839),(400,771),(600,703),(800,636),(1000,568),(1200,501),(1400,433)]:
    original_label(source_crop((85,cy-13,133,cy+13)),(0,val),ax.get_yaxis_transform(),
                   13,align=(1,.5),offset=(-8,0))

events = [('2024-10-17','아즈모스 도입','24.10.17','#319c9d',1.035),
          ('2024-12-19','NEXT','24.12.19',blue,1.205),
          ('2025-04-17','결정석 조정','25.04.17','#f53749',1.035),
          ('2025-06-19','ASSEMBLE','25.06.19','#cb9206',1.205),
          ('2025-10-23','결정석 조정','25.10.23','#f53749',1.035),
          ('2025-12-18','CROWN','25.12.18',blue,1.205),
          ('2026-01-15','아즈모스 삭제','26.01.15','#319c9d',1.035)]
event_boxes = [(969,344,1090,399),(1083,282,1148,336),(1221,344,1326,399),
               (1302,282,1411,336),(1475,344,1579,399),(1563,282,1644,336),
               (1580,344,1698,399)]
for (ds,name,caption,color,y), box in zip(events,event_boxes):
    dt = date.fromisoformat(ds)
    ax.axvline(dt,color=color,lw=1.05,ls=(0,(5,5)),alpha=.7)
    original_label(source_crop(box),(mdates.date2num(dt),y),ax.get_xaxis_transform(),30)
for ds, label, box in [('2026-06-18','1차',(1830,322,1864,348)),
                       ('2026-07-23','2차',(1874,322,1909,348)),
                       ('2026-08-20','3차',(1913,322,1949,348))]:
    dt=date.fromisoformat(ds)
    ax.axvline(dt,color='#9a4dcc',lw=1.05,ls=(0,(5,5)),alpha=.7)
    original_label(source_crop(box),(mdates.date2num(dt),1.035),ax.get_xaxis_transform(),14)
original_label(source_crop((1828,252,1944,279)),(mdates.date2num(date(2026,7,18)),1.205),ax.get_xaxis_transform(),14)

# Identical frame, title artwork, axis geometry, ticks and event lettering to boss_tier_aligned.
fig.lines.append(plt.Line2D([.795,.811],[.615,.615],transform=fig.transFigure,color=red,lw=2.4))
original_label(source_crop((1476,176,1620,205)),(.819,.615),fig.transFigure,13,align=(0,.5))
fig.lines.append(plt.Line2D([.795,.811],[.580,.580],transform=fig.transFigure,color=blue,lw=2.4))
fig.text(.819,.580,'사냥 메소 생산량',ha='left',va='center',fontsize=10.5,fontproperties=font_manager.FontProperties(fname=str(ROOT/'Maple/assets/fonts/NotoSansKR-Bold.ttf')),color='#304652')
ax.scatter(dates[-1],production[-1],color=red,s=25,zorder=7)
original_label(source_crop((1855,412,1931,443)),(mdates.date2num(dates[-1]),production[-1]),ax.transData,17,align=(0,0),offset=(8,5))
ax.scatter(dates[-1],field[-1],color=blue,s=25,zorder=7)
ax.annotate(f'{field[-1]:,.1f}',(dates[-1],field[-1]),xytext=(8,5),textcoords='offset points',ha='left',va='bottom',fontsize=12,fontweight='bold',color=blue)
original_label(source_crop((146,968,356,992)),(.078,.144),fig.transFigure,13,align=(0,0))
OUT.parent.mkdir(parents=True,exist_ok=True)
for suffix in ['png','svg']:
    fig.savefig(OUT.with_suffix('.'+suffix),facecolor=fig.get_facecolor())
print(json.dumps({'png':str(OUT.with_suffix('.png')),'scope':'all main and challenger worlds in source aggregate; pure field only','endpoint':float(field[-1])},ensure_ascii=False))
