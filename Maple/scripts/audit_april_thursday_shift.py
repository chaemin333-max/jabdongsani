from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/thursday_month_boundary_audit_20260913'
bar=pd.read_csv(R/'data/four_boss_window_alignment/2504_pixels.csv',parse_dates=['date'])
src=pd.read_csv(R/'data/now_20250410_overlay_v2/digitized_overlay.csv',parse_dates=['date']).sort_values('date')
bar=bar.sort_values('date');t=src.date.astype('datetime64[ns]').astype('int64').to_numpy()
out=[]
for offset in [-2,-1,0,1,2]:
    q=(bar.date+pd.Timedelta(days=offset)).astype('datetime64[ns]').astype('int64').to_numpy()
    y=-np.interp(q,t,src.boss_y)
    x=-bar.top_y.to_numpy();dx=np.diff(x);dy=np.diff(y)
    valid=(bar.date.diff().dt.days.to_numpy()[1:]<=9)
    def boundary(d):
        p=pd.Timestamp(d).normalize();return any((p+pd.Timedelta(days=i)).day in (1,2) for i in range(7))
    excluded=np.array([boundary(d) for d in bar.date])
    for label,mask in [('all',valid),('exclude_week_containing_1_or_2',valid&~excluded[1:]&~excluded[:-1])]:
        out.append(dict(source_date_shift_days=offset,rule=label,n=int(mask.sum()),change_corr=float(np.corrcoef(dx[mask],dy[mask])[0,1])))
d=pd.DataFrame(out);d.to_csv(D/'april_date_shift_sensitivity.csv',index=False);print(d.to_string(index=False))
