"""Test Bbar/(Bsource/Ssource) with free additive origins against October total pixels."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.optimize import minimize_scalar
R=Path(__file__).resolve().parents[1];O=R/'data/four_total_bridges_20260913'
bar=pd.read_csv(R/'data/four_boss_window_alignment/2504_pixels.csv',parse_dates=['date'])
src=pd.read_csv(R/'data/now_20250410_overlay_v2/digitized_overlay.csv',parse_dates=['date'])
target=pd.read_csv(R/'data/total_origin_audit_20260913/original_total_pixels.csv')
sourcecols=['boss_y','field_y','azmoth_y','other_coin_y','etc_y']
z=824.0000295505364 # lower feasible limit reached in official September share fit; sensitivity needed
src['boss_height']=z-src.boss_y
src['source_sum_height']=0.
for col in sourcecols:
    h=(z-src[col]).clip(lower=0)
    if col=='azmoth_y':h=h.where(src.date>=pd.Timestamp('2024-10-17'),0.)
    if col=='other_coin_y':h=h.where(src.date>=pd.Timestamp('2024-02-22'),0.)
    src['source_sum_height']+=h.fillna(0)
src['ratio_source_sum_over_boss']=src.source_sum_height/src.boss_height
q=pd.merge_asof(bar[['date','total_px']].sort_values('date'),src[['date','ratio_source_sum_over_boss','source_sum_height']].sort_values('date'),on='date',direction='nearest',tolerance=pd.Timedelta(days=4)).dropna()
month=target.month.to_numpy();y=target.y.to_numpy()
q['month']=(q.date.dt.year-2023)*12+q.date.dt.month-1+(q.date.dt.day-1)/q.date.dt.days_in_month
q=q[(q.month>=month.min())&(q.month<=month.max())].copy()
q['october_total_y']=np.interp(q.month,month,y)
# Diagnostic models of the same raw images. No economic zero is fixed.
train=(q.date>='2024-01-01')&(q.date<'2024-10-01');test=q.date>='2024-10-17'
results=[]
for method,cols in [('source_sum_only',['source_sum_height']),('ratio_with_bar_free_origin',['ratio_source_sum_over_boss','ratio_times_bar'])]:
    q['ratio_times_bar']=q.ratio_source_sum_over_boss*q.total_px
    X=np.column_stack([np.ones(len(q))]+[q[c] for c in cols]);beta=np.linalg.lstsq(X[train],-q.loc[train,'october_total_y'],rcond=None)[0]
    pred=X@beta
    for label,mask in [('train',train),('post_Azmoth',test)]:
        err=pred[mask]+q.loc[mask,'october_total_y'].to_numpy()
        span=np.percentile(q.loc[mask,'october_total_y'],90)-np.percentile(q.loc[mask,'october_total_y'],10)
        results.append(dict(method=method,window=label,n=int(mask.sum()),RMSE_original_total_pixels=float(np.sqrt(np.mean(err**2))),median_bias_pixels=float(np.median(err)),RMSE_over_target_span_pct=float(100*np.sqrt(np.mean(err**2))/span),coefficients=json.dumps(beta.tolist())))
    q[method+'_predicted_negative_y']=pred
pd.DataFrame(results).to_csv(O/'total_ratio_formula_test.csv',index=False)
constrained=[]
lower=-float(q.total_px.min())+1
for high in [0,100,300]:
    if high<=lower:continue
    def fit_at_origin(origin):
        v=(q.total_px+origin)*q.ratio_source_sum_over_boss
        X=np.column_stack([np.ones(len(q)),v]);beta=np.linalg.lstsq(X[train],-q.loc[train,'october_total_y'],rcond=None)[0]
        pred=X@beta;err=pred[train]+q.loc[train,'october_total_y'].to_numpy()
        return float(np.sum(err*err)),beta,pred
    optimum=minimize_scalar(lambda origin:fit_at_origin(origin)[0],bounds=(lower,high),method='bounded')
    loss,beta,pred=fit_at_origin(optimum.x)
    for label,mask in [('train',train),('post_Azmoth',test)]:
        err=pred[mask]+q.loc[mask,'october_total_y'].to_numpy()
        constrained.append(dict(origin_upper_bound=high,origin_lower_bound=lower,fitted_origin=optimum.x,scale=beta[1],window=label,n=int(mask.sum()),RMSE_original_total_pixels=float(np.sqrt(np.mean(err**2))),median_bias_pixels=float(np.median(err))))
pd.DataFrame(constrained).to_csv(O/'total_ratio_physical_origin_sensitivity.csv',index=False)
q.to_csv(O/'total_ratio_formula_weekly.csv',index=False)
print(pd.DataFrame(results).to_string(index=False))
print(pd.DataFrame(constrained).to_string(index=False))
