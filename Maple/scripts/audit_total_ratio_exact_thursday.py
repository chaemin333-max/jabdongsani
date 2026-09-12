"""Reconstruct 2504 source values at exact Thursday bar dates; event on Thursday."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.optimize import minimize_scalar
R=Path(__file__).resolve().parents[1];D=R/'data/total_ratio_exact_thursday_20260913';D.mkdir(parents=True,exist_ok=True)
bar=pd.read_csv(R/'data/four_boss_window_alignment/2504_pixels.csv',parse_dates=['date']).sort_values('date')
bar.date=bar.date.dt.normalize()
source=pd.read_csv(R/'data/now_20250410_overlay_v2/digitized_overlay.csv',parse_dates=['date']).sort_values('date')
target=pd.read_csv(R/'data/total_origin_audit_20260913/original_total_pixels.csv')
q=bar[['date','total_px','top_y']].copy()
for name in ['boss','field','azmoth','other_coin','etc']:
    col=name+'_y';s=source.dropna(subset=[col]);q[col]=np.interp(q.date.astype('datetime64[ns]').astype('int64'),s.date.astype('datetime64[ns]').astype('int64'),s[col])
q['azmoth_active']=q.date>=pd.Timestamp('2024-10-17')
q['other_coin_active']=q.date>=pd.Timestamp('2024-02-22')
q['contains_month_1_or_2']=q.date.map(lambda t:any((t+pd.Timedelta(days=i)).day in (1,2) for i in range(7)))
q['month']=(q.date.dt.year-2023)*12+q.date.dt.month-1+(q.date.dt.day-1)/q.date.dt.days_in_month
q=q[(q.month>=target.month.min())&(q.month<=target.month.max())].copy()
q['target_negative_y']=-np.interp(q.month,target.month,target.y)
allresults=[];allrows=[]
for zero in [824.,826.,828.,832.,836.]:
    d=q.copy();height={n:(zero-d[n+'_y']).clip(lower=0) for n in ['boss','field','azmoth','other_coin','etc']}
    height['azmoth']=height['azmoth'].where(d.azmoth_active,0.)
    height['other_coin']=height['other_coin'].where(d.other_coin_active,0.)
    d['source_sum']=sum(height.values());d['boss_source']=height['boss'];d['ratio']=d.source_sum/d.boss_source
    train=(d.date>='2024-01-01')&(d.date<'2024-10-01')
    post=d.date>='2024-10-17'
    methods={
        'source_sum':np.column_stack([np.ones(len(d)),d.source_sum]),
        'ratio_free_origin':np.column_stack([np.ones(len(d)),d.ratio,d.ratio*d.total_px]),
    }
    # q additive bar origin is restricted so every bar remains positive.
    low=-float(d.total_px.min())+1
    def fit_constrained(origin):
        X=np.column_stack([np.ones(len(d)),d.ratio*(d.total_px+origin)])
        beta=np.linalg.lstsq(X[train],d.loc[train,'target_negative_y'],rcond=None)[0]
        pred=X@beta
        return float(np.sum((pred[train]-d.loc[train,'target_negative_y'])**2)),pred,beta
    optimum=minimize_scalar(lambda origin:fit_constrained(origin)[0],bounds=(low,300),method='bounded')
    _,predcon,betacon=fit_constrained(optimum.x)
    for method,X in methods.items():
        beta=np.linalg.lstsq(X[train],d.loc[train,'target_negative_y'],rcond=None)[0]
        pred=X@beta;d[method+'_prediction']=pred
        for period,mask in [('train',train),('post_all',post),('post_exclude_month1_2',post&~d.contains_month_1_or_2)]:
            err=pred[mask]-d.loc[mask,'target_negative_y']
            allresults.append(dict(source_zero_y=zero,method=method,period=period,n=int(mask.sum()),RMSE_target_pixels=float(np.sqrt(np.mean(err**2))),median_signed_error=float(np.median(err)),coefficients=json.dumps(beta.tolist())))
    d['ratio_positive_origin_prediction']=predcon
    for period,mask in [('train',train),('post_all',post),('post_exclude_month1_2',post&~d.contains_month_1_or_2)]:
        err=predcon[mask]-d.loc[mask,'target_negative_y']
        allresults.append(dict(source_zero_y=zero,method='ratio_positive_origin',period=period,n=int(mask.sum()),RMSE_target_pixels=float(np.sqrt(np.mean(err**2))),median_signed_error=float(np.median(err)),coefficients=json.dumps({'origin':optimum.x,'beta':betacon.tolist()})))
    d['source_zero_y']=zero;allrows.append(d)
pd.DataFrame(allresults).to_csv(D/'formula_sensitivity.csv',index=False)
pd.concat(allrows).to_csv(D/'weekly_exact_thursday.csv',index=False)
z=pd.DataFrame(allresults);print(z[z.source_zero_y==824][['method','period','n','RMSE_target_pixels','median_signed_error']].to_string(index=False))
print('10/17-10/24',q[q.date.isin([pd.Timestamp('2024-10-17'),pd.Timestamp('2024-10-24')])][['date','boss_y','azmoth_y','target_negative_y']].to_string(index=False))
assert q.date.dt.weekday.eq(3).all()
assert q[q.date.eq('2024-10-17')].azmoth_active.all()
assert len(z)==45
