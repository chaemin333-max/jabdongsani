from pathlib import Path
import numpy as np,pandas as pd
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'data/total_ratio_exact_thursday_20260913'
a=np.asarray(Image.open(R/'assets/sources/20250410/production_by_source.jpg').convert('RGB'),dtype=int)
rows=[]
for x in range(1070,1120):
    col=a[725:810,x]
    mask=(col[:,0]>145)&(col[:,0]<240)&(col[:,1]-col[:,0]>13)&(col[:,2]-col[:,0]>20)&(col[:,2]-col[:,1]>3)
    ys=np.where(mask)[0]+725
    rows.append(dict(x=x,candidate_y=float(np.median(ys)) if len(ys) else np.nan,count=len(ys),minimum_y=int(ys.min()) if len(ys) else np.nan,maximum_y=int(ys.max()) if len(ys) else np.nan))
d=pd.DataFrame(rows);d.to_csv(D/'cyan_candidates_around_azmoth.csv',index=False)
print(d[d.x.isin([1085,1086,1087,1088,1090,1094,1097,1100,1105])].to_string(index=False))
