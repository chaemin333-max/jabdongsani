from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.optimize import minimize_scalar
R=Path(__file__).resolve().parents[1];D=R/'data/total_ratio_exact_thursday_20260913'
d=pd.read_csv(D/'weekly_exact_thursday.csv',parse_dates=['date']);d=d[d.source_zero_y==824].copy()
d['azmoth_height']=np.where(d.azmoth_active,(824-d.azmoth_y).clip(lower=0),0)
d['sum_without_az']=d.source_sum-d.azmoth_height
train=(d.date>='2024-01-01')&(d.date<'2024-10-01');post=d.date>='2024-10-17'
out=[]
for label,source_sum in [('full_sources',d.source_sum),('sources_without_azmoth',d.sum_without_az)]:
    ratio=source_sum/d.boss_source
    X=np.column_stack([np.ones(len(d)),ratio,ratio*d.total_px])
    y=d.target_negative_y.to_numpy();beta=np.linalg.lstsq(X[train],y[train],rcond=None)[0];pred=X@beta
    implied_origin=beta[1]/beta[2]
    for period,mask in [('pre_train',train),('post_all',post),('post_without_1_2_week',post&~d.contains_month_1_or_2)]:
        e=pred[mask]-y[mask]
        out.append(dict(source_ratio=label,period=period,n=int(mask.sum()),RMSE_target_pixels=float(np.sqrt(np.mean(e**2))),median_bias_pixels=float(np.median(e)),implied_bar_additive_origin_px=float(implied_origin)))
pd.DataFrame(out).to_csv(D/'ratio_formula_azmoth_sensitivity.csv',index=False)
print(pd.DataFrame(out).to_string(index=False))
