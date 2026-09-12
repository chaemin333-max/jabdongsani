"""Independent within-2510 check: published total line vs source-panel sum."""
from pathlib import Path
import calendar
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/total_ratio_exact_thursday_20260913'
p=pd.read_csv(R/'data/field_share_reconstruction_20260912/source_pixels.csv',parse_dates=['date'])
p=p[p.source.astype(str)=='251016'].pivot(index='date',columns='series',values='height').reset_index()
t=pd.read_csv(R/'data/total_origin_audit_20260913/original_total_pixels.csv')
p['month']=(p.date.dt.year-2023)*12+p.date.dt.month-1+(p.date.dt.day-1)/p.date.dt.days_in_month
p=p[(p.month>=t.month.min())&(p.month<=t.month.max())].copy()
p['total_negative_y']=-np.interp(p.month,t.month,t.y)
groups={'full':['boss','field','coin_dark','coin_light','other'],'without_dark_azmoth':['boss','field','coin_light','other']}
out=[]
for name,cols in groups.items():
    q=p.dropna(subset=cols).copy();q['sum']=q[cols].sum(axis=1)
    # Fit constant scale and intercept before the July ASSEMBLE jump; evaluate later.
    train=q.date<'2025-06-19';test=q.date>='2025-06-19'
    if train.sum()<4:continue
    X=np.column_stack([np.ones(len(q)),q['sum']]);beta=np.linalg.lstsq(X[train],q.loc[train,'total_negative_y'],rcond=None)[0]
    err=X@beta-q.total_negative_y.to_numpy()
    for label,mask in [('train',train),('later',test)]:
        out.append(dict(source_sum=name,period=label,n=int(mask.sum()),RMSE_total_pixels=float(np.sqrt(np.mean(err[mask]**2))),median_bias_pixels=float(np.median(err[mask]))))
pd.DataFrame(out).to_csv(D/'within_2510_coin_scope.csv',index=False);print(pd.DataFrame(out).to_string(index=False))
