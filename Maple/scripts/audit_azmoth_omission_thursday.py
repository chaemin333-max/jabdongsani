"""Post-result diagnostic of a missing Azmoth component in 2510 total."""
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/total_ratio_exact_thursday_20260913'
d=pd.read_csv(D/'weekly_exact_thursday.csv',parse_dates=['date']);d=d[d.source_zero_y==824].copy()
d['azmoth_height']=np.where(d.azmoth_active,(824-d.azmoth_y).clip(lower=0),0.)
d['source_sum_excluding_azmoth']=d.source_sum-d.azmoth_height
train=(d.date>='2024-01-01')&(d.date<'2024-10-01');post=d.date>='2024-10-17'
out=[]
for source in ['source_sum','source_sum_excluding_azmoth']:
    v=d[source].to_numpy();X=np.column_stack([np.ones(len(d)),v]);y=d.target_negative_y.to_numpy()
    beta=np.linalg.lstsq(X[train],y[train],rcond=None)[0];pred=X@beta;d[source+'_prediction_from_pre']=pred
    for label,mask in [('pre_Azmoth_calibration',train),('after_Azmoth_all',post),('after_Azmoth_exclude_1_2_weeks',post&~d.contains_month_1_or_2)]:
        e=pred[mask]-y[mask]
        out.append(dict(source=source,period=label,n=int(mask.sum()),RMSE_target_pixels=float(np.sqrt(np.mean(e**2))),median_bias_pixels=float(np.median(e)),scale=beta[1]))
pd.DataFrame(out).to_csv(D/'azmoth_omission_diagnostic.csv',index=False)
d[['date','azmoth_height','source_sum','source_sum_excluding_azmoth','target_negative_y','source_sum_prediction_from_pre','source_sum_excluding_azmoth_prediction_from_pre']].to_csv(D/'azmoth_weekly_reconciliation.csv',index=False)
print(pd.DataFrame(out).to_string(index=False))
for day in ['2024-10-10','2024-10-17','2024-10-24','2024-12-19','2024-12-26','2025-01-02']:
    x=d[d.date.eq(day)]
    if len(x):print(day,'Azmoth height',round(x.azmoth_height.iloc[0],1),'sum',round(x.source_sum.iloc[0],1),'without',round(x.source_sum_excluding_azmoth.iloc[0],1),'target -y',round(x.target_negative_y.iloc[0],1))
