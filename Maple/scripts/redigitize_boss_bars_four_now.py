"""Re-read every stacked boss bar from source images; preserve raw pixel borders."""
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
from PIL import Image,ImageDraw
from scipy.signal import find_peaks
from digitize_now_20260910 import stack_profile
R=Path(__file__).resolve().parents[1];SRC=R/'assets/sources/four_now_originals';O=R/'data/four_now_redigitized_20260913';O.mkdir(exist_ok=True)
specs=[
 ('250410','250410 보스구간별.png',130,955,750,761,764,300,5,8,
  [[252,217,226],[181,95,124],[202,197,231],[124,112,160]],'2023-03-30'),
 ('251016','251016_보스구간별.png',124,1154,720,754,758,270,7,8,
  [[82,109,230],[245,101,65],[17,174,146],[158,106,225],[249,165,82],[21,166,211]],'2023-03-30'),
 ('260910','260910_보스구간별생산.png',130,820,640,663,666,330,5,8,
  [[96,115,254],[255,95,53],[2,181,146],[175,113,253],[255,165,79],[5,195,248],[255,118,148]],'2024-08-22')]
allrows=[];qa={}
for name,filename,x0,x1,y0,y1,base,toplim,distance,prom,palette,start in specs:
    im=np.asarray(Image.open(SRC/filename).convert('RGB'),dtype=float)
    profile=np.mean(np.ptp(im[y0:y1,x0:x1],axis=2),axis=0)
    centers=find_peaks(profile,distance=distance,prominence=prom)[0]+x0
    pal=np.asarray(palette,float);plab=[]
    for i,x in enumerate(centers):
        date=pd.Timestamp(start)+pd.Timedelta(weeks=int(i))
        event_crossing=name=='251016' and str(date.date()) in ('2025-04-17','2025-06-19')
        if event_crossing:
            event_palette=np.array([np.median(im[y-2:y+3,1186:1197],axis=(0,1)) for y in [309,339,371,401,433,463]])
            options=[]
            for xx in [x-1,x,x+1]:
                hh,_,_=stack_profile(im,xx,757,260,event_palette)
                options.append((hh.sum(),xx,hh))
            total,chosen,heights=max(options,key=lambda v:v[0])
            row=dict(snapshot=name,date=str(date.date()),x_pixel=int(x),chosen_x_pixel=int(chosen),top_y=int(757-total),bottom_y=757,total_height_px=int(total),detected_ink_rows=int(total),top_color_index=-1,bottom_color_index=-1,method='event_dash_adjacent_stack')
            for c,h in enumerate(heights):row[f'tier{c+1}_height_px']=int(h)
            allrows.append(row);continue
        candidates=[]
        radius=4 if event_crossing else 2
        for xx in range(max(0,x-radius),x+radius+1):
            cc=np.median(im[toplim:base+1,xx:xx+1],axis=1)
            saturation=np.ptp(cc,axis=1)/np.maximum(cc.max(axis=1),1)
            ik=(saturation>.075)&(cc.mean(axis=1)<250)
            ys=np.where(ik)[0]
            if len(ys)<8:continue
            last=int(ys.max());first=last;gap=0
            for yy in range(last,-1,-1):
                if ik[yy]:first=yy;gap=0
                else:
                    gap+=1
                    if gap>=5:break
            candidates.append((toplim+first,xx,cc))
        if not candidates:continue
        top,chosen,col=min(candidates,key=lambda item:item[0])
        distances=np.linalg.norm(col[:,None,:]-pal[None,:,:],axis=2)
        ink=(np.ptp(col,axis=1)/np.maximum(col.max(axis=1),1)>.075)&(col.mean(axis=1)<250)
        # Assign each row to ordered bottom->top colors; no output total fitting.
        colors=np.argmin(distances[top-toplim:base-toplim,:],axis=1)
        costs=distances[top-toplim:base-toplim,:]**2
        # Top->bottom categories must be nonincreasing; DP prevents color crossover.
        n,k=costs.shape;dp=np.full((n,k),np.inf);pr=np.zeros((n,k),int)
        dp[0]=costs[0]
        for j in range(1,n):
            running=np.minimum.accumulate(dp[j-1,::-1])[::-1]
            for c in range(k):
                candidates=dp[j-1,c:];pick=int(np.argmin(candidates))+c
                dp[j,c]=costs[j,c]+candidates.min();pr[j,c]=pick
        labels=np.empty(n,int);labels[-1]=int(np.argmin(dp[-1]))
        for j in range(n-1,0,-1):labels[j-1]=pr[j,labels[j]]
        heights=np.bincount(labels,minlength=k)
        row=dict(snapshot=name,date=str(date.date()),x_pixel=int(x),chosen_x_pixel=int(chosen),top_y=top,bottom_y=base,total_height_px=int(base-top),detected_ink_rows=int(ink.sum()),top_color_index=int(labels[0]),bottom_color_index=int(labels[-1]),method='alternate_rgb_ordered_stack')
        for c,h in enumerate(heights):row[f'tier{c+1}_height_px']=int(h)
        allrows.append(row)
    qa[name]=dict(image=filename,detected_centers=len(centers),output_rows=len([r for r in allrows if r['snapshot']==name]),first_x=int(centers[0]),last_x=int(centers[-1]),source_sha256=hashlib.sha256((SRC/filename).read_bytes()).hexdigest())
d=pd.DataFrame(allrows);d.to_csv(O/'boss_bars_all.csv',index=False)
(O/'boss_bar_manifest.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
for name,g in d.groupby('snapshot'):
    canvas=Image.open(SRC/qa[name]['image']).convert('RGB')
    draw=ImageDraw.Draw(canvas)
    for row in g.itertuples():
        x,y=int(row.chosen_x_pixel),int(row.top_y)
        draw.ellipse((x-2,y-2,x+2,y+2),fill='#ff0011')
    canvas.save(O/f'{name}_boss_bars_qa.png')
print(json.dumps(qa))
for name,g in d.groupby('snapshot'):
    print(name,'n',len(g),'tier means',[round(g[f'tier{i}_height_px'].mean(),1) for i in range(1,1+(4 if name=='250410' else 6 if name=='251016' else 7))])
    assert (g[[c for c in g if c.startswith('tier')]].sum(axis=1)==g.total_height_px).all()
