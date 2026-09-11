import csv
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'Maple/data/per_capita_production_v3_weekly.csv'
OUT=ROOT/'Maple/figures/per_capita_production_v3_canonical.png'
OUT.parent.mkdir(parents=True, exist_ok=True)

# Prefer a Korean Noto family installed by the workflow.
candidates=['Noto Sans CJK KR','Noto Sans KR','Noto Sans CJK JP','DejaVu Sans']
installed={f.name for f in font_manager.fontManager.ttflist}
FONT=next((x for x in candidates if x in installed),'DejaVu Sans')
plt.rcParams['font.family']=FONT
plt.rcParams['axes.unicode_minus']=False

rows=[]
with SRC.open(encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        d=datetime.strptime(r['date'],'%Y-%m-%d')
        p=float(r['P_total_newage100'])
        q=float(r['Q_raw_plot_v3'])
        rows.append((d,p,q))

# Canonical normalization requested by user: mean of September 2025 = 100 for BOTH series.
sep=[x for x in rows if x[0].year==2025 and x[0].month==9]
p_den=sum(x[1] for x in sep)/len(sep)
q_den=sum(x[2] for x in sep)/len(sep)
dates=[x[0] for x in rows]
p_idx=[100*x[1]/p_den for x in rows]
q_idx=[100*x[2]/q_den for x in rows]

# Reference-style event layer.
events=[
('NEW AGE','23.06.15','2023-06-15','#1976d2'),
('DREAMER','23.12.21','2023-12-21','#1976d2'),
('MILESTONE','24.06.20','2024-06-20','#1976d2'),
('아즈모스 도입','24.10.17','2024-10-17','#319a98'),
('NEXT','24.12.19','2024-12-19','#1976d2'),
('결정석 조정','25.04.17','2025-04-17','#ef5350'),
('ASSEMBLE','25.06.19','2025-06-19','#d28a00'),
('결정석 조정','25.10.23','2025-10-23','#ef5350'),
('CROWN','25.12.18','2025-12-18','#1976d2'),
('아즈모스 삭제','26.01.15','2026-01-15','#319a98'),
('OVERDRIVE 1차','26.06.18','2026-06-18','#8e44ad'),
('OVERDRIVE 2차','26.07.23','2026-07-23','#8e44ad'),
('OVERDRIVE 3차','26.08.20','2026-08-20','#8e44ad'),
]

fig=plt.figure(figsize=(19.2,10.8),dpi=150,facecolor='#bfeceb')
# Main rounded window, reference-inspired but single-color outer background.
outer=FancyBboxPatch((0.025,0.055),0.95,0.87,boxstyle='round,pad=0.012,rounding_size=0.022',transform=fig.transFigure,fc='#12b8e8',ec='#0c2631',lw=2.2,zorder=0)
fig.add_artist(outer)
yellow=FancyBboxPatch((0.034,0.067),0.932,0.835,boxstyle='round,pad=0.008,rounding_size=0.010',transform=fig.transFigure,fc='#ffd31a',ec='#172b34',lw=2.0,zorder=0.1)
fig.add_artist(yellow)
panel=FancyBboxPatch((0.041,0.076),0.918,0.815,boxstyle='round,pad=0.006,rounding_size=0.006',transform=fig.transFigure,fc='white',ec='#263238',lw=1.6,zorder=0.2)
fig.add_artist(panel)

ax=fig.add_axes([0.075,0.17,0.85,0.56],zorder=2)
ax.set_facecolor('white')
ax.plot(dates,p_idx,lw=3.1,color='#ef3d43',label='총 메소 생산량')
ax.plot(dates,q_idx,lw=3.1,color='#0874d1',label='1인당 메소 생산량 (V3)')
ax.axhline(100,color='#9aa7ad',lw=1.0,ls=(0,(4,4)),alpha=.65)

# x range includes historical event labels from NEW AGE, matching reference layout.
ax.set_xlim(datetime(2023,1,1),datetime(2026,9,15))
ymax=max(max(p_idx),max(q_idx))*1.13
ax.set_ylim(0,ymax)
ax.grid(True,color='#dfe9ed',lw=.8,alpha=.85)
ax.spines[['top','right']].set_visible(False)
ax.spines[['left','bottom']].set_color('#78909c')
ax.tick_params(colors='#34495e',labelsize=11)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,4,7,10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%y.%m'))

# Title: Korean Noto with deliberate stroke, avoiding image-model glyph artifacts.
title=fig.text(.064,.828,'1인당 메소 생산량',fontsize=42,fontweight='bold',color='#ffd21a',ha='left',va='center',zorder=4)
title.set_path_effects([pe.Stroke(linewidth=7,foreground='#15333b'),pe.Normal()])
fig.text(.065,.785,'본섭 평균 계정 생산능력으로 보정한 유효 생산계정당 메소 생산량 · V3',fontsize=15.5,fontweight='bold',color='#213b4a',ha='left',zorder=4)

leg=ax.legend(loc='upper right',bbox_to_anchor=(1.0,1.48),ncol=2,frameon=False,fontsize=14,handlelength=2.4,columnspacing=2.5)
for t in leg.get_texts(): t.set_fontweight('bold')

# Event lines and labels above the axes.
for i,(name,ds,dstr,c) in enumerate(events):
    x=datetime.strptime(dstr,'%Y-%m-%d')
    ax.axvline(x,color=c,lw=1.25,ls=(0,(5,5)),alpha=.72)
    # Alternate label heights only where dense, preserving readability.
    y=1.145 if i not in (5,7,9) else 1.06
    ax.text(x,y,name+'\n'+ds,transform=ax.get_xaxis_transform(),ha='center',va='bottom',fontsize=10.2,fontweight='bold',color=c,clip_on=False)

# Accurate endpoint labels from the actual arrays.
ax.scatter([dates[-1]],[p_idx[-1]],s=35,color='#ef3d43',zorder=5)
ax.scatter([dates[-1]],[q_idx[-1]],s=35,color='#0874d1',zorder=5)
ax.annotate(f'{p_idx[-1]:.1f}',(dates[-1],p_idx[-1]),xytext=(-10,18),textcoords='offset points',ha='right',fontsize=13,fontweight='bold',color='#ef3d43')
ax.annotate(f'{q_idx[-1]:.1f}',(dates[-1],q_idx[-1]),xytext=(-10,-24),textcoords='offset points',ha='right',fontsize=13,fontweight='bold',color='#0874d1')

fig.text(.075,.105,'2025년 9월 평균 = 100',fontsize=13.5,fontweight='bold',color='#294957')
fig.text(.925,.105,'※ V3 productive-equivalent exposure 보정',fontsize=11.5,fontweight='bold',color='#78909c',ha='right')
fig.text(.925,.082,'데이터: Maple/data/per_capita_production_v3_weekly.csv',fontsize=9.5,color='#78909c',ha='right')

fig.savefig(OUT,facecolor=fig.get_facecolor(),bbox_inches=None)
print('saved',OUT)
print('P Sep25 denominator',p_den,'Q Sep25 denominator',q_den)
print('endpoint P index',p_idx[-1],'V3 index',q_idx[-1])
