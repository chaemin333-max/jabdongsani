"""Check whether monthly boss timing explains bar/source differences after free offsets."""
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];O=R/'data/four_total_bridges_20260913'
d=pd.read_csv(O/'matched_bar_source.csv',parse_dates=['date'])
out=[]
for source,g in d.groupby('source_name'):
    g=g.dropna(subset=['bar','source']).copy()
    g['month_start']=((g.date.dt.day<=4)|(g.date.dt.days_in_month-g.date.dt.day<4)).astype(float)
    y=g.source.to_numpy()
    for include in [False,True]:
        X=np.column_stack([np.ones(len(g)),g.bar.to_numpy(),g.month_start.to_numpy()]) if include else np.column_stack([np.ones(len(g)),g.bar.to_numpy()])
        beta=np.linalg.lstsq(X,y,rcond=None)[0];pred=X@beta
        out.append(dict(source=source,month_start_included=include,n=len(g),intercept=beta[0],bar_slope=beta[1],month_start_coefficient_pixels=beta[2] if include else np.nan,RMSE_pixels=np.sqrt(np.mean((pred-y)**2)),R2=1-np.sum((pred-y)**2)/np.sum((y-y.mean())**2)))
pd.DataFrame(out).to_csv(O/'monthly_boss_scope_diagnostic.csv',index=False)
print(pd.DataFrame(out).to_string(index=False))
