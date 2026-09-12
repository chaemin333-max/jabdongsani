"""NOW-like stacked panels: canonical total above, pure field production below."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager,patheffects
from matplotlib.patches import FancyBboxPatch
import matplotlib.dates as md
R=Path(__file__).resolve().parents[1]
for f in (R/'assets/fonts').glob('*.ttf'):font_manager.fontManager.addfont(str(f))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False,'font.size':11})
title=font_manager.FontProperties(fname=str(R/'assets/fonts/Jua-Regular.ttf'))
d=pd.read_csv(R/'data/field_share_reconstruction_20260912/weekly_field.csv',parse_dates=['date'])
fig=plt.figure(figsize=(16,11),dpi=160,facecolor='#bfeeee')
for box,color in [((.018,.025,.964,.945),'#19b9e7'),((.026,.036,.948,.925),'#ffd21a'),((.036,.046,.928,.905),'white')]:
    fig.add_artist(FancyBboxPatch(box[:2],box[2],box[3],boxstyle='round,pad=.004,rounding_size=.016',transform=fig.transFigure,facecolor=color,edgecolor='#14363b',linewidth=2,zorder=-10))
effect=[patheffects.withStroke(linewidth=5,foreground='#14363b')]
fig.text(.065,.90,'총 메소 생산량',fontproperties=title,fontsize=35,color='#ffda27',path_effects=effect)
fig.text(.065,.485,'순수 사냥 메소 생산량',fontproperties=title,fontsize=32,color='#ffda27',path_effects=effect)
ax1=fig.add_axes([.083,.57,.835,.285]);ax2=fig.add_axes([.083,.155,.835,.285],sharex=ax1)
for ax,col,label in [(ax1,'P_total','총 메소 생산량'),(ax2,'F_field','필드 사냥 생산량')]:
    color='#ee3548' if col=='P_total' else '#0776c7'
    ax.plot(d.date,d[col],color=color,lw=2.8,label=label,zorder=3)
    if col=='F_field':ax.fill_between(d.date,d.F_field_low,d.F_field_high,color=color,alpha=.10,lw=0)
    last=d.dropna(subset=[col]).iloc[-1]
    ax.plot(last.date,last[col],'o',color=color,ms=5)
    ax.annotate(f'{last[col]:,.1f}',(last.date,last[col]),xytext=(-12,18),textcoords='offset points',ha='right',color=color,fontweight='bold',fontsize=14)
    ax.set_ylim(bottom=0,top=d[col].max()*1.20)
    ax.grid(color='#e4e9eb',lw=.7);ax.spines[['top','right']].set_visible(False)
    for side in ['bottom','left']:ax.spines[side].set_color('#a1b1b7')
    for season,start,end,color in [(2,'2025-06-19','2025-11-20','#fff1cf'),(3,'2025-12-18','2026-04-16','#efdef5'),(4,'2026-06-18','2026-08-20','#dff1e6')]:
        a,b=pd.Timestamp(start),pd.Timestamp(end)
        ax.axvspan(a,b,color=color,alpha=.4,zorder=0)
        if ax==ax2:ax.text(a+(b-a)/2,-.12,f'챌린저스\n시즌 {season}',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=10,color='#50646d')
    ax.tick_params(colors='#415560')
ax1.tick_params(labelbottom=False)
ax2.xaxis.set_major_locator(md.MonthLocator(interval=2));ax2.xaxis.set_major_formatter(md.DateFormatter('%y.%m'))
ax2.set_xlim(d.date.min(),d.date.max()+pd.Timedelta(days=7))
fig.text(.918,.905,'2026.08.20까지',ha='right',fontsize=12,color='#50646d')
fig.text(.083,.075,'공통 단위: NEW AGE 총생산 = 100',fontsize=11,color='#50646d')
fig.text(.918,.075,'사냥 = 총생산 × 필드 비율 · 옅은 띠: 판독·미분리 선 범위',ha='right',fontsize=10,color='#71858a')
fig.savefig(R/'figures/total_and_pure_field_20260912.png',dpi=180)

