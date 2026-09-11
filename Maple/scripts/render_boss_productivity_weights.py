"""Render conditional weekly boss productivity and weights."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[1]
font_manager.fontManager.addfont(str(ROOT/'assets/fonts/NotoSansKR-Regular.ttf'))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False,'font.size':11})
d=pd.read_csv(ROOT/'data/boss_productivity_weights_20260912/weekly_weights.csv',parse_dates=['date'])
fig,axes=plt.subplots(2,1,figsize=(14,8),sharex=True,layout='constrained')
axes[0].plot(d.date,d.main_productivity_index,color='#2166ac',label='본섭 계정당 생산량')
axes[0].plot(d.date,d.challenger_productivity_index,color='#d6604d',label='챌린저스 계정당 생산량')
axes[0].set_ylabel('본섭 2025년 9월 평균 = 100')
axes[0].legend(loc='upper left')
for season,color in zip(range(1,5),['#1b9e77','#d95f02','#7570b3','#e7298a']):
    x=d[d.season==season]
    axes[1].plot(x.date,x.w,color=color,label=f'시즌 {season}')
    axes[1].fill_between(x.date,x.w_scenario_min,x.w_scenario_max,color=color,alpha=.16)
axes[1].set_ylabel('챌린저스 / 본섭 생산성 비율 w')
axes[1].legend(ncol=4,loc='upper left')
axes[1].set_ylim(bottom=0)
for ax in axes:ax.grid(alpha=.18)
fig.suptitle('주간 보스 생산성 · 신규 보스 보상 반영 후 조건부 분해',fontsize=19)
fig.supxlabel('음영: 가정별 시나리오 범위(신뢰구간 아님) · 마지막 관측 2026-08-20',fontsize=10)
fig.savefig(ROOT/'figures/boss_productivity_weights_20260912.png',dpi=160)
