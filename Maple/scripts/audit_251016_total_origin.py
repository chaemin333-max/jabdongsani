"""Source-to-source diagnostic. Affine fits are diagnostics, not revised canonical data."""
from pathlib import Path
import json,calendar,hashlib
import numpy as np,pandas as pd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];O=R/'data/total_origin_audit_20260913';O.mkdir(parents=True,exist_ok=True)
rawp=R/'data/meso_total_production_raw_canonical.json';raw=json.loads(rawp.read_text(encoding='utf-8'))['total']
im=np.asarray(Image.open(R.parent/'251016 총메소.png').convert('RGB'),float)
# Calendar mapping from printed Jan/Jul tick centers, not peaks.
months=np.array([0,6,12,18,24,30]);xs=np.array([159,380,600,823,1045,1266]);slope,offset=np.polyfit(months,xs,1)
rows=[]
for x in range(150,1380,2):
    m=(x-offset)/slope
    patch=im[300:740,x-1:x+2];score=patch[:,:,0]-(patch[:,:,1]+patch[:,:,2])/2
    if 1145<=x<=1176:score[:210,:]=-1 # red vertical patch lettering, not data
    iy,ix=np.unravel_index(np.argmax(score),score.shape)
    if score[iy,ix]<35:continue
    rows.append(dict(x=x,y=iy+300,month=m,P=np.interp(m,raw['month_coordinate'],raw['index'])*6.495250069))
d=pd.DataFrame(rows)
# P=a*(-y)+b reveals which source height corresponds to stored P=0.
a,b=np.polyfit(-d.y,d.P,1);d['P_from_source_affine']=-a*d.y+b;d['error']=d.P_from_source_affine-d.P
d.to_csv(O/'original_total_pixels.csv',index=False)
v=pd.read_csv(R/'data/now_20250410_overlay_v2/digitized_overlay.csv');t=pd.to_datetime(v.date)
cal=(t>='2024-04-01')&(t<'2024-07-01');valid=v.sum_px.notna()
ca,cb=np.polyfit(v.loc[cal,'sum_px'],v.loc[cal,'canonical_total'],1)
v['affine_diagnostic']=ca*v.sum_px+cb
v['same_window_scalar']=np.median(v.loc[cal,'canonical_total']/v.loc[cal,'sum_px'])*v.sum_px
fit=[]
for label,mask in [('calibration',cal),('post_NEXT',t>='2025-01-01')]:
 for method in ['affine_diagnostic','same_window_scalar']:
    z=v.loc[mask&valid];fit.append(dict(window=label,method=method,MAPE_pct=float((z[method]/z.canonical_total-1).abs().mean()*100)))
v.to_csv(O/'affine_vs_scalar.csv',index=False)
result={'canonical_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),'total_image_size':[im.shape[1],im.shape[0]],'source_fit_a':a,'source_fit_b':b,'implied_source_zero_y':b/a,'source_fit_RMSE':float(np.sqrt(np.mean(d.error**2))),'source_fit_MAPE_pct':float((d.error/d.P).abs().mean()*100),'april_calibration_affine_slope':ca,'april_calibration_affine_intercept':cb,'april_effective_zero_if_five_components':826+cb/(5*ca),'metrics':fit,'warning':'Post-result affine sensitivity; no new OOS claim; total image has no visible zero tick; this does not establish true zero.'}
(O/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
fig,ax=plt.subplots(figsize=(14,6));ax.imshow(im.astype('uint8'));ax.scatter(d.x,d.y,s=3,c='#00aaff');ax.axhline(b/a,c='#bb33cc',ls='--',label='P=0 implied by stored canonical');ax.set_xlim(120,1400);ax.set_ylim(810,270);ax.legend();fig.savefig(R/'figures/total_251016_source_pixel_audit.png',dpi=150)
