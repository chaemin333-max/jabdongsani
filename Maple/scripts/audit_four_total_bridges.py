"""Find which bar->source->total bridge fails without assuming drawn y=0."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.optimize import minimize_scalar
R=Path(__file__).resolve().parents[1];O=R/'data/four_total_bridges_20260913';O.mkdir(parents=True,exist_ok=True)
def read2(path):return pd.read_csv(path,parse_dates=['date'])
apr_bar=read2(R/'data/four_boss_window_alignment/2504_pixels.csv')[['date','top_y']].rename(columns={'top_y':'y'})
apr_bar['v']=-apr_bar.y
apr_src=read2(R/'data/now_20250410_overlay_v2/digitized_overlay.csv')[['date','boss_y','field_y','azmoth_y','other_coin_y','etc_y']]
apr_b=apr_src[['date','boss_y']].rename(columns={'boss_y':'y'});apr_b['v']=-apr_b.y
oct_bar=read2(R/'data/tier_regression_audit/official_20251016_pixels.csv')[['date','height_pixels']].rename(columns={'height_pixels':'v'})
oct_p=read2(R/'data/field_share_reconstruction_20260912/source_pixels.csv');oct_p=oct_p[oct_p.source.astype(str)=='251016']
oct_b=oct_p[oct_p.series=='boss'][['date','y_pixel']].dropna().rename(columns={'y_pixel':'y'});oct_b['v']=-oct_b.y
sep_bar=read2(R/'data/now_20260910/boss_tier_weekly.csv')
sep_bar=sep_bar[['date']+[f'tier{i}_raw' for i in range(1,8)]]
sep_bar['v']=sep_bar[[f'tier{i}_raw' for i in range(1,8)]].sum(axis=1)
sep_b=read2(R/'data/now_20260910/production_by_source_weekly.csv');sep_b=sep_b[sep_b.series=='boss_rewards'][['date','line_y_pixel']].dropna().rename(columns={'line_y_pixel':'y'});sep_b['v']=-sep_b.y
bridges=[];detail=[]
for name,bar,source in [('2504',apr_bar,apr_b),('2510',oct_bar,oct_b),('2609',sep_bar,sep_b)]:
    x=bar[['date','v']].rename(columns={'v':'bar'}).sort_values('date');y=source[['date','v']].rename(columns={'v':'source'}).sort_values('date')
    z=pd.merge_asof(x,y,on='date',direction='nearest',tolerance=pd.Timedelta(days=4)).dropna()
    z['bar_change']=z.bar.diff();z['source_change']=z.source.diff();z['days']=z.date.diff().dt.days
    q=z[(z.days<=9)&z.bar_change.notna()].copy()
    # For 2504 the source has daily detail, for others weekly plotted observations.
    for smooth in [1,3,5]:
        dx=q.bar_change.rolling(smooth,center=True,min_periods=smooth).mean()
        dy=q.source_change.rolling(smooth,center=True,min_periods=smooth).mean()
        ok=dx.notna()&dy.notna();dx=dx[ok].to_numpy();dy=dy[ok].to_numpy()
        if len(dx)<4:continue
        k=np.dot(dx,dy)/np.dot(dx,dx)
        bridges.append(dict(source=name,window_start=str(z.date.min().date()),window_end=str(z.date.max().date()),plotted_matches=len(z),valid_adjacent_changes=len(q),smooth_weeks=smooth,n=len(dx),difference_corr=np.corrcoef(dx,dy)[0,1],difference_scale=k,change_rmse=np.sqrt(np.mean((k*dx-dy)**2))))
    z['source_name']=name;detail.append(z)
pd.DataFrame(bridges).to_csv(O/'bar_source_bridge.csv',index=False)
pd.concat(detail).to_csv(O/'matched_bar_source.csv',index=False)
# Official 11-day shares constrain the source-chart intercept independently of canonical total.
official=pd.read_csv(R/'data/production_evidence_search_20260912/official_20241028_shares.csv')
dates=pd.to_datetime(apr_src.date).astype('datetime64[ns]').astype('int64').to_numpy()
columns={'boss':'boss_y','field':'field_y','azmoth':'azmoth_y','other_coin':'other_coin_y','etc':'etc_y'}
tests=[]
for o in official.itertuples():
    ds=pd.date_range(o.start,o.end)+pd.Timedelta(hours=12);ns=ds.as_unit('ns').astype('int64').to_numpy();v={}
    for n,c in columns.items():
        good=apr_src[c].notna().to_numpy();v[n]=np.interp(ns,dates[good],apr_src[c][good]).mean()
    tests.append((o,v))
def shares(z,o,v):
    heights={n:max(0,z-y) for n,y in v.items()}
    if o.window_label.startswith('September'):heights['azmoth']=0
    total=sum(heights.values());return {n:100*h/total for n,h in heights.items()}
def loss(z):
    e=[]
    for o,v in tests:
        s=shares(z,o,v)
        for n,k in [('boss','boss_pct'),('field','field_pct'),('azmoth','coin_azmoth_pct'),('other_coin','coin_other_pct'),('etc','other_pct')]:e.append(s[n]-getattr(o,k))
    return np.mean(np.square(e))
opt=minimize_scalar(loss,bounds=(824,845),method='bounded')
opt_sep=minimize_scalar(lambda z:np.mean([(shares(z,tests[0][0],tests[0][1])[n]-getattr(tests[0][0],k))**2 for n,k in [('boss','boss_pct'),('field','field_pct'),('other_coin','coin_other_pct'),('etc','other_pct')]]),bounds=(824,845),method='bounded')
anchor=[]
for z in [824.,826.,828.,float(opt.x)]:
 for o,v in tests:
    s=shares(z,o,v)
    anchor.append(dict(zero_y=z,window=o.window_label,mean_squared_pp=loss(z),**{n+'_pct':s[n] for n in s}))
pd.DataFrame(anchor).to_csv(O/'april_official_share_zero.csv',index=False)
summary={'zero_y_fit_to_official_shares':float(opt.x),'fit_rmse_pp':float(np.sqrt(opt.fun)),'zero_y_fit_September_only':float(opt_sep.x),'October_share_RMSE_with_September_zero_pp':float(np.sqrt(np.mean([(shares(opt_sep.x,tests[1][0],tests[1][1])[n]-getattr(tests[1][0],k))**2 for n,k in [('boss','boss_pct'),('field','field_pct'),('azmoth','coin_azmoth_pct'),('other_coin','coin_other_pct'),('etc','other_pct')]]))),'original_826_rmse_pp':float(np.sqrt(loss(826.))),'note':'Post-result intercept fit on official 2410 shares; not an independent validation. A common y0 and included sources are assumptions.','bar_source':bridges}
(O/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
assert len(bridges)>=6
