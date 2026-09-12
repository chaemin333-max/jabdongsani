from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/total_ratio_exact_thursday_20260913'
allrows=pd.read_csv(D/'weekly_exact_thursday.csv',parse_dates=['date']);out=[]
for z,d in allrows.groupby('source_zero_y'):
    d=d.copy();az=np.where(d.azmoth_active,(z-d.azmoth_y).clip(lower=0),0)
    pre=(d.date>='2024-01-01')&(d.date<'2024-10-01');post=d.date>='2024-10-17'
    for label,v in [('with_azmoth',d.source_sum),('without_azmoth',d.source_sum-az)]:
        X=np.column_stack([np.ones(len(d)),v]);y=d.target_negative_y.to_numpy();b=np.linalg.lstsq(X[pre],y[pre],rcond=None)[0]
        err=(X@b-y)[post]
        out.append(dict(source_zero_y=z,scenario=label,n=int(post.sum()),post_RMSE_2510_total_pixels=float(np.sqrt(np.mean(err**2))),post_median_bias_pixels=float(np.median(err))))
out=pd.DataFrame(out);out.to_csv(D/'azmoth_zero_sensitivity.csv',index=False);print(out.to_string(index=False))
