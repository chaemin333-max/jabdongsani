"""Enumerate all source combinations and run only identifiable comparisons.
No existing canonical total is used as a calibration target.
"""
from pathlib import Path
from itertools import combinations
import json
import numpy as np,pandas as pd
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
R=Path(__file__).resolve().parents[1];O=R/'data/four_source_alignment_20260913';O.mkdir(exist_ok=True)
a=pd.read_csv(R/'data/now_20250410_overlay_v2/digitized_overlay.csv')
old=pd.read_csv(R/'data/total_origin_audit_20260913/original_total_pixels.csv')
dates=pd.to_datetime(a.date)
valid=a.sum_px.notna()&(a.month_coordinate>=old.month.min())&(a.month_coordinate<=old.month.max())
z=a.loc[valid].copy();z['october_total_y']=np.interp(z.month_coordinate,old.month,old.y)
# Reserve post-Azmoth for comparison; fit on Jan-Sep 2024 only.
cal=(pd.to_datetime(z.date)>='2024-01-01')&(pd.to_datetime(z.date)<'2024-10-01')
hold=pd.to_datetime(z.date)>='2024-10-17'
res=[]
for zero in [748.,750.,752.,778.3827686]:
    target=zero-z.october_total_y
    k=float(np.median(target[cal]/z.loc[cal,'sum_px']))
    err=(k*z.sum_px-target)/target
    res.append(dict(comparison='2504_sum_to_2510_total',zero_y=zero,fit='one_scale_2024JanSep',scale=k,intercept_px=0,train_MAPE=float(err[cal].abs().mean()*100),holdout_MAPE=float(err[hold].abs().mean()*100),holdout_bias=float(err[hold].median()*100)))
# Free intercept estimates an implied zero; it does not prove that zero is true.
k,b=np.polyfit(z.loc[cal,'sum_px'],-z.loc[cal,'october_total_y'],1)
zero=-b;target=zero-z.october_total_y;err=(k*z.sum_px-target)/target
res.append(dict(comparison='2504_sum_to_2510_total',zero_y=zero,fit='free_zero_2024JanSep',scale=k,intercept_px=b,train_MAPE=float(err[cal].abs().mean()*100),holdout_MAPE=float(err[hold].abs().mean()*100),holdout_bias=float(err[hold].median()*100)))
z['source_affine_predicted_y']=-(k*z.sum_px+b);z.to_csv(O/'april_october_total_comparison.csv',index=False)
pd.DataFrame(res).to_csv(O/'zero_sensitivity.csv',index=False)
# October and September production-source plots have a real common interval.
p=pd.read_csv(R/'data/field_share_reconstruction_20260912/source_pixels.csv')
oct=p[p.source.astype(str)=='251016'].pivot(index='date',columns='series',values='height')
sep=p[p.source.astype(str)=='260910'].pivot(index='date',columns='series',values='height')
ratios=pd.concat([oct.field/(oct.boss+oct.field)*100,sep.field/(sep.boss+sep.field)*100],axis=1,keys=['2510','2609']).dropna()
ratios['difference_pp']=ratios['2609']-ratios['2510'];ratios.to_csv(O/'october_september_BF.csv')
prior=json.loads((R/'data/april_vs_231116/summary.json').read_text())
pairs=[]
for x,y in combinations(['2311','2504','2510','2609'],2):
    metric='';value=None;status='NO_COMMON_OBSERVABLE';reason=''
    if (x,y)==('2311','2504'):
        status='COMPARABLE';metric='mean_abs_BF_share_difference_pp';value=prior['mean_abs_BF_difference_pp'];reason='2023AprOct; excludes Ursus from both denominators; no scale fit'
    elif (x,y)==('2504','2510'):
        status='CONDITIONAL_COMPARABLE';metric='postAzmoth_MAPE_free_zero_pct';value=res[-1]['holdout_MAPE'];reason='April source sum versus October total; source scope and zero not established'
    elif (x,y)==('2510','2609'):
        status='COMPARABLE';metric='mean_abs_BF_share_difference_pp';value=float(ratios.difference_pp.abs().mean());reason=f'{len(ratios)} overlapping observed weeks; boss reward and field only; no total canonical fitting'
    elif (x,y)==('2311','2510'):reason='October total covers 2023 but has no contemporaneous B/F split; old boss tiers omit monthly/daily scopes'
    else:reason='No overlapping dates for same observable'
    pairs.append(dict(source1=x,source2=y,status=status,metric=metric,value=value,reason=reason))
pd.DataFrame(pairs).to_csv(O/'all_six_pairs.csv',index=False)
joint=[]
for n in [3,4]:
 for group in combinations(['2311','2504','2510','2609'],n):
    edges=[p for p in pairs if p['source1'] in group and p['source2'] in group and 'COMPARABLE' in p['status'] and p['status']!='NO_COMMON_OBSERVABLE']
    joint.append(dict(sources='+'.join(group),comparable_edges=len(edges),independent_cycle_count=0,status='NOT_IDENTIFIABLE_AS_COMMON_CURVE',error='',reason='No common-time common-variable dataset; no closed independent comparison cycle; cannot assign one source as culprit'))
pd.DataFrame(joint).to_csv(O/'all_joint_combinations.csv',index=False)
summary={'pairs':pairs,'zero_sensitivity':res,'joint_combinations':joint,'conclusion':'2504-only outlier not established. MAPE and percentage-point differences are different metrics, not rankable in one score.'}
(O/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
assert len(pairs)==6 and len(joint)==5 and len(ratios)>0
for f in (R/'assets/fonts').glob('NotoSansKR*.ttf'):font_manager.fontManager.addfont(str(f))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False})
fig,axs=plt.subplots(1,2,figsize=(13,5),layout='constrained')
axs[0].plot(pd.to_datetime(z.date),z.october_total_y,label='2510 총생산 원본 y')
axs[0].plot(pd.to_datetime(z.date),z.source_affine_predicted_y,'--',label='2504 합계→2510 y (단일 선형 환산)')
axs[0].invert_yaxis();axs[0].set_ylabel('원본 픽셀 y (위쪽일수록 생산 많음)');axs[0].legend(fontsize=9);axs[0].tick_params(axis='x',rotation=30)
axs[1].plot(ratios.index,ratios['2510'],'o-',label='2510');axs[1].plot(ratios.index,ratios['2609'],'s--',label='2609');axs[1].set_ylabel('사냥 / (보스리워드 + 사냥), %');axs[1].tick_params(axis='x',rotation=30);axs[1].legend()
for ax in axs:ax.grid(alpha=.2)
fig.suptitle('원본끼리의 대조 · 기존 총생산 정본으로 강제 정렬하지 않음')
fig.savefig(R/'figures/four_source_alignment_20260913.png',dpi=160)
print(json.dumps(summary,ensure_ascii=False))
