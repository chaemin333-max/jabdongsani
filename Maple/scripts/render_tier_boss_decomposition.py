"""Render tier-aware results without modifying the user's canonical graph."""
import csv
from datetime import date
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parents[2]
with (ROOT/'Maple/data/tier_boss_decomposition_v1/weekly_decomposition.csv').open(encoding='utf-8') as f:r=list(csv.DictReader(f))
font=ROOT/'Maple/assets/fonts/NotoSansKR-Regular.ttf';font_manager.fontManager.addfont(str(font));plt.rcParams['font.family']=font_manager.FontProperties(fname=str(font)).get_name();plt.rcParams['axes.unicode_minus']=False
ds=[date.fromisoformat(x['date']) for x in r]
def a(k):return np.array([float(x[k]) if x[k]!='' else np.nan for x in r])
fig,axes=plt.subplots(3,1,figsize=(15,12),dpi=160);fig.subplots_adjust(left=.08,right=.97,top=.89,bottom=.09,hspace=.4)
fig.suptitle('구간별 보스 생산 분해 · 카이·메이린은 하드 세렌 이하',fontsize=20,y=.96)
fig.text(.5,.92,'리프 전 본섭 하위 생산 일정 + 시즌별 챌섭 상한 가정 · 2026.08.20까지',ha='center',color='#526773')
ax=axes[0];ax.plot(ds,a('B_total'),color='#999',label='전체 주간 보스 생산');ax.plot(ds,a('M_boss'),color='#1477b5',label='본섭 생산');ax.plot(ds,a('C_boss'),color='#9b4cad',label='챌린저스 생산');ax.set_ylabel('기존 정본의 상대지수');ax.set_title('구간별 생산량을 보존한 배분');ax.legend(ncol=3,fontsize=10)
ax=axes[1];ax.fill_between(ds,a('scenario_share_min')*100,a('scenario_share_max')*100,color='#d7c6df',label='계산한 이동·본섭 변화 시나리오 범위')
ax.plot(ds,a('C_share')*100,color='#9b4cad',label='기준 시나리오');ax.set_ylabel('챌린저스 기여율 (%)');ax.set_title('같은 가정 아래의 기여율과 시나리오 비교');ax.legend(fontsize=9);ax.set_ylim(0,70)
ax=axes[2];base=np.mean([float(x['M_mean_per_100k']) for x in r if x['date'].startswith('2025-09') and x['M_mean_per_100k']])
ax.plot(ds,a('M_mean_per_100k')/base*100,color='#1477b5',label='본섭 평균');ax.plot(ds,a('C_mean_per_100k')/base*100,color='#9b4cad',label='챌린저스 평균');ax.set_ylabel('2025.09 본섭 평균=100');ax.set_title('동일 기준으로 비교한 계정당 보스 생산');ax.legend(fontsize=10)
for ax in axes:
    for start,end in [('2024-12-19','2025-01-16'),('2025-06-19','2025-07-17'),('2025-12-18','2026-01-15'),('2026-06-18','2026-07-23')]:ax.axvspan(date.fromisoformat(start),date.fromisoformat(end),color='#e4f3ee',zorder=-1)
    ax.grid(alpha=.18);ax.spines[['top','right']].set_visible(False);ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3));ax.xaxis.set_major_formatter(mdates.DateFormatter('%y.%m'))
fig.text(.08,.025,'연한 초록 = 리프 불가 기간. 이동량은 관측 인구 감소를 이용한 시나리오이며, 음영은 통계적 신뢰구간이 아닙니다.',fontsize=10,color='#526773')
p=ROOT/'Maple/figures/tier_boss_decomposition_v1.png';fig.savefig(p);print(p)
