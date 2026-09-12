"""Source-origin sensitivity with all other calibration choices unchanged."""
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/four_total_bridges_20260913'
src=pd.read_csv(R/'data/now_20250410_overlay_v2/digitized_overlay.csv',parse_dates=['date'])
bar=pd.read_csv(R/'data/four_boss_window_alignment/2504_pixels.csv',parse_dates=['date'])
orig=pd.read_csv(R/'data/total_origin_audit_20260913/original_total_pixels.csv')
rows=[]
for z in [824,826,828,832,836]:
    x=src[['date','boss_y','field_y','azmoth_y','other_coin_y','etc_y']].copy()
    h={n:(z-x[n+'_y']).clip(lower=0).fillna(0) for n in ['boss','field','azmoth','other_coin','etc']}
    h['azmoth']=h['azmoth'].where(x.date>=pd.Timestamp('2024-10-17'),0)
    h['other_coin']=h['other_coin'].where(x.date>=pd.Timestamp('2024-02-22'),0)
    x['sum']=sum(h.values());x['ratio']=x['sum']/h['boss']
    q=pd.merge_asof(bar[['date','total_px']].sort_values('date'),x[['date','sum','ratio']].sort_values('date'),on='date',direction='nearest',tolerance=pd.Timedelta(days=4)).dropna()
    q['month']=(q.date.dt.year-2023)*12+q.date.dt.month-1+(q.date.dt.day-1)/q.date.dt.days_in_month
    q=q[(q.month>=orig.month.min())&(q.month<=orig.month.max())]
    y=-np.interp(q.month,orig.month,orig.y);train=(q.date>='2024-01-01')&(q.date<'2024-10-01');test=q.date>='2024-10-17'
    for label,v in [('sum',q['sum'].to_numpy()),('ratio_Bbar',(q.total_px*q.ratio).to_numpy())]:
        X=np.column_stack([np.ones(len(q)),v]);b=np.linalg.lstsq(X[train],y[train],rcond=None)[0]
        e=X@b-y
        rows.append(dict(source_zero_candidate_y=z,method=label,pre_train_RMSE_px=float(np.sqrt(np.mean(e[train]**2))),post_Azmoth_RMSE_px=float(np.sqrt(np.mean(e[test]**2))),post_Azmoth_median_bias_px=float(np.median(e[test]))))
d=pd.DataFrame(rows);d.to_csv(D/'source_zero_sensitivity.csv',index=False);print(d.to_string(index=False))
