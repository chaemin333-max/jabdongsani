"""Diagnostic: can small per-week x corrections eliminate interior kinks?

This does not replace the equal-spacing weekly panel.  It tests whether a
nonuniform calendar axis or raster warp is needed to explain the original.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

R=Path(__file__).resolve().parents[1]
O=R/'data/four_now_redigitized_20260913'
w=pd.read_csv(O/'weekly_line_pixels_all.csv',dtype={'snapshot':str})
w=w[(w.snapshot=='250410')&(w.series=='boss')].sort_values('date').reset_index(drop=True)
pixels=pd.read_csv(O/'250410_each_pixel_traces.csv')
traces={s:g.set_index('x_pixel').y_pixel for s,g in pixels.groupby('series')}
series=('boss','field','azmoth')
nominal=w.x_float.to_numpy()
launch_idx=int(np.where(w.date=='2024-10-17')[0][0])
candidates=[]
for i,x in enumerate(nominal):
    poss=np.arange(round(x)-3,round(x)+4,dtype=int)
    if i==launch_idx:poss=np.array([1087])
    candidates.append(poss)

def edge_cost(left,right):
    if right-left<6 or right-left>10:return 1e8
    loss=.5*(right-left-7.5972)**2
    for name in series:
        t=traces[name]
        if left not in t.index or right not in t.index:continue
        z=t.loc[(t.index>=left)&(t.index<=right)]
        if len(z)<5:continue
        x=z.index.to_numpy(float);y=z.to_numpy(float)
        line=t.loc[left]+(t.loc[right]-t.loc[left])*(x-left)/(right-left)
        loss+=np.mean((y-line)**2)
    return float(loss)

scores=[(candidates[0]-nominal[0])**2];back=[]
for i in range(1,len(candidates)):
    before=candidates[i-1];current=candidates[i]
    cost=np.empty(len(current));prev=np.empty(len(current),int)
    for j,x in enumerate(current):
        options=np.array([scores[-1][k]+edge_cost(a,x) for k,a in enumerate(before)])
        best=int(np.argmin(options))
        cost[j]=options[best]+(x-nominal[i])**2
        prev[j]=best
    scores.append(cost);back.append(prev)
path=np.empty(len(candidates),int);path[-1]=int(np.argmin(scores[-1]))
for i in range(len(candidates)-2,-1,-1):path[i]=back[i][path[i+1]]
chosen=np.array([candidates[i][path[i]] for i in range(len(path))])

rows=[]
for i in range(len(chosen)-1):
    left,right=int(chosen[i]),int(chosen[i+1])
    for name in series:
        t=traces[name]
        if left not in t.index or right not in t.index:continue
        z=t.loc[(t.index>=left)&(t.index<=right)]
        if len(z)<5:continue
        x=z.index.to_numpy(float);y=z.to_numpy(float)
        line=t.loc[left]+(t.loc[right]-t.loc[left])*(x-left)/(right-left)
        rows.append(dict(series=name,date=w.date[i],x0=left,x1=right,
                         max_abs_residual_px=float(max(abs(y-line)))))
d=pd.DataFrame(rows)
w['nonuniform_best_x']=chosen;w['shift_from_equal_grid_px']=chosen-w.x_pixel
w[['date','x_float','x_pixel','nonuniform_best_x','shift_from_equal_grid_px']].to_csv(
    O/'250410_nonuniform_vertex_diagnostic.csv',index=False)
d.to_csv(O/'250410_nonuniform_segment_diagnostic.csv',index=False)
receipt=dict(interpretation='diagnostic only; launch x=1087 fixed; each other week allowed ±3px',
    shifted_weeks=int((chosen!=w.x_pixel.to_numpy()).sum()),
    max_shift_px=int(max(abs(chosen-w.x_pixel.to_numpy()))),
    count_gt5px=d.groupby('series').max_abs_residual_px.apply(lambda x:int((x>5).sum())).to_dict(),
    count_segments=d.groupby('series').size().to_dict())
(O/'250410_nonuniform_vertex_diagnostic.json').write_text(
    json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
