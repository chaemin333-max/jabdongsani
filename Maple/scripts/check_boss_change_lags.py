from pathlib import Path
import json
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/four_boss_change_alignment'
s={n:pd.read_csv(D/(n+'_series.csv'),parse_dates=['date']) for n in ['2311','2504','2510','2609']}
out=[]
for a,b in [('2311','2504'),('2311','2510'),('2504','2510'),('2504','2609'),('2510','2609')]:
 for lag in range(-3,4):
    x=s[a];y=s[b].copy();y.date+=pd.Timedelta(weeks=lag)
    lo=max(x.date.min(),y.date.min());hi=min(x.date.max(),y.date.max())
    grid=pd.date_range(lo.ceil('D'),hi.floor('D'),freq='7D')
    if len(grid)<5:continue
    nx=grid.as_unit('ns').astype('int64')
    xv=np.interp(nx,x.date.astype('datetime64[ns]').astype('int64'),x.indicator)
    yv=np.interp(nx,y.date.astype('datetime64[ns]').astype('int64'),y.indicator)
    dx=np.diff(xv);dy=np.diff(yv)
    def supported(source):
        days=source.date.astype('datetime64[ns]').astype('int64').to_numpy()
        q=nx.to_numpy();j=np.searchsorted(days,q)
        before=np.where(j>0,q-days[np.maximum(j-1,0)],np.iinfo('int64').max)
        after=np.where(j<len(days),days[np.minimum(j,len(days)-1)]-q,np.iinfo('int64').max)
        return np.minimum(before,after)<=pd.Timedelta(days=7).value
    adj=(supported(x)&supported(y));adj=adj[1:]&adj[:-1]
    for span in [1,3]:
        xx=pd.Series(dx).where(adj).rolling(span,center=True,min_periods=span).mean().dropna()
        yy=pd.Series(dy).where(adj).rolling(span,center=True,min_periods=span).mean().dropna()
        both=xx.index.intersection(yy.index);xx=xx.loc[both].to_numpy();yy=yy.loc[both].to_numpy()
        if len(xx)<3:continue
        out.append(dict(pair=a+'_'+b,lag_weeks=lag,smoothing_weeks=span,n=len(xx),change_corr=float(np.corrcoef(xx,yy)[0,1])))
d=pd.DataFrame(out);d.to_csv(D/'lag_sensitivity.csv',index=False)
print(d[(d.lag_weeks==0)&(d.smoothing_weeks==3)].to_string(index=False))
print(d[(d.smoothing_weeks==3)].sort_values('change_corr').groupby('pair').tail(1).to_string(index=False))
