"""Recover shared weekly vertices, accounting for thick rounded line joins."""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

R = Path(__file__).resolve().parents[1]
O = R/'data/four_now_redigitized_20260913'
SRC = R/'assets/sources/four_now_originals/250410_생산처별장기추이.jpg'
raw = pd.read_csv(O/'250410_each_pixel_traces.csv')
axis = pd.read_csv(O/'250410_nonuniform_vertex_diagnostic.csv').rename(
    columns={'nonuniform_best_x':'x_week','x_float':'x_equal'})
axis['dx_from_previous_week'] = axis.x_week.diff()
assert len(axis)==118 and axis.loc[axis.date=='2024-10-17','x_week'].iloc[0]==1087
traces = {s:g.set_index('x_pixel').y_pixel for s,g in raw.groupby('series')}

# Find visible turns without treating either edge of a rendered point disc as
# an additional dated observation.  Retain raw edge peaks for audit.
corner_rows = []
for name,trace in traces.items():
    gx = np.arange(trace.index.min(),trace.index.max()+1)
    gy = np.interp(gx,trace.index,trace.to_numpy(float))
    smooth = gaussian_filter1d(gy,1)
    left = (np.roll(smooth,2)-np.roll(smooth,5))/3
    right = (np.roll(smooth,-5)-np.roll(smooth,-2))/3
    angle = np.abs(np.arctan(right)-np.arctan(left))*180/np.pi
    angle[:6]=0;angle[-6:]=0
    peaks,_ = find_peaks(angle,distance=5,prominence=10)
    peaks = peaks[angle[peaks]>=25]
    for idx in peaks:
        x = int(gx[idx])
        j = int(np.argmin(abs(axis.x_week.to_numpy()-x)))
        gap = int(abs(axis.x_week.iloc[j]-x))
        corner_rows.append(dict(series=name,x_corner=x,y_corner=float(gy[idx]),
            turn_angle_deg=float(angle[idx]),date=axis.date.iloc[j],
            shared_week_x=int(axis.x_week.iloc[j]),
            gap_to_shared_week_x_px=gap,
            assignment='within_4px_point_disk' if gap<=4 else 'unmatched'))
corners = pd.DataFrame(corner_rows).sort_values(['series','x_corner'])
corners['dx_from_previous_bend_px'] = corners.groupby('series').x_corner.diff()
corners['weeks_since_previous_bend'] = corners.groupby('series').date.transform(
    lambda z:pd.to_datetime(z).diff().dt.days/7)
corners['dx_per_week_between_bends'] = (
    corners.dx_from_previous_bend_px/corners.weeks_since_previous_bend)
corners.to_csv(O/'250410_all_detected_bends.csv',index=False)

# Two nearby curvature peaks can be the edges of one thick weekly point.
merged=[]
for (name,date),g in corners.groupby(['series','date']):
    merged.append(dict(series=name,date=date,
        x_bend_estimate=float(np.average(g.x_corner,weights=g.turn_angle_deg)),
        x_bend_min=int(g.x_corner.min()),x_bend_max=int(g.x_corner.max()),
        edge_peak_count=len(g),max_turn_angle_deg=float(g.turn_angle_deg.max()),
        shared_week_x=int(g.shared_week_x.iloc[0])))
bends = pd.DataFrame(merged).sort_values(['series','date'])
bends['dx_from_previous_bend_px'] = bends.groupby('series').x_bend_estimate.diff()
bends['weeks_since_previous_bend'] = bends.groupby('series').date.transform(
    lambda z:pd.to_datetime(z).diff().dt.days/7)
bends['dx_per_week_between_bends'] = (
    bends.dx_from_previous_bend_px/bends.weeks_since_previous_bend)
bends.to_csv(O/'250410_merged_weekly_bends.csv',index=False)

support = bends.groupby('date').series.nunique().rename('bend_source_count')
axis = axis.merge(support,left_on='date',right_index=True,how='left')
axis['bend_source_count'] = axis.bend_source_count.fillna(0).astype(int)
axis.to_csv(O/'250410_joint_weekly_axis.csv',index=False)

points=[]
for row in axis.itertuples():
    x=int(row.x_week)
    for name in ('boss','field','azmoth','other_coin','other'):
        if name=='other':
            status='unresolved_at_axis';y=np.nan;lo=np.nan;hi=np.nan
        elif name=='azmoth' and row.date<'2024-10-17':
            status='not_observable_before_launch';y=np.nan;lo=np.nan;hi=np.nan
        elif name=='other_coin' and row.date<'2024-02-22':
            status='not_observable_before_introduction';y=np.nan;lo=np.nan;hi=np.nan
        elif name in traces and x in traces[name].index:
            trace=traces[name]
            nearby=trace.loc[(trace.index>=x-2)&(trace.index<=x+2)]
            y=float(np.median(trace.loc[(trace.index>=x-1)&(trace.index<=x+1)]))
            lo=float(nearby.min()-2);hi=float(nearby.max()+2)
            status='observed_thick_stroke'
        else:
            status='unresolved_rgb';y=np.nan;lo=np.nan;hi=np.nan
        points.append(dict(date=row.date,series=name,x_week=x,
            y_center_estimate_px=y,y_possible_low_px=lo,y_possible_high_px=hi,
            status=status,bend_detected_here=bool(((bends.date==row.date)&
                (bends.series==name)).any())))
points=pd.DataFrame(points)
points.to_csv(O/'250410_joint_weekly_points.csv',index=False)

# Validate the connecting strokes away from the ±2px disc surrounding each
# vertex.  Each vertex's latent y centre can move ±4px inside the thick join.
checks=[]
for name,trace in traces.items():
    for i in range(len(axis)-1):
        if name=='azmoth' and axis.date.iloc[i]<'2024-10-17':continue
        if name=='other_coin' and axis.date.iloc[i]<'2024-02-22':continue
        x0=int(axis.x_week.iloc[i]);x1=int(axis.x_week.iloc[i+1])
        if x0 not in trace.index or x1 not in trace.index:continue
        inner=trace.loc[(trace.index>x0+2)&(trace.index<x1-2)]
        if inner.empty:continue
        xx=inner.index.to_numpy(float);u=(xx-x0)/(x1-x0)
        yy=inner.to_numpy(float);a=float(trace.loc[x0]);b=float(trace.loc[x1])
        best=min(float(np.max(abs(yy-((a+da)*(1-u)+(b+db)*u))))
                 for da in range(-4,5) for db in range(-4,5))
        checks.append(dict(series=name,week_start=axis.date.iloc[i],
            week_end=axis.date.iloc[i+1],x_start=x0,x_end=x1,
            interior_columns=len(inner),best_max_residual_px=best,
            verdict='WITHIN_STROKE_AND_POINT_SIZE' if best<=6 else 'REVIEW'))
checks=pd.DataFrame(checks)
checks.to_csv(O/'250410_point_aware_segment_test.csv',index=False)

# Same point-disc test on the old rigid lattice for an explicit before/after.
equal_checks=[]
for name,trace in traces.items():
    for i in range(len(axis)-1):
        if name=='azmoth' and axis.date.iloc[i]<'2024-10-17':continue
        if name=='other_coin' and axis.date.iloc[i]<'2024-02-22':continue
        x0=int(axis.x_pixel.iloc[i]);x1=int(axis.x_pixel.iloc[i+1])
        if x0 not in trace.index or x1 not in trace.index:continue
        inner=trace.loc[(trace.index>x0+2)&(trace.index<x1-2)]
        if inner.empty:continue
        xx=inner.index.to_numpy(float);u=(xx-x0)/(x1-x0)
        yy=inner.to_numpy(float);a=float(trace.loc[x0]);b=float(trace.loc[x1])
        best=min(float(np.max(abs(yy-((a+da)*(1-u)+(b+db)*u))))
                 for da in range(-4,5) for db in range(-4,5))
        equal_checks.append(dict(series=name,week_start=axis.date.iloc[i],
            x_start=x0,x_end=x1,best_max_residual_px=best,
            verdict='WITHIN_STROKE_AND_POINT_SIZE' if best<=6 else 'REVIEW'))
equal_checks=pd.DataFrame(equal_checks)
equal_checks.to_csv(O/'250410_equal_grid_point_aware_test.csv',index=False)

# Measure original colored vertical stroke widths, not enlargement widths.
rgb=np.asarray(Image.open(SRC).convert('RGB'),dtype=float)
color_specs={'boss':([191,75,84],65),'field':([253,158,166],45),
             'azmoth':([192,217,228],35),'other_coin':([42,86,130],42)}
stroke_widths={}
for name,trace in traces.items():
    color,limit=color_specs[name];lengths=[]
    for x,y in trace.items():
        x=int(x);y=int(y)
        patch=rgb[max(0,y-10):min(rgb.shape[0],y+11),x]
        count=int((np.linalg.norm(patch-color,axis=1)<limit).sum())
        if count:lengths.append(count)
    stroke_widths[name]=dict(median_px=float(np.median(lengths)),
        p95_px=float(np.quantile(lengths,.95)))

canvas=Image.open(SRC).convert('RGB');draw=ImageDraw.Draw(canvas)
palette={'boss':'#09bd24','field':'#1168ff','azmoth':'#dc00db','other_coin':'#ff9811'}
for row in points.itertuples():
    if row.status!='observed_thick_stroke':continue
    x=int(row.x_week);y=int(round(row.y_center_estimate_px))
    draw.ellipse((x-2,y-2,x+2,y+2),fill=palette[row.series])
canvas.save(O/'250410_joint_weekly_vertices_qa.png')
canvas.crop((1035,280,1270,825)).resize((940,2180)).save(
    O/'250410_joint_weekly_vertices_zoom.png')
canvas.crop((1187,312,1210,377)).resize((460,1300)).save(
    O/'250410_thick_point_corrected.png')

# Display only detected bends, with one vertical x per shared Thursday.
overlay=Image.open(SRC).convert('RGBA')
layer=Image.new('RGBA',overlay.size,(0,0,0,0));mark=ImageDraw.Draw(layer)
for r in axis.itertuples():
    if r.bend_source_count:
        mark.line((int(r.x_week),300,int(r.x_week),820),fill=(60,70,70,65),width=1)
for r in bends.itertuples():
    x=int(round(r.x_bend_estimate));trace=traces[r.series]
    if x not in trace.index:continue
    y=int(trace.loc[x]);color=palette[r.series]
    mark.ellipse((x-3,y-3,x+3,y+3),outline=color,width=2)
Image.alpha_composite(overlay,layer).convert('RGB').save(O/'250410_shared_week_bends_qa.png')
Image.alpha_composite(overlay,layer).convert('RGB').crop((1035,280,1270,825)).resize(
    (940,2180)).save(O/'250410_shared_week_bends_zoom.png')

by_series=checks.groupby('series').verdict.value_counts().unstack(fill_value=0)
holdout=pd.read_csv(O/'250410_leave_one_source_out.csv')
receipt=dict(launch_anchor=dict(date='2024-10-17',x=1087),weeks=len(axis),
    mean_dx_pixels=float(axis.dx_from_previous_week.dropna().mean()),
    dx_histogram={str(int(k)):int(v) for k,v in
                  axis.dx_from_previous_week.value_counts().sort_index().items()},
    raw_corner_candidates=len(corners),merged_bend_markers=len(bends),
    unmatched_bend_candidates=int((corners.assignment=='unmatched').sum()),
    max_bend_to_shared_week_x_px=int(corners.gap_to_shared_week_x_px.max()),
    straight_stroke_envelope_px=6,point_disc_radius_x_px=2,
    vertex_centre_allowance_y_px=4,
    measured_stroke_widths_px=stroke_widths,
    equal_grid_review_counts={k:int(v) for k,v in
        equal_checks.groupby('series').verdict.apply(lambda z:(z=='REVIEW').sum()).items()},
    leave_one_source_out_review_counts={r.held_out_series:int(r.review_gt6px)
        for r in holdout.itertuples()},
    segment_verdicts=by_series.to_dict(orient='index'),
    interpretation='shared weekly x estimates and point-size-consistent straight strokes; point centres remain pixel intervals')
(O/'250410_joint_weekly_manifest.json').write_text(
    json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
assert receipt['unmatched_bend_candidates']==0
print(json.dumps(receipt,ensure_ascii=False,indent=2))
