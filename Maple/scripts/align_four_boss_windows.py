"""Compare shared low/high boss boundary in four NOW source charts."""
from pathlib import Path
import json,hashlib,os
import numpy as np,pandas as pd
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'data/four_boss_window_alignment';O.mkdir(exist_ok=True)
imgpath=R/'assets/sources/four_now_originals/250410 보스구간별.png'
a=np.asarray(Image.open(imgpath).convert('RGB'),float)
rows=[]
for x in np.arange(133+float(os.environ.get('BOSS_X_SHIFT','0')),954,7.96):
    ix=round(x);rgb=np.median(a[330:764,ix-1:ix+2],axis=1)
    sat=(rgb.max(1)-rgb.min(1)>14)&(rgb.mean(1)<247)
    ys=np.where(sat)[0]+330
    if len(ys)<20:continue
    top=int(ys.min())
    dark=(rgb[:,1]<180)&(rgb[:,2]<215)&(rgb[:,2]>rgb[:,0]+8)
    light=(rgb[:,1]>=180)&(rgb[:,1]<225)&(rgb[:,2]>215)&(rgb[:,2]>rgb[:,0]+8)
    transition=None
    for y in range(max(top+8,350),740):
        i=y-330
        if light[i:i+5].sum()>=4 and dark[max(0,i-8):i].sum()>=4:
            transition=y;break
    if transition is None:continue
    # First visible bar aligns to the week of 2023-03-30, last to 2025-03-27.
    # Printed Mar labels sit below those weeks, not at the first pixel as dates.
    dt=pd.Timestamp('2023-03-30')+pd.Timedelta(days=(x-133)*7/7.96)
    rows.append(dict(date=dt,top_y=top,low_boundary_y=transition,baseline_y=764,low_px=transition-top,high_px=764-transition,total_px=764-top))
ap=pd.DataFrame(rows);ap['low_share']=ap.low_px/ap.total_px;ap.to_csv(O/'2504_pixels.csv',index=False)
old=pd.read_csv(R/'data/tier_regression_audit/official_20251016_pixels.csv')
old['low_px']=old.old_tier1_pixels+old.old_tier2_pixels
old['high_px']=old[[f'old_tier{i}_pixels' for i in range(3,7)]].sum(axis=1)
old['total_px']=old.low_px+old.high_px;old['low_share']=old.low_px/old.total_px
old.to_csv(O/'2510_low_high.csv',index=False)
new=pd.read_csv(R/'data/now_20260910/boss_tier_weekly.csv')
new['low_px']=new.tier1_raw
new['high_px']=new[[f'tier{i}_raw' for i in range(2,8)]].sum(axis=1)
new['total_px']=new.low_px+new.high_px;new['low_share']=new.low_px/new.total_px
new.to_csv(O/'2609_low_high.csv',index=False)
series={'2504':ap,'2510':old,'2609':new};pairs=[];details=[]
for l,r in [('2504','2510'),('2504','2609'),('2510','2609')]:
    x=series[l][['date','low_share','low_px','high_px','total_px']].copy()
    y=series[r][['date','low_share','low_px','high_px','total_px']].copy()
    x.date=pd.to_datetime(x.date);y.date=pd.to_datetime(y.date)
    z=pd.merge_asof(x.sort_values('date'),y.sort_values('date'),on='date',direction='nearest',tolerance=pd.Timedelta(days=4),suffixes=('_'+l,'_'+r)).dropna()
    z['difference_pp']=100*(z['low_share_'+l]-z['low_share_'+r]);z['pair']=l+'_'+r
    if len(z):
        pairs.append(dict(pair=l+'_'+r,n=len(z),start=str(z.date.min().date()),end=str(z.date.max().date()),MAE_pp=z.difference_pp.abs().mean(),median_bias_pp=z.difference_pp.median(),max_abs_pp=z.difference_pp.abs().max()))
        details.append(z)
pd.DataFrame(pairs).to_csv(O/'pair_summary.csv',index=False)
pd.concat(details).to_csv(O/'pair_details.csv',index=False)
pd.DataFrame([
    dict(source='2311',measurement='five unstacked boss group lines',low_high_numeric=False,reason='Hard Suu not separately named; zero and scale not printed'),
    dict(source='2504',measurement='four stacked tier groups',low_high_numeric=True,reason=''),
    dict(source='2510',measurement='six stacked tier groups',low_high_numeric=True,reason=''),
    dict(source='2609',measurement='seven stacked tier groups',low_high_numeric=True,reason='')
]).to_csv(O/'availability.csv',index=False)
summary={'status':'THREE_STACKED_CHARTS_NUMERIC_2311_TAXONOMY_OPEN','pair_summary':pairs,'2504_bar_count':len(ap),'source_hashes':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [imgpath,R/'data/tier_regression_audit/official_20251016_pixels.csv',R/'data/now_20260910/boss_tier_weekly.csv']},'warning':'Source-specific stacked-bar shares; not common absolute meso scale. 2311 lacks identifiable Hard Suu allocation.'}
(O/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary));assert len(pairs)==3
