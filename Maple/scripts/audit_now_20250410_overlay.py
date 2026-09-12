"""Independent image reading; one early scale calibration, later holdout shape audit."""
from pathlib import Path
import calendar,json,hashlib
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
R=Path(__file__).resolve().parents[1];O=R/'data/now_20250410_overlay';O.mkdir(exist_ok=True)
src=R/'assets/sources/20250410/production_by_source.jpg'
im=np.asarray(Image.open(src).convert('RGB'),float)
rawpath=R/'data/meso_total_production_raw_canonical.json'
raw=json.loads(rawpath.read_text(encoding='utf-8'))['total']
# Interior month tick centers; edge labels and event arrows are not date anchors.
# Month coordinate: Jan 2023 = 0. Tick positions manually read from the original image.
mx=np.array([3,7,11,15,19,23]);px=np.array([474,606,738,870,1003,1135])
coef=np.polyfit(mx,px,1)
names=['boss','field','azmoth','other_coin','etc']
palette=np.array([[191,75,84],[229,145,164],[179,215,225],[35,76,105],[168,171,168]])
rows=[]
for x in range(368,1263,3):
    month=(x-coef[1])/coef[0];year=2023+int(np.floor(month))//12;mo=int(np.floor(month))%12+1
    day=1+(month-np.floor(month))*calendar.monthrange(year,mo)[1]
    ds=pd.Timestamp(year,mo,1)+pd.Timedelta(days=float(day-1))
    if ds>pd.Timestamp('2025-04-09'):continue
    v={}
    for n,c,(lo,hi) in zip(names,palette,[(305,745),(650,799),(710,823),(705,823),(814,829)]):
        # Choose color-best original pixel, not a median that erases sloped thin lines.
        patch=im[lo:hi+1,x-1:x+2];dist=np.linalg.norm(patch-c,axis=2)
        if n=='field':dist[(patch[:,:,0]<205)|(patch[:,:,1]<110)|(patch[:,:,2]<=patch[:,:,1])]=1e6
        if n=='azmoth':dist[(patch.mean(2)<165)|(patch[:,:,2]-patch[:,:,0]<8)]=1e6
        if n=='other_coin':dist[(patch.mean(2)>170)|(patch[:,:,2]-patch[:,:,0]<25)]=1e6
        iy,ix=np.unravel_index(np.argmin(dist),dist.shape)
        v[n+'_y']=lo+iy;v[n+'_distance']=float(dist[iy,ix])
        v[n+'_px']=max(0,826-lo-iy) if dist[iy,ix]<85 else np.nan
        if n=='azmoth' and ds<pd.Timestamp('2024-10-17'):v[n+'_px']=0
        if n=='other_coin' and ds<pd.Timestamp('2024-02-22'):v[n+'_px']=0
    rows.append(dict(date=ds.isoformat(),month_coordinate=month,x_pixel=x,**v))
d=pd.DataFrame(rows)
for n in names:d[n+'_px']=d[n+'_px'].interpolate(limit=2,limit_area='inside')
d['sum_px']=d[[n+'_px' for n in names]].sum(axis=1,min_count=5)
d['canonical_total']=np.interp(d.month_coordinate,raw['month_coordinate'],raw['index'])*6.495250069
# Use only 2024 Apr-Jun for unit conversion; never fit the holdout to the red curve.
dates=pd.to_datetime(d.date)
cal=(dates>='2024-04-01')&(dates<'2024-07-01')&d.sum_px.notna()
k=float(np.median(d.loc[cal,'canonical_total']/d.loc[cal,'sum_px']))
d['read_total']=d.sum_px*k
for n in names:d[n+'_index']=d[n+'_px']*k
d['relative_error']=d.read_total/d.canonical_total-1
d['window']=np.where(cal,'scale_calibration',np.where(dates>='2024-07-01','forward_holdout','earlier_comparison'))
d.to_csv(O/'digitized_overlay.csv',index=False)
summ=[]
for label,g in d.dropna(subset=['read_total']).groupby('window'):
    summ.append(dict(window=label,n_pixels=len(g),MAPE_pct=float(g.relative_error.abs().mean()*100),median_bias_pct=float(g.relative_error.median()*100)))
pd.DataFrame(summ).to_csv(O/'comparison_summary.csv',index=False)
manifest={'scale':k,'scale_window':'2024-04-01 through 2024-06-30','forward_holdout':'2024-07-01 onward','date_calibration':'linear mapping from six interior printed month tick centers; no curve-fitting date shift','month_ticks':mx.tolist(),'pixel_ticks':px.tolist(),'zero_y':826,'important':'independent image holdout, not a forecast OOS; canonical provenance may share official history; source scope incl. Ursus unresolved','hashes':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,rawpath]},'metrics':summ}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for f in (R/'assets/fonts').glob('NotoSansKR*.ttf'):font_manager.fontManager.addfont(str(f))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False})
fig=plt.figure(figsize=(20,11.25),dpi=160,facecolor='#bfeeed')
for xy,w,h,color,rounding in [((.025,.095),.95,.81,'#05bce7',.020),((.031,.107),.938,.772,'#ffdc32',.010),((.037,.115),.926,.756,'white',.005)]:
    fig.add_artist(FancyBboxPatch(xy,w,h,boxstyle=f'round,pad=.006,rounding_size={rounding}',transform=fig.transFigure,fc=color,ec='#14353b',lw=2,zorder=0))
reference=plt.imread(R.parent/'총메소생산.png');art=reference[220:405,125:1015]
ta=fig.add_axes([.043,.765,.29,.29*(20/11.25)*art.shape[0]/art.shape[1]],zorder=3);ta.imshow(art);ta.axis('off')
ax=fig.add_axes([.078,.205,.674,.405],zorder=2)
daily=pd.date_range('2023-01-01','2026-08-20');m=np.array([(z.year-2023)*12+z.month-1+(z.day-1)/calendar.monthrange(z.year,z.month)[1] for z in daily])
ax.plot(daily,np.interp(m,raw['month_coordinate'],raw['index'])*6.495250069,color='#fa3044',lw=3,label='기존 총생산 정본')
ax.plot(dates,d.read_total,color='#087bea',lw=2,ls='--',label='250410 생산처 합계')
ax.axvspan(pd.Timestamp('2024-04-01'),pd.Timestamp('2024-07-01'),color='#fff2bf',alpha=.6,label='단위 보정 구간')
ax.set_xlim(pd.Timestamp('2023-01-01'),pd.Timestamp('2026-08-28'));ax.set_ylim(0,1400);ax.set_yticks(np.arange(0,1401,200))
import matplotlib.dates as md
ax.xaxis.set_major_locator(md.MonthLocator(bymonth=[1,4,7,10]));ax.xaxis.set_major_formatter(md.DateFormatter('%y.%m'))
ax.grid(color='#e3edf0',lw=.85);ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False);ax.spines[['left','bottom']].set_color('#a4b8bf');ax.tick_params(colors='#455e6b',labelsize=12,length=0,pad=12)
ax.legend(loc='upper left',bbox_to_anchor=(1.04,1.04),frameon=False,fontsize=12)
for ds,name,col in [('2023-06-15','NEW AGE','#087bea'),('2024-10-17','아즈모스 도입','#319c9d'),('2024-12-19','NEXT','#087bea')]:
    dt=pd.Timestamp(ds);ax.axvline(dt,color=col,lw=1,ls=(0,(5,5)),alpha=.7);ax.text(dt,1.20 if name=='NEXT' else 1.035,name+'\n'+dt.strftime('%y.%m.%d'),transform=ax.get_xaxis_transform(),ha='center',va='bottom',fontsize=12,color=col,fontweight='bold')
fig.text(.078,.144,'NEW AGE 총생산 = 100',fontsize=12,color='#455e6b');fig.text(.795,.45,'250410은 생산처별 선의 합계\n주별 비율로 정본에 강제 정렬하지 않음',fontsize=11,color='#455e6b')
fig.savefig(R/'figures/total_20250410_overlay.png')
# Pixel QA preserves the real source image with extracted coordinates.
fig2,qa=plt.subplots(figsize=(16,8));qa.imshow(im.astype('uint8'))
for n in names:qa.scatter(d.x_pixel,d[n+'_y'],s=3,label=n)
qa.set_xlim(320,1300);qa.set_ylim(860,270);qa.legend();fig2.savefig(R/'figures/now_20250410_pixel_qa.png',dpi=150)
print(json.dumps(manifest))
assert k>0 and len(summ)==3
assert hashlib.sha256(rawpath.read_bytes()).hexdigest()==manifest['hashes'][str(rawpath.relative_to(R))]
if __name__=='__main__':pass
