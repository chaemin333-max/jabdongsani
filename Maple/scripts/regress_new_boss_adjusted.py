"""Observed tier changes with separate menu-expansion controls."""
import numpy as np
from datetime import date
from pathlib import Path
from audit_tier_regression import regress,read
from fit_tier_boss_decomposition import write
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Maple/data/new_boss_reward_opportunities'
bars=read(ROOT/'Maple/data/now_20260910/boss_tier_weekly.csv');wins=read(ROOT/'Maple/data/now_20260910/season_identification_windows.csv')
pop={r['date']:r for r in read(ROOT/'Maple/data/maple_production_calibration_inputs_weekly.csv')}
menu={(r['profile'],r['date']):float(r['opportunity_factor']) for r in read(D/'weekly_opportunity_factors.csv')}
ds=[date.fromisoformat(r['date']) for r in bars]
good=np.array([not any(abs((d-date.fromisoformat(w[k])).days)<=7 for w in wins for k in ['start','season_end']) for d in ds]);valid=good[1:]&good[:-1];positions=np.arange(1,len(ds))[valid]
A=np.array([float(pop[str(d)]['A_main_accounts']) for d in ds]);C=np.array([float(pop[str(d)]['C_challenger_accounts']) for d in ds])
B=np.array([[float(r[f'tier{j}_raw']) for j in range(1,8)] for r in bars]);F=np.array([menu['main_upper',str(d)] for d in ds]);FC=np.array([menu['challenger_seren',str(d)] for d in ds])
growth={'2025-03-20','2025-07-17','2026-02-12','2026-03-19','2026-07-23'};reward={'2025-04-17','2025-10-23'}
base=[np.ones(len(ds)-1),np.diff(np.log(A)),np.diff(np.log1p(C/1e5)),np.array([float(str(d) in reward) for d in ds[1:]]),np.array([float(str(d) in growth) for d in ds[1:]])]
upper=np.diff(np.log1p(B[:,4:].sum(1)/2.944717415)-np.log(F))
names=['intercept','dlog_A','dlog1p_C_100k','reward_pulse','growth_pulse','upper_fixed_menu_change','main_new_boss_menu_change','shared_easy_adversary_menu_change']
X=np.array(base+[upper,np.diff(np.log(F)),np.diff(np.log(FC))]).T[valid]
rows=[];summary=[]
for label,y in [('low2',np.log(B[:,:2].sum(1))),('tier3',np.log1p(B[:,2]/2.944717415)),('tier4',np.log1p(B[:,3]/2.944717415))]:
    rr,ss=regress(np.diff(y)[valid],X,names,positions,label+'_new_menu_adjusted_HAC4');rows.extend(rr);summary.append(ss)
write(D/'adjusted_regression.csv',rows);write(D/'adjusted_regression_models.csv',summary)
for r in rows:
    if r['term'] in ['dlog1p_C_100k','main_new_boss_menu_change','shared_easy_adversary_menu_change']:print(r)
