"""Check original 250410 strokes between every adjacent Thursday grid point.

An actual weekly polygon should be nearly straight between its vertices.  We
re-read every intervening image column; non-straight intervals remain flagged
and are never silently repaired or fitted into the weekly output.
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[1]
O=R/'data/four_now_redigitized_20260913'
SRC=R/'assets/sources/four_now_originals/250410_생산처별장기추이.jpg'
im=np.asarray(Image.open(SRC).convert('RGB'),dtype=float)
weekly=pd.read_csv(O/'weekly_line_pixels_all.csv',dtype={'snapshot':str})
weekly=weekly[(weekly.snapshot=='250410')&(weekly.chart=='production_sources')]
dense=pd.read_csv(O/'raster_trace_nonweekly.csv',dtype={'snapshot':str})
cyan=pd.read_csv(O/'azmoth_light_cyan_raster.csv')
specs={'boss':([191,75,84],300,745,65),
       'field':([253,158,166],645,800,45),
       'other_coin':([42,86,130],692,823,42)}

def trace_rgb(name):
    color,lo,hi,limit=specs[name]
    guide=dense[(dense.snapshot=='250410')&(dense.series==name)&
                (dense.y_pixel.notna())].sort_values('x_pixel')
    gx=guide.x_pixel.to_numpy();gy=guide.y_pixel.to_numpy()
    rows=[]
    for x in range(368,1263):
        if not len(gx) or np.min(abs(gx-x))>6:continue
        expected=float(np.interp(x,gx,gy))
        patch=im[lo:hi+1,max(0,x-1):x+2]
        dist=np.linalg.norm(patch-np.asarray(color),axis=2)
        ys=np.arange(lo,hi+1)
        dist[abs(ys-expected)>9,:]=np.inf
        dist[np.ptp(patch,axis=2)<12]=np.inf
        k,j=np.unravel_index(np.argmin(dist),dist.shape)
        best=float(dist[k,j])
        if best<limit:rows.append((x,int(lo+k),best))
    return pd.DataFrame(rows,columns=['x_pixel','y_pixel','rgb_distance'])

traces={'azmoth':cyan[['x_pixel','y_pixel','rgb_distance']].copy()}
for name in specs:traces[name]=trace_rgb(name)
alltrace=[]
for name,g in traces.items():
    z=g.copy();z['series']=name;alltrace.append(z)
pd.concat(alltrace,ignore_index=True).to_csv(O/'250410_each_pixel_traces.csv',index=False)

results=[]
for name,g in traces.items():
    pixels=g.set_index('x_pixel').y_pixel
    w=weekly[(weekly.series==name)&(weekly.status=='direct_weekly_rgb')].sort_values('date')
    for left,right in zip(w.iloc[:-1].itertuples(),w.iloc[1:].itertuples()):
        if (pd.Timestamp(right.date)-pd.Timestamp(left.date)).days!=7:continue
        x0,x1=int(left.x_pixel),int(right.x_pixel)
        center=pixels.loc[(pixels.index>=x0)&(pixels.index<=x1)]
        if x1<=x0 or len(center)<5:
            results.append(dict(series=name,week_start=left.date,week_end=right.date,
                x_start=x0,x_end=x1,observed_columns=len(center),
                max_abs_chord_residual_px=np.nan,rms_chord_residual_px=np.nan,
                verdict='UNRESOLVED_COLUMNS'))
            continue
        xx=center.index.to_numpy(float);yy=center.to_numpy(float)
        # Use original-image line centres at the endpoints, not a smoothed fit.
        # If an endpoint is covered by a crossing, fall back to the weekly RGB
        # observation and flag an endpoint discrepancy separately.
        ya=float(pixels.loc[x0]) if x0 in pixels.index else float(left.y_pixel)
        yb=float(pixels.loc[x1]) if x1 in pixels.index else float(right.y_pixel)
        chord=ya+(yb-ya)*(xx-x0)/(x1-x0)
        resid=yy-chord
        maximum=float(np.max(abs(resid)));rms=float(np.sqrt(np.mean(resid**2)))
        results.append(dict(series=name,week_start=left.date,week_end=right.date,
            x_start=x0,x_end=x1,observed_columns=len(center),
            max_abs_chord_residual_px=maximum,rms_chord_residual_px=rms,
            verdict='STRAIGHT_WITHIN_3PX' if maximum<=3 else
                    'REVIEW_3_TO_5PX' if maximum<=5 else 'INTERIOR_KINK_GT5PX'))

result=pd.DataFrame(results)
result.to_csv(O/'250410_weekly_segment_straightness.csv',index=False)
counts=result.groupby(['series','verdict']).size().rename('segments').reset_index()
counts.to_csv(O/'250410_weekly_segment_summary.csv',index=False)

def grid_bad_count(launch_x,spacing,name):
    t=traces[name].set_index('x_pixel').y_pixel
    bad=total=0
    for k in range(-100,30):
        if name=='azmoth' and k<0:continue
        x0=int(round(launch_x+k*spacing));x1=int(round(launch_x+(k+1)*spacing))
        if x0<368 or x1>1262 or x0>=x1 or x0 not in t.index or x1 not in t.index:
            continue
        z=t.loc[(t.index>=x0)&(t.index<=x1)]
        if len(z)<5:continue
        xx=z.index.to_numpy(float);yy=z.to_numpy(float)
        line=t.loc[x0]+(t.loc[x1]-t.loc[x0])*(xx-x0)/(x1-x0)
        bad+=bool(max(abs(yy-line))>5);total+=1
    return bad,total

# A stringent check of the proposed equal-spacing hypothesis: even allowing
# the visible first cyan pixel ±2 px and a broad plausible weekly spacing,
# does any *single* uniform grid remove all interior kinks?
sweep=[]
for first in range(1085,1090):
    for spacing in np.arange(7.45,7.751,.005):
        item=dict(first_x=first,pixels_per_week=float(spacing))
        for name in ('boss','field','azmoth','other_coin'):
            bad,total=grid_bad_count(first,spacing,name)
            item[name+'_gt5px']=bad;item[name+'_segments']=total
        item['boss_field_gt5px']=item['boss_gt5px']+item['field_gt5px']
        sweep.append(item)
sweep=pd.DataFrame(sweep)
sweep.to_csv(O/'250410_grid_sensitivity.csv',index=False)
best=sweep.sort_values(['boss_field_gt5px','azmoth_gt5px']).iloc[0]

canvas=Image.open(SRC).convert('RGB');draw=ImageDraw.Draw(canvas)
for row in result.itertuples():
    if row.verdict=='INTERIOR_KINK_GT5PX':
        x=(row.x_start+row.x_end)//2
        draw.line((x,285,x,825),fill='#ff00aa',width=1)
canvas.save(O/'250410_segment_kink_qa.png')
example=Image.open(SRC).convert('RGB').crop((1187,312,1210,377)).resize((460,1300))
edraw=ImageDraw.Draw(example)
for x,y,color in [(1193,361,'#00d833'),(1196,364,'#ec00ad'),(1201,325,'#00d833')]:
    xx=(x-1187)*20;yy=(y-312)*20
    edraw.ellipse((xx-7,yy-7,xx+7,yy+7),fill=color)
example.save(O/'250410_original_interior_kink_example.png')
receipt=dict(method='each original x column compared with chord between consecutive anchored Thursday points',
    tolerance_px=3,clear_kink_threshold_px=5,
    counts=counts.to_dict(orient='records'),
    uniform_grid_sensitivity=dict(first_x_range=[1085,1089],pixels_per_week_range=[7.45,7.75],
        best_boss_field_gt5px=int(best.boss_field_gt5px),
        best_first_x=int(best.first_x),best_pixels_per_week=float(best.pixels_per_week)),
    concrete_counterexample=dict(date_start='2025-01-23',date_end='2025-01-30',
        endpoint_x=[1193,1201],interior_kink_x=1196,
        observed_interior_y=364,chord_interior_y=347.5,deviation_px=16.5),
    no_claim_of_perfect_straightness=bool((result.verdict!='STRAIGHT_WITHIN_3PX').any()))
(O/'250410_segment_straightness_manifest.json').write_text(
    json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
