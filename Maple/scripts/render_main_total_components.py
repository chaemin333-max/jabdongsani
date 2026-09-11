from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
R=Path(__file__).resolve().parents[1]
font_manager.fontManager.addfont(str(R/'assets/fonts/NotoSansKR-Regular.ttf'))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False,'font.size':11})
D=R/'data/main_total_components_20260912'
s=pd.read_csv(D/'residual_allocation_scenarios.csv',parse_dates=['date'])
d=pd.read_csv(D/'weekly_components.csv',parse_dates=['date'])
fig,ax=plt.subplots(2,1,figsize=(13,8),sharex=True,layout='constrained')
for ratio,g in s.groupby('residual_C_to_M_productivity_assumed'):
    ax[0].plot(g.date,g.q_main*100000,label=f'잔액 생산성 비율 {ratio:g}')
    ax[1].plot(g.date,g.q_main_sep2025_100)
ax[0].fill_between(d.date,d.q_main_lower_fixed_boss*100000,d.q_main_upper_fixed_boss*100000,color='gray',alpha=.15,label='잔액 배분만의 허용 범위')
ax[0].set_ylabel('본섭 10만 계정당 총생산\nNEW AGE 총생산 단위')
ax[0].legend(ncol=2,fontsize=9)
ax[1].set_ylabel('각 시나리오의 2025년 9월 = 100')
for a in ax:a.grid(alpha=.2)
fig.suptitle('본섭 1인당 총 메소 생산량 · 잔액 배분 시나리오',fontsize=18)
fig.supxlabel('잔액 = 총생산 − 주간 보스 (월간 보스 포함) · 음영은 전체 모형 신뢰구간이 아님',fontsize=10)
fig.savefig(R/'figures/main_total_components_20260912.png',dpi=160)
