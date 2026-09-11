import csv,json
from datetime import date
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Maple/data/tier_regression_audit'
def read(name):
    with (D/name).open(encoding='utf-8') as f:return list(csv.DictReader(f))
font=ROOT/'Maple/assets/fonts/NotoSansKR-Regular.ttf';font_manager.fontManager.addfont(str(font));plt.rcParams['font.family']=font_manager.FontProperties(fname=str(font)).get_name();plt.rcParams['axes.unicode_minus']=False
fig,axes=plt.subplots(2,2,figsize=(16,11),dpi=160);fig.subplots_adjust(left=.09,right=.97,top=.86,bottom=.16,hspace=.48,wspace=.35)
fig.suptitle('보스 구간 분해 · 메타분석 / 회귀 / 공식 역대조',fontsize=21,y=.96)
fig.text(.5,.905,'개장 효과는 관측 변화의 요약 · 공식 역대조는 총량 복원 검증 · 분해 비율의 독립 검증과 구분',ha='center',color='#526773')
ax=axes[0,0];rr=read('opening_episode_effects.csv');m=json.loads((D/'episode_meta_summary.json').read_text())
vals=[float(r['increase_pct']) for r in rr]+[m['pooled_pct']];lower=[float(r['bootstrap_lower_pct']) for r in rr]+[m['ci_lower_pct']];upper=[float(r['bootstrap_upper_pct']) for r in rr]+[m['ci_upper_pct']]
ax.errorbar(vals,np.arange(5),xerr=[np.array(vals)-lower,np.array(upper)-vals],fmt='o',capsize=4,color='#176da3')
ax.set_yticks(np.arange(5),['시즌1','시즌2','시즌3','시즌4','통합 요약']);ax.invert_yaxis();ax.axvline(0,color='#999',lw=.8)
ax.set_title('① 개장 전 3주 대비 리프 전 하위 생산 증가');ax.set_xlabel('하드 진힐라 이하 생산 증가율 (%)')
ax=axes[0,1];allr=read('regression_coefficients.csv');specs=[('low2_difference_upper_control_HAC4','dlog1p_C_100k','일반 주간 변화'),('opening_local_FE_HAC2','log1p_C_100k','개장 전후'),('opening_local_FE_post_control_HAC2','log1p_C_100k','개장 전후 + 공통 변화 통제')]
for i,(model,term,label) in enumerate(specs):
 r=next(r for r in allr if r['model']==model and r['term']==term);v=float(r['coefficient']);ax.errorbar(v,i,xerr=[[v-float(r['ci_lower'])],[float(r['ci_upper'])-v]],fmt='o',capsize=4,color='#85519b')
ax.set_yticks(range(3),[x[2] for x in specs]);ax.invert_yaxis();ax.axvline(0,color='#999',lw=.8);ax.set_title('② 챌린저스 인구 변화의 회귀계수');ax.set_xlabel('계수 및 HAC 구간 · 인과효과로 해석하지 않음')
ax.text(0,-.38,'개장 회귀의 4시즌 부호검사 p=0.125',transform=ax.transAxes,fontsize=10,color='#85519b')
ax=axes[1,0];r=read('cross_broadcast_holdout.csv');ds=[date.fromisoformat(x['date']) for x in r]
ax.plot(ds,[float(x['old_official_scaled']) for x in r],label='2025.10 방송 복원',color='#176da3');ax.plot(ds,[float(x['new_official_raw']) for x in r],label='2026.09 방송 복원',color='#e17b2e',ls='--')
ax.axvspan(ds[0],ds[15],color='#e6ecef',label='눈금 교정 16주');ax.set_title('③ 이후 43주 역대조: MAPE 2.35%, R² 0.991');ax.set_ylabel('동일 눈금의 상대 생산량');ax.legend(fontsize=8)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3));ax.xaxis.set_major_formatter(mdates.DateFormatter('%y.%m'))
ax=axes[1,1];r=read('official_constraint_audit.csv');raw=[float(x['reconstructed_raw_multiplier'])/float(x['official_multiplier']) if x['reconstructed_raw_multiplier'] else np.nan for x in r]
ax.plot(range(1,7),raw,'o-',label='원시 픽셀',color='#e17b2e');ax.plot(range(1,7),np.ones(6),'s--',label='공식 배율로 보정한 값',color='#176da3');ax.set_ylim(.3,1.25);ax.set_xticks(range(1,7));ax.set_xlabel('생산 구간');ax.set_ylabel('복원 증감배율 / 공식 증감배율');ax.set_title('④ 공식 배율의 재현과 원시 픽셀 차이');ax.legend(fontsize=9)
ax.text(.02,-.28,'5구간 원시 기준점은 해상도상 분리 불가.\n보정값의 일치는 설계된 제약이며 독립 검증이 아님.',transform=ax.transAxes,fontsize=9,color='#526773')
for ax in axes.flat:ax.grid(alpha=.18);ax.spines[['top','right']].set_visible(False)
fig.text(.09,.035,'네 시즌은 동일 게임의 관측 사건입니다. 통합 효과와 좁은 회귀 오차를 독립 실험의 인과 증거로 과장하지 않습니다.',fontsize=10,color='#526773')
p=ROOT/'Maple/figures/tier_regression_official_audit.png';fig.savefig(p);print(p)

# Verify measured 2025 chart boundaries directly against the original screenshot.
from PIL import Image
source=next(p for p in ROOT.glob('251016*.png') if '보스별' in p.name);fig,ax=plt.subplots(figsize=(14,6),dpi=160);ax.imshow(Image.open(source))
for row in read('official_20251016_pixels.csv')[::4]:
 x=float(row['x_pixel']);y=757
 for j in range(1,7):y-=float(row[f'old_tier{j}_pixels']);ax.plot([x-2,x+2],[y,y],color='black',lw=.55)
ax.set_xlim(115,1160);ax.set_ylim(765,270);ax.set_title('2025.10 공식 자료 픽셀 경계 확인');fig.tight_layout();fig.savefig(ROOT/'Maple/figures/official_20251016_pixel_audit.png')
