#!/usr/bin/env python3
import csv, math
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[2]
INP=ROOT/'Maple/data/per_capita_production_v3_weekly.csv'
OUT=ROOT/'Maple/figures/per_capita_production_v3_canonical.png'
OUT.parent.mkdir(parents=True,exist_ok=True)

# Bundle licensed fonts so Windows and Linux produce the same typography.
FONTS=ROOT/'Maple/assets/fonts'
for p in FONTS.glob('*.ttf'):
    font_manager.fontManager.addfont(str(p))
regular=font_manager.FontProperties(fname=str(FONTS/'NotoSansKR-Regular.ttf'))
bold=font_manager.FontProperties(fname=str(FONTS/'NotoSansKR-Bold.ttf'))
title_font=font_manager.FontProperties(fname=str(FONTS/'Jua-Regular.ttf'))
plt.rcParams['font.family']=[regular.get_name()]
plt.rcParams['axes.unicode_minus']=False

with INP.open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
def dt(s): return datetime.strptime(s,'%Y-%m-%d')
def fl(x):
    try:return float(x)
    except:return math.nan

dates=[dt(r['date']) for r in rows]
P=[fl(r['P_total_newage100']) for r in rows]
Q=[fl(r['Q_index_sep2025_100_v3']) for r in rows]
# Hide per-capita line before DREAMER as requested.
Q=[(v if d>=dt('2023-12-21') else math.nan) for d,v in zip(dates,Q)]
# Canonical identification failure stays a true gap (do not plot interpolation).
for i,r in enumerate(rows):
    if r['identification_failed'].lower()=='true': Q[i]=math.nan
# Normalize total production to Sep-2025 mean=100, then visual separation x2.5.
sepP=[p for d,p in zip(dates,P) if d.year==2025 and d.month==9]
pden=sum(sepP)/len(sepP)
Pidx=[100*p/pden for p in P]
Pred=[2.5*x for x in Pidx]

fig=plt.figure(figsize=(16,9),dpi=160,facecolor='#bfeeee')
# Decorative NOW-like frame.
outer=FancyBboxPatch((.018,.035),.964,.91,boxstyle='round,pad=0.012,rounding_size=.022',transform=fig.transFigure,facecolor='#19b9e7',edgecolor='#102838',linewidth=2.2,zorder=-10)
mid=FancyBboxPatch((.028,.048),.944,.882,boxstyle='round,pad=0.008,rounding_size=.013',transform=fig.transFigure,facecolor='#ffd21a',edgecolor='#102838',linewidth=2.0,zorder=-9)
inner=FancyBboxPatch((.038,.060),.924,.852,boxstyle='round,pad=0.004,rounding_size=.005',transform=fig.transFigure,facecolor='#ffffff',edgecolor='#102838',linewidth=1.5,zorder=-8)
for p in (outer,mid,inner):fig.add_artist(p)
ax=fig.add_axes([.073,.20,.875,.43],facecolor='white')
start=next(d for d,p,q in zip(dates,Pred,Q) if math.isfinite(p) or math.isfinite(q))
end=dates[-1]+timedelta(days=14)

# Challenger season bands.
bands=[('챌린저스 시즌 1','2024-12-19','2025-05-22','#d8edff','#2677b9'),('챌린저스 시즌 2','2025-06-19','2025-11-20','#fff0c9','#c77c00'),('챌린저스 시즌 3','2025-12-18','2026-04-16','#f2ddfa','#8d45a8'),('챌린저스 시즌 4','2026-06-18','2026-09-17','#ddf6e6','#24805b')]
for name,a,b,fc,tc in bands:
    a,b=dt(a),dt(b); ax.axvspan(a,b,color=fc,alpha=.48,lw=0,zorder=0)
    # Dedicated season strip below the axis: event dashes never cross its text.
    left,right=max(a,start),min(b,end)
    if left < right:
        ax.text(left+(right-left)/2,-.105,name.replace(' 시즌 ','\n시즌 '),transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=10,fontproperties=bold,color=tc,linespacing=1.3,clip_on=False)

red='#ef3e43'; blue='#0874cc'
ax.plot(dates,Pred,color=red,lw=2.7,label='총 메소 생산량 ×2.5',zorder=3)
ax.plot(dates,Q,color=blue,lw=2.9,label='1인당 메소 생산량',zorder=4)
ax.axhline(100,color='#9fb1bd',lw=1,ls=(0,(4,4)),alpha=.65,zorder=1)

# Patch/event markers. Exact dates from canonical project layer.
events=[('NEW AGE','2023-06-15','#147ee8'),('DREAMER','2023-12-21','#147ee8'),('MILESTONE','2024-06-20','#147ee8'),('아즈모스 도입','2024-10-17','#2aa2a0'),('NEXT','2024-12-19','#147ee8'),('결정석 조정','2025-04-17','#ef4d55'),('ASSEMBLE','2025-06-19','#e49a12'),('결정석 조정','2025-10-23','#ef4d55'),('CROWN','2025-12-18','#147ee8'),('아즈모스 삭제','2026-01-15','#2aa2a0'),('OVERDRIVE 1차','2026-06-18','#9851bd'),('OVERDRIVE 2차','2026-07-23','#9851bd'),('OVERDRIVE 3차','2026-08-20','#9851bd')]
levels=[1.16,1.16,1.16,1.025,1.16,1.025,1.16,1.025,1.16,1.025,1.025,1.025,1.025]
for (lab,ds,c),lev in zip(events,levels):
    x=dt(ds)
    if x < start:
        # DREAMER is one week before the first sample; retain its date in the header.
        if lab != 'DREAMER': continue
        x=start
    if x > end: continue
    if dt(ds)>=start:
        ax.axvline(x,color=c,lw=1.0,ls=(0,(5,5)),alpha=.60,zorder=1)
    label=lab+'\n'+dt(ds).strftime('%y.%m.%d')
    if lab.startswith('OVERDRIVE'):
        label=lab.split()[-1]
    ax.text(x,lev,label,transform=ax.get_xaxis_transform(),ha='left' if lab=='DREAMER' else 'center',va='bottom',fontsize=10,fontproperties=bold,color=c,linespacing=1.5,clip_on=False)
ax.text(dt('2026-07-20'),1.16,'OVERDRIVE',transform=ax.get_xaxis_transform(),ha='center',va='bottom',fontsize=10,fontproperties=bold,color='#9851bd')

ax.grid(True,color='#dce7ec',lw=.8,alpha=.8)
ax.spines[['top','right']].set_visible(False)
ax.spines[['left','bottom']].set_color('#7893a3')
ax.tick_params(colors='#294556',labelsize=10)
ax.set_xlim(start,end)
ymax=max(max(x for x in Pred if math.isfinite(x)),max(x for x in Q if math.isfinite(x)))
ax.set_ylim(0,math.ceil((ymax*1.08)/50)*50)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%y.%m'))

# Title with Maple-like outlined treatment; no subtitle/V3 text.
t=fig.text(.052,.84,'1인당 메소 생산량',fontsize=48,fontproperties=title_font,color='#ffda27',ha='left',va='center')
t.set_path_effects([pe.Stroke(linewidth=9,foreground='#123b35'),pe.Normal()])
# Legend in clean top-right area.
handles,labels=ax.get_legend_handles_labels()
fig.legend(handles,labels,loc='upper right',bbox_to_anchor=(.948,.883),ncol=2,frameon=False,prop=font_manager.FontProperties(fname=bold.get_file(),size=11),handlelength=2.0,columnspacing=2.2)
fig.text(.075,.085,'2025년 9월 평균 = 100',fontsize=11,fontweight='bold',color='#294556')
fig.text(.075,.063,'※ 총 메소 생산량은 시각적 분리를 위해 ×2.5',fontsize=8.7,color='#718895')

# Endpoint labels use actual plotted data.
last=next(i for i in range(len(rows)-1,-1,-1) if math.isfinite(Q[i]))
ax.scatter(dates[last],Q[last],s=28,color=blue,zorder=6)
ax.annotate(f'{Q[last]:.1f}',(dates[last],Q[last]),xytext=(-8,-16),textcoords='offset points',ha='right',color=blue,fontweight='bold',fontsize=10)
ax.scatter(dates[-1],Pred[-1],s=28,color=red,zorder=6)
ax.annotate(f'{Pred[-1]:.1f}',(dates[-1],Pred[-1]),xytext=(-4,38),textcoords='offset points',ha='right',color=red,fontproperties=bold,fontsize=11,arrowprops=dict(arrowstyle='-',color=red,lw=.7))

plt.savefig(OUT,dpi=160,facecolor=fig.get_facecolor(),bbox_inches=None)
print(OUT)
