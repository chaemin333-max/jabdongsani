import pandas as pd,numpy as np,json,calendar
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];d=pd.read_csv(R/'data/now_20250410_overlay/digitized_overlay.csv');t=pd.to_datetime(d.date)
raw=json.loads((R/'data/meso_total_production_raw_canonical.json').read_text(encoding='utf-8'))['total']
def total(dates):
    m=[(z.year-2023)*12+z.month-1+(z.day-1+z.hour/24)/calendar.monthrange(z.year,z.month)[1] for z in dates]
    return np.interp(m,raw['month_coordinate'],raw['index'])*6.495250069
out=[]
for shift in [-14,-7,0,7,14]:
 for zero in [-2,0,2]:
    ts=t+pd.Timedelta(days=shift);p=total(ts)
    h=d.sum_px+zero*5;cal=(ts>='2024-04-01')&(ts<'2024-07-01');k=np.nanmedian(p[cal]/h[cal]);err=k*h/p-1;post=ts>='2025-01-01'
    out.append(dict(date_shift_days=shift,zero_shift_px=zero,post_NEXT_bias_pct=float(np.nanmedian(err[post])*100),post_NEXT_MAPE_pct=float(np.nanmean(abs(err[post]))*100)))
print(pd.DataFrame(out).to_string(index=False))
for ds in ['2024-09-17','2024-10-22','2025-03-20']:
    i=np.argmin(abs(t-pd.Timestamp(ds)));r=d.iloc[i];print(ds,{n:round(r[n+'_px']/r.sum_px*100,2) for n in ['boss','field','azmoth','other_coin','etc']})
im=np.array(Image.open(R/'assets/sources/20250410/production_by_source.jpg').convert('RGB'))
for x in [950,1150,1250]:
 print('column',x,[(y,im[y,x].tolist()) for y in range(814,830)])
pd.DataFrame(out).to_csv(R/'data/now_20250410_overlay/axis_sensitivity.csv',index=False)
sub=[]
for component in ['none','boss','field','azmoth','other_coin','etc']:
    v=d.read_total if component=='none' else d.read_total-d[component+'_index']
    for label,mask in [('post_NEXT',t>='2025-01-01'),('azmoth_pre_NEXT',(t>='2024-10-17')&(t<'2024-12-19'))]:
        err=v[mask]/d.canonical_total[mask]-1
        sub.append(dict(component_removed=component,window=label,MAPE_pct=float(err.abs().mean()*100),median_bias_pct=float(err.median()*100)))
print(pd.DataFrame(sub).to_string(index=False))
pd.DataFrame(sub).to_csv(R/'data/now_20250410_overlay/component_diagnostic.csv',index=False)
