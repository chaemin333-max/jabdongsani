"""Put four increment series in arbitrary October-2025 pixel-equivalent units."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
R=Path(__file__).resolve().parents[1];D=R/'data/four_boss_change_alignment'
series={n:pd.read_csv(D/(n+'_series.csv'),parse_dates=['date']) for n in ['2311','2504','2510','2609']}
ref=series['2510'];metric=pd.read_csv(D/'pairwise_change_metrics.csv').set_index('pair')
out=[]
for name,s in series.items():
    if name=='2510':scale=1.;offset=0.
    else:
        pair='2510_2609' if name=='2609' else name+'_2510'
        scale=1/metric.loc[pair,'difference_scale_k'] if name=='2609' else metric.loc[pair,'difference_scale_k']
        left=max(s.date.min(),ref.date.min());right=min(s.date.max(),ref.date.max())
        grid=pd.date_range(left.ceil('D'),right.floor('D'),freq='7D')
        xi=np.interp(grid.as_unit('ns').astype('int64'),s.date.astype('datetime64[ns]').astype('int64'),s.indicator)
        yi=np.interp(grid.as_unit('ns').astype('int64'),ref.date.astype('datetime64[ns]').astype('int64'),ref.indicator)
        offset=float(np.median(yi-scale*xi))
    z=s.copy();z['source']=name;z['scale_from_overlap_differences']=scale;z['offset_from_overlap_median']=offset;z['aligned_2510_pixel_equivalent']=scale*z.indicator+offset;out.append(z)
a=pd.concat(out,ignore_index=True);a.to_csv(D/'aligned_curves.csv',index=False)
for f in (R/'assets/fonts').glob('NotoSansKR*.ttf'):font_manager.fontManager.addfont(str(f))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False})
fig,ax=plt.subplots(figsize=(14,6),layout='constrained')
for name,z in a.groupby('source'):
    ax.plot(z.date,z.aligned_2510_pixel_equivalent,label=name,lw=2,alpha=.85)
ax.set_ylabel('2510의 목표 구간 픽셀 상당량 (임의 기준선)')
ax.set_title('주간 변화량으로 배율 맞춤 · 겹친 구간 중앙값으로 수직 위치 맞춤')
ax.grid(alpha=.2);ax.legend()
fig.savefig(R/'figures/four_boss_change_alignment.png',dpi=170)
print(a.groupby('source')[['scale_from_overlap_differences','offset_from_overlap_median']].first().to_string())
