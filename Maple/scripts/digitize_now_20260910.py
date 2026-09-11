"""Digitize the three user-supplied NOW slides; no generative image tools.

Keep measured pixels and explicitly rate-constrained versions separately.
The bar calendar is anchored on Aug 21 2025 / Aug 20 2026 (52 weeks).
"""
import csv,json,hashlib
from datetime import date,timedelta
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.optimize import minimize

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'Maple/assets/sources/20260910'
OUT=ROOT/'Maple/data/now_20260910'
TIERS=['하드 스우 미만','하드 스우 ~ 하드 진 힐라','노멀 세렌 ~ 하드 세렌',
       '이지 카링 ~ 익스트림 스우','노멀 흉성 ~ 노멀 림보','익스트림 세렌 ~ 하드 림보','하드 벨로나 이상']
RATES=np.array([.40,.98,4.03,8.24,10.73,16.83])
COUNT_RATES=np.array([.63,.73,2.44,2.71,2.53,9.94])

def write(name,rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)

def rgb(name):return np.array(Image.open(SRC/name).convert('RGB'),dtype=float)

def chroma(p):
    return (p-p.min(axis=-1,keepdims=True))/np.maximum(np.ptp(p,axis=-1,keepdims=True),1.)

def stack_profile(im,x,bottom,top_limit,palette):
    x=int(round(x));col=np.mean(im[top_limit:bottom+1,max(0,x-1):x+2],axis=1)
    sat=np.ptp(col,axis=-1)/np.maximum(col.max(-1),1)
    # Start at the base and stop after an uncolored gap above the actual bar.
    yy=np.flatnonzero(sat>.15)
    if not len(yy):raise ValueError('No colored bar')
    last=yy[-1];first=last;gap=0
    for y in range(last,-1,-1):
        if sat[y]>.15:gap=0;first=y
        else:
            gap+=1
            if gap>=4:break
    p=col[first:last+1][::-1]
    costs=np.sum((chroma(p)[:,None,:]-chroma(palette)[None,:,:])**2,axis=-1)
    # Ordered dynamic programming, bottom low tier -> top high tier.
    n,k=costs.shape;dp=np.full((n,k),np.inf);prev=np.zeros((n,k),int);dp[0]=costs[0]
    for i in range(1,n):
        for j in range(k):
            ix=np.argmin(dp[i-1,:j+1]);dp[i,j]=dp[i-1,ix]+costs[i,j];prev[i,j]=ix
    labels=np.empty(n,int);labels[-1]=np.argmin(dp[-1])
    for i in range(n-1,0,-1):labels[i-1]=prev[i,labels[i]]
    heights=np.bincount(labels,minlength=k).astype(float)
    return heights,top_limit+first,top_limit+last

def digitize_bars():
    im=rgb('boss_production_by_tier.png')
    palette=np.array([np.median(im[y-2:y+3,846:851],axis=(0,1)) for y in [360,377,395,412,430,447,465]])
    dates=[date(2026,8,20)-timedelta(weeks=104-i) for i in range(105)]
    centers=np.linspace(141.5,813.5,105); heights=[];raw=[]
    for d,x in zip(dates,centers):
        # Choose a bar interior near the calibrated grid, avoiding white inter-bar gaps.
        candidates=[int(round(x))+v for v in [-1,0,1]]
        xx=max(candidates,key=lambda xx:np.mean(np.ptp(im[640:662,xx],axis=-1)))
        h,top,bottom=stack_profile(im,xx,665,344,palette);heights.append(h)
        for j in range(7):raw.append(dict(date=d.isoformat(),tier=j+1,label=TIERS[j],x_pixel=xx,
                                        height_pixels=h[j],stack_top_y=top,stack_bottom_y=bottom))
    h=np.array(heights);cal=h.copy();old=dates.index(date(2025,8,21));new=104;checks=[]
    for j,r in enumerate(RATES):
        a,b=h[old,j],h[new,j]
        # Equal pixel-error weighted least adjustment, y_new = r*y_old.
        a_fit=(a+r*b)/(1+r*r);b_fit=r*a_fit
        cal[old,j]=a_fit;cal[new,j]=b_fit
        checks.append(dict(tier=j+1,label=TIERS[j],reference_date='2025-08-21',comparison_date='2026-08-20',
                           official_change_pct=int(round((r-1)*100)),official_multiplier=r,old_raw_pixels=a,new_raw_pixels=b,
                           raw_multiplier=b/a if a else '',old_constrained_pixels=a_fit,new_constrained_pixels=b_fit,
                           old_adjustment_pixels=a_fit-a,new_adjustment_pixels=b_fit-b))
    with (ROOT/'Maple/data/maple_production_calibration_inputs_weekly.csv').open() as f:panel={r['date']:r for r in csv.DictReader(f)}
    obs=np.array([float(panel[d.isoformat()]['B_boss_newage100'])*6.495250069 for d in dates])
    scale=float(np.median(obs/cal.sum(1)))  # shared vertical scale only; never reshape to old curve
    rows=[]
    for i,d in enumerate(dates):
        row=dict(date=d.isoformat(),x_pixel=float(centers[i]),B_existing_weekly=obs[i],
                 B_digitized_raw=h[i].sum()*scale,B_digitized_constrained=cal[i].sum()*scale)
        for j in range(7):
            row[f'tier{j+1}_raw']=h[i,j]*scale;row[f'tier{j+1}']=cal[i,j]*scale
        rows.append(row)
    write('boss_tier_pixels.csv',raw);write('boss_tier_weekly.csv',rows);write('official_boss_production_growth.csv',checks)
    return dict(bar_count=105,first_date=str(dates[0]),last_date=str(dates[-1]),palette=palette.tolist(),
                index_per_pixel=scale,median_abs_relative_to_existing=float(np.median(abs(cal.sum(1)*scale/obs-1))),
                max_endpoint_pixel_adjustment=max(abs(x['old_adjustment_pixels']) for x in checks),
                calendar='105 weekly bars; last 2026-08-20; Aug 21 2025 is bar 52; x=141.5..813.5'),dates,h,cal,palette

def digitize_distribution():
    im=rgb('solo_clear_distribution.png');palette=np.array([[94,116,252],[251,97,53],[0,180,148],
                                                          [173,115,254],[255,165,83],[0,193,245]],float)
    heights=np.array([stack_profile(im,x,736,303,palette)[0] for x in [380,610]])
    shares=heights/heights.sum(axis=1)[:,None]
    def objective(p):
        pred=COUNT_RATES*p/(COUNT_RATES@p)
        return np.sum((p-shares[0])**2)+np.sum((pred-shares[1])**2)
    fit=minimize(objective,shares[0],method='SLSQP',bounds=[(1e-9,1)]*6,
                 constraints={'type':'eq','fun':lambda x:x.sum()-1},options={'ftol':1e-14,'maxiter':1000})
    if not fit.success:raise RuntimeError(fit.message)
    p0=fit.x;growth=COUNT_RATES@p0;p1=COUNT_RATES*p0/growth
    out=[]
    for j in range(6):
        out.append(dict(tier=j+1,label=TIERS[j] if j<5 else '익스트림 세렌 이상',reference_date='2026-02-12',
                        comparison_date='2026-08-20',raw_share_reference=shares[0,j],raw_share_comparison=shares[1,j],
                        official_change_pct=int(round((COUNT_RATES[j]-1)*100)),official_multiplier=COUNT_RATES[j],
                        constrained_share_reference=p0[j],constrained_share_comparison=p1[j],
                        implied_population_growth_multiplier=growth,
                        interpretation='growth of tier counts; common total inferred from distribution bars'))
    write('solo_clear_distribution.csv',out)
    return dict(raw_heights=heights.tolist(),raw_shares=shares.tolist(),
                implied_total_multiplier=float(growth),max_share_adjustment_pp=float(np.max(abs(np.array([p0,p1])-shares))*100),
                interpretation='count-growth reading, not percentage-point changes; inferred common total is not a printed official number')

def digitize_sources():
    im=rgb('production_by_source.png'); names=['boss_rewards','field','serazar_coin','coin_exchange','other']
    palette=np.array([np.median(im[y-1:y+2,1165:1188],axis=(0,1)) for y in [342,364,386,410,435]])
    # Explicit ranges exclude labels. RGB matching retains uncertainty at crossings.
    xs=np.linspace(192,1130,53); ds=[date(2025,8,21)+timedelta(weeks=i) for i in range(53)]
    result=[]
    for d,x in zip(ds,xs):
        xx=int(round(x));col=np.median(im[333:715,xx-2:xx+3],axis=1)
        for j,name in enumerate(names):
            distances=np.linalg.norm(col-palette[j],axis=1)
            mask=distances<([85,50,75,40,28][j])
            # Measured per-series ROIs prevent a pale edge of the boss curve
            # from being misread as the field line, or an event dash as 'other'.
            lo,hi=[(333,650),(640,706),(694,714),(640,714),(704,714)][j]
            ys=np.arange(333,715);mask &= (ys>=lo)&(ys<=hi)
            # The gray series is visually buried in the zero-axis band.
            if j==4:mask[:]=False
            yy=np.flatnonzero(mask)
            if len(yy):
                best=yy[np.argmin(distances[yy])];close=yy[abs(yy-best)<=4]; y=float(np.median(close)+333);height=714-y
            else:y='';height=''
            result.append(dict(date=d.isoformat(),series=name,x_pixel=float(x),line_y_pixel=y,
                               height_from_zero_pixels=height,status='detected' if y!='' else 'below_resolution_at_axis' if j==4 else 'unresolved_overlap_or_zero',
                               height_upper_bound_pixels=3 if j==4 else '',
                               source='production_by_source.png'))
    # One scale tied to the already canonical weekly boss series, not a separate rescaling per source.
    with (ROOT/'Maple/data/maple_production_calibration_inputs_weekly.csv').open() as f:panel={r['date']:r for r in csv.DictReader(f)}
    ratios=[float(panel[r['date']]['B_boss_newage100'])*6.495250069/r['height_from_zero_pixels'] for r in result
            if r['series']=='boss_rewards' and r['height_from_zero_pixels']!='' and r['height_from_zero_pixels']>0]
    scale=float(np.median(ratios))
    for r in result:r['production_index']=r['height_from_zero_pixels']*scale if r['height_from_zero_pixels']!='' else ''
    write('production_by_source_weekly.csv',result)
    return dict(palette=palette.tolist(),index_per_pixel=scale,records=len(result),
                unresolved=sum(r['status']!='detected' for r in result),baseline_y=714)

def windows_and_assumptions():
    rows=[]
    settings=[('2024-12-19','2025-01-16','2025-05-22',2,3,None,'none','761'),
              ('2025-06-19','2025-07-17','2025-11-20',3,3,4,'none','773'),
              ('2025-12-18','2026-01-15','2026-04-16',3,3,11,'Kai','790'),
              ('2026-06-18','2026-07-23','2026-09-17',4,4,4,'Meirin; Kai reopens','805')]
    for i,(start,leap,end,dominant,cap,weeks,boss,ref) in enumerate(settings):
        rows.append(dict(season=i+1,start=start,first_leap=leap,no_leap_end=(date.fromisoformat(leap)-timedelta(days=1)).isoformat(),
                         season_end=end,no_leap_days=(date.fromisoformat(leap)-date.fromisoformat(start)).days,
                         dominant_or_challenger_tier=dominant,production_support_cap_tier=cap,
                         liberation_weeks_user_assumption=weeks if weeks else '',season_boss=boss,
                         official_schedule_url=f'https://maplestory.nexon.com/news/update/{ref}',
                         interpretation='schedule official; productivity caps and stable pre-leap main low tiers are user model assumptions'))
    write('season_identification_windows.csv',rows)

def main():
    OUT.mkdir(exist_ok=True,parents=True)
    bars,*_=digitize_bars();dist=digitize_distribution();sources=digitize_sources();windows_and_assumptions()
    manifest=dict(bars=bars,distribution=dist,sources=sources,
                  source_images={p.name:dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),dimensions=Image.open(p).size)
                                 for p in SRC.glob('*.png')},
                  note='Image reconstructions are measurements, while printed ratios are transcribed. Both versions retained.')
    (OUT/'digitization_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
