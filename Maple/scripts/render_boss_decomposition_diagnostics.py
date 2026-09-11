"""Research figure; deliberately separate from the user's canonical NOW chart."""
import csv,json
from datetime import date
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'Maple/data/boss_decomposition_joint_v1'
with (DATA/'weekly_decomposition.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
with (DATA/'share_profile.csv').open(encoding='utf-8') as f:profiles=list(csv.DictReader(f))
fp=ROOT/'Maple/assets/fonts/NotoSansKR-Regular.ttf'
font_manager.fontManager.addfont(str(fp));plt.rcParams['font.family']=font_manager.FontProperties(fname=str(fp)).get_name()
plt.rcParams['axes.unicode_minus']=False
dates=[date.fromisoformat(r['date']) for r in rows]
def array(k):return np.array([float(r[k]) if r[k] else np.nan for r in rows])
fig,axes=plt.subplots(2,2,figsize=(16,10),dpi=160)
fig.subplots_adjust(left=.07,right=.97,top=.87,bottom=.11,hspace=.45,wspace=.26)
fig.suptitle('보스 생산 공동분해 · 조건부 추정과 식별 검사',fontsize=21,y=.96)
fig.text(.5,.91,'분석 종점 2026.08.21 · 마지막 공동 관측 08.20 · 단위는 상대지수',ha='center',color='#586477')
ax=axes[0,0];ax.plot(dates,array('B_observed'),color='#222222',label='기존 보스 생산')
ax.plot(dates,array('B_fitted'),color='#e39728',ls='--',label='모형 적합 총량')
ax.set_title('① 총량 적합');ax.set_ylabel('NEW AGE 총생산=100 기준');ax.legend(fontsize=9)
ax=axes[0,1]
base=np.nanmean([float(r['bM_reconciled_per_100k']) for r in rows if r['date'].startswith('2025-09') and r['bM_reconciled_per_100k']])
ax.plot(dates,array('bM_reconciled_per_100k')/base*100,color='#1277ba',label='본섭 평균')
ax.plot(dates,array('bC_reconciled_per_100k')/base*100,color='#934aa8',label='챌린저스 평균')
ax.set_title('② 같은 기준으로 비교한 계정당 생산량');ax.set_ylabel('2025.09 본섭 평균=100');ax.legend(fontsize=9)
ax=axes[1,0];ax.fill_between(dates,array('conditional_laplace_p05')*100,array('conditional_laplace_p95')*100,
                           color='#dcd7ee',label='조건부 90% Laplace 범위')
ax.fill_between(dates,array('scenario_min')*100,array('scenario_max')*100,color='#ae9bcf',alpha=.8,label='계산한 시나리오의 중심값 범위')
ax.plot(dates,array('challenger_share')*100,color='#76419e',label='선택 모형의 중심값');ax.set_ylim(0,100)
ax.set_title('③ 챌린저스의 전체 보스 생산 기여율');ax.set_ylabel('%');ax.legend(fontsize=8,loc='upper left')
ax=axes[1,1]
for ds,col in [('2026-03-26','#1277ba'),('2026-08-20','#934aa8')]:
    pp=[r for r in profiles if r['date']==ds]
    ax.plot([100*float(r['target_share']) for r in pp],[100*float(r['log_rmse']) for r in pp],marker='o',color=col,label=ds)
ax.set_title('④ 기여율을 바꿔도 총량은 비슷하게 맞는가?');ax.set_xlabel('해당 날짜에 고정한 챌린저스 기여율 (%)')
ax.set_ylabel('전체 적합 로그 RMSE ×100');ax.legend(fontsize=9)
for i,ax in enumerate(axes.flat):
    ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
    if i<3:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6));ax.xaxis.set_major_formatter(mdates.DateFormatter('%y.%m'))
fig.text(.07,.035,'중심값은 확정 분해가 아닙니다. ④의 평평한 곡선은 서로 다른 배분이 같은 총량과 양립함을 뜻합니다.',fontsize=11,color='#643a49')
output=ROOT/'Maple/figures/boss_decomposition_joint_v1_diagnostics.png';fig.savefig(output);print(output)
