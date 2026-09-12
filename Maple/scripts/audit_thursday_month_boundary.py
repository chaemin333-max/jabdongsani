"""Re-run source/total bridges on Thursday observation weeks excluding days 1-2."""
from pathlib import Path
import json
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/thursday_month_boundary_audit_20260913';D.mkdir(parents=True,exist_ok=True)

def month_boundary_week(day):
    d=pd.Timestamp(day).normalize()
    assert d.weekday()==3,(d,d.day_name())
    return any((d+pd.Timedelta(days=i)).day in (1,2) for i in range(7))

base=pd.read_csv(R/'data/four_total_bridges_20260913/total_ratio_formula_weekly.csv',parse_dates=['date'])
base['thursday']=base.date.dt.normalize()
base['contains_month_day_1_or_2']=base.thursday.map(month_boundary_week)
base['date_is_1_or_2']=base.thursday.dt.day.isin([1,2])
base.to_csv(D/'weekly_keep_flags.csv',index=False)
results=[]
for rule in ['all','exclude_date_1_or_2','exclude_week_containing_1_or_2']:
    keep=pd.Series(True,index=base.index)
    if rule=='exclude_date_1_or_2':keep=~base.date_is_1_or_2
    if rule=='exclude_week_containing_1_or_2':keep=~base.contains_month_day_1_or_2
    train=keep&(base.date>='2024-01-01')&(base.date<'2024-10-01')
    test=keep&(base.date>='2024-10-17')
    for method,cols in [('source_sum',['source_sum_height']),('ratio_free_origin',['ratio_source_sum_over_boss','ratio_times_bar'])]:
        base['ratio_times_bar']=base.ratio_source_sum_over_boss*base.total_px
        X=np.column_stack([np.ones(len(base))]+[base[c] for c in cols]);y=-base.october_total_y.to_numpy()
        beta=np.linalg.lstsq(X[train],y[train],rcond=None)[0]
        pred=X@beta
        for label,m in [('train',train),('after_Azmoth',test)]:
            err=pred[m]-y[m]
            results.append(dict(rule=rule,method=method,period=label,n=int(m.sum()),RMSE_2510_original_pixels=float(np.sqrt(np.mean(err**2))),median_signed_error_pixels=float(np.median(err)),coefficients=json.dumps(beta.tolist())))
pd.DataFrame(results).to_csv(D/'formula_comparison.csv',index=False)
fixed=[]
for method,col in [('source_sum','source_sum_only_predicted_negative_y'),('ratio_free_origin','ratio_with_bar_free_origin_predicted_negative_y')]:
    err=base[col]+base.october_total_y
    post=base.date>='2024-10-17'
    for label,mask in [('all_post',post),('post_excluding_month_1_2_weeks',post&~base.contains_month_day_1_or_2)]:
        fixed.append(dict(method=method,period=label,n=int(mask.sum()),RMSE_fixed_model_pixels=float(np.sqrt(np.mean(err[mask]**2))),median_bias_fixed_model_pixels=float(np.median(err[mask]))))
pd.DataFrame(fixed).to_csv(D/'fixed_model_post_subset.csv',index=False)

bridge=pd.read_csv(R/'data/four_total_bridges_20260913/matched_bar_source.csv',parse_dates=['date'])
change=[]
for name,g in bridge.groupby('source_name'):
    g=g.sort_values('date').copy();g['thursday']=g.date.dt.normalize()
    g['excluded']=g.thursday.map(month_boundary_week)
    g['days']=g.thursday.diff().dt.days
    g['db']=g.bar.diff();g['ds']=g.source.diff()
    g['prior_excluded']=g.excluded.shift(1,fill_value=False)
    for rule in ['all','exclude_week_containing_1_or_2']:
        use=(g.days<=9)&g.db.notna()&g.ds.notna()
        if rule!='all':use&=~g.excluded&~g.prior_excluded
        x=g.loc[use,'db'].to_numpy();y=g.loc[use,'ds'].to_numpy()
        change.append(dict(source=name,rule=rule,n=len(x),weekly_change_corr=float(np.corrcoef(x,y)[0,1]),same_direction=float(np.mean(np.sign(x)==np.sign(y)))))
pd.DataFrame(change).to_csv(D/'bar_source_change_comparison.csv',index=False)
assert len(results)==12 and len(change)==6
assert base.contains_month_day_1_or_2.sum()>base.date_is_1_or_2.sum()
print(pd.DataFrame(results)[['rule','method','period','n','RMSE_2510_original_pixels']].to_string(index=False))
print(pd.DataFrame(fixed).to_string(index=False))
print(pd.DataFrame(change).to_string(index=False))
