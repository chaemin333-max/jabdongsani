"""Compare week-to-week boss tier changes without assuming image y=0."""
from pathlib import Path
import json,hashlib
from itertools import combinations
import numpy as np,pandas as pd
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'data/four_boss_change_alignment';O.mkdir(parents=True,exist_ok=True)
# 2311 dark-blue Hard Damien through Hard Jin Hilla (Hard Suu included per user assumption).
im=np.asarray(Image.open(R/'assets/sources/four_now_originals/231116_보스구간별생산.png').convert('RGB'),dtype=int)
rows=[]
for x in range(94,1654,7):
    col=im[590:1100,x-1:x+2]
    score=col[:,:,2]-col[:,:,0]
    iy,ix=np.unravel_index(np.argmax(score),score.shape)
    if score[iy,ix]<65:continue
    dt=pd.Timestamp('2023-04-01')+pd.Timedelta(days=(x-94)*214/1560)
    rows.append(dict(source='2311',date=dt,pixel_x=x,pixel_y=590+iy,indicator=-(590+iy)))
nov=pd.DataFrame(rows);nov.to_csv(O/'2311_line_pixels.csv',index=False)
# 2504 light-violet stacked band = Hard Suu through Hard Black Mage.
ap=pd.read_csv(R/'data/four_boss_window_alignment/2504_pixels.csv',parse_dates=['date'])
bar=np.asarray(Image.open(R/'assets/sources/four_now_originals/250410 보스구간별.png').convert('RGB'),dtype=int)
aprows=[]
for r in ap.itertuples():
    x=round(133+(r.date-pd.Timestamp('2023-03-30')).total_seconds()/86400*7.96/7)
    col=np.median(bar[round(r.low_boundary_y):764,x-1:x+2],axis=1)
    red=(col[:,0]-col[:,1]>35)&(col[:,1]<195)&(col[:,2]>col[:,1]+4)
    candidates=np.where(red)[0]
    lower=round(r.low_boundary_y)+int(candidates[0]) if len(candidates) else 764
    if lower<=r.low_boundary_y+5:continue
    aprows.append(dict(source='2504',date=r.date,pixel_x=x,pixel_y=lower,indicator=lower-r.low_boundary_y,light_top_y=r.low_boundary_y))
apr=pd.DataFrame(aprows);apr.to_csv(O/'2504_hardsuu_band_pixels.csv',index=False)
octo=pd.read_csv(R/'data/tier_regression_audit/official_20251016_pixels.csv',parse_dates=['date'])
octo=pd.DataFrame(dict(source='2510',date=octo.date,indicator=octo.old_tier3_pixels))
sep=pd.read_csv(R/'data/now_20260910/boss_tier_weekly.csv',parse_dates=['date'])
sep=pd.DataFrame(dict(source='2609',date=sep.date,indicator=sep.tier2_raw))
series={'2311':nov,'2504':apr,'2510':octo,'2609':sep}
for name,s in series.items():s[['date','indicator']].to_csv(O/(name+'_series.csv'),index=False)
pairrows=[];aligned=[]
for left,right in combinations(series,2):
    x=series[left][['date','indicator']].sort_values('date').rename(columns={'indicator':'left'})
    y=series[right][['date','indicator']].sort_values('date').rename(columns={'indicator':'right'})
    # Weekly grid, interpolation only within the available plotted range.
    start=max(x.date.min(),y.date.min());end=min(x.date.max(),y.date.max())
    if start>=end:continue
    grid=pd.date_range(start.ceil('D'),end.floor('D'),freq='7D')
    if len(grid)<3:continue
    xi=np.interp(grid.as_unit('ns').astype('int64'),x.date.astype('datetime64[ns]').astype('int64'),x.left)
    yi=np.interp(grid.as_unit('ns').astype('int64'),y.date.astype('datetime64[ns]').astype('int64'),y.right)
    def supported(source):
        days=source.date.astype('datetime64[ns]').astype('int64').to_numpy()
        q=grid.as_unit('ns').astype('int64').to_numpy()
        j=np.searchsorted(days,q)
        before=np.where(j>0,q-days[np.maximum(j-1,0)],np.iinfo('int64').max)
        after=np.where(j<len(days),days[np.minimum(j,len(days)-1)]-q,np.iinfo('int64').max)
        return np.minimum(before,after)<=pd.Timedelta(days=7).value
    valid=supported(x)&supported(y)
    adjacent=valid[1:]&valid[:-1]
    dx=np.diff(xi)[adjacent];dy=np.diff(yi)[adjacent]
    # Shape matching uses only differences. k is not a physical meso scale.
    k=float(np.dot(dx,dy)/np.dot(dx,dx)) if np.dot(dx,dx)>0 else np.nan
    corr=float(np.corrcoef(dx,dy)[0,1]) if len(dx)>2 else np.nan
    same=float(np.mean(np.sign(dx)==np.sign(dy)))
    rmse=float(np.sqrt(np.mean((k*dx-dy)**2)))
    span=float(np.percentile(yi,90)-np.percentile(yi,10))
    pairrows.append(dict(pair=left+'_'+right,start=str(grid[0].date()),end=str(grid[-1].date()),weeks=len(grid),difference_pairs=len(dx),difference_scale_k=k,weekly_change_correlation=corr,same_direction_fraction=same,RMSE_in_right_image_pixels=rmse,RMSE_over_right_10_90_span_pct=100*rmse/span if span>0 else np.nan))
    aligned.extend(dict(pair=left+'_'+right,date=str(d.date()),left=xv,right=yv,left_delta=lx,right_delta=ry) for d,xv,yv,lx,ry in zip(grid[1:][adjacent],xi[1:][adjacent],yi[1:][adjacent],dx,dy))
pd.DataFrame(pairrows).to_csv(O/'pairwise_change_metrics.csv',index=False)
pd.DataFrame(aligned).to_csv(O/'aligned_weekly_differences.csv',index=False)
summary={'status':'PIXEL_CHANGE_ONLY_NO_ZERO_ASSUMPTION','mapping':{'2311':'Hard Damien-Hard Jin Hilla; Hard Suu assigned here by user assumption','2504':'Hard Suu-Hard Black Mage proxy for requested tier; includes above Hard Jin Hilla','2510':'Hard Damien-Hard Jin Hilla; Hard Suu assigned here by user assumption','2609':'Hard Suu-Hard Jin Hilla'},'pairs':pairrows,'warning':'Change correlations do not establish equal level, zero, or category scope. 2504 includes bosses through Black Mage. Weekly grids interpolate pixel observations.'}
(O/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary));assert len(pairrows)>=4
