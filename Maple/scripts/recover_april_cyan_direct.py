"""Direct light-cyan detection; preserve overlap with dark coin as unresolved."""
from pathlib import Path
import numpy as np,pandas as pd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];D=R/'data/total_ratio_exact_thursday_20260913'
a=np.asarray(Image.open(R/'assets/sources/20250410/production_by_source.jpg').convert('RGB'),dtype=int)
old=pd.read_csv(R/'data/now_20250410_overlay_v2/digitized_overlay.csv')
rows=[]
for x in range(1080,1263):
    col=a[700:810,x]
    mask=(col[:,0]>145)&(col[:,0]<240)&(col[:,1]-col[:,0]>13)&(col[:,2]-col[:,0]>20)&(col[:,2]-col[:,1]>3)
    ys=np.where(mask)[0]+700
    dark=float(np.interp(x,old.x_pixel,old.other_coin_y))
    independent=ys[ys<dark-8]
    cy=float(np.median(independent)) if len(independent) else np.nan
    rows.append(dict(x=x,light_cyan_y=cy,dark_coin_y=dark,independent_pixels=len(independent),status='independent' if np.isfinite(cy) else 'overlap_or_absent'))
d=pd.DataFrame(rows);d.to_csv(D/'cyan_direct_trace.csv',index=False)
fig,ax=plt.subplots(figsize=(13,5),layout='constrained');ax.imshow(a.astype('uint8'))
ax.scatter(d.x,d.light_cyan_y,s=5,c='#ef3e43',label='분리 검출 청색');ax.plot(d.x,d.dark_coin_y,c='#ffae00',lw=1,label='진한 주화')
ax.set_xlim(1075,1262);ax.set_ylim(810,690);ax.legend();fig.savefig(R/'figures/april_cyan_direct_trace.png',dpi=160)
print(d[d.x.isin([1085,1086,1087,1088,1090,1094,1097,1100])].to_string(index=False))
print('reliable',int(d.light_cyan_y.notna().sum()),'of',len(d))
