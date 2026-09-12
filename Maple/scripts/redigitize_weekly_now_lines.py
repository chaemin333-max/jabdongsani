"""Read Thursday points, not arbitrary 2/3-pixel raster samples, from NOW charts.

The dense line trace is a local color-guide only.  Each emitted weekly y comes
from the original RGB image at its calculated weekly x coordinate.  No missing
component is set to zero or interpolated as an observation.
"""
from pathlib import Path
import calendar
import json

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parents[1]
S=R/'assets/sources/four_now_originals'
O=R/'data/four_now_redigitized_20260913'
dense=pd.read_csv(O/'raster_trace_nonweekly.csv',dtype={'snapshot':str})
azmoth=pd.read_csv(O/'azmoth_light_cyan_raster.csv').set_index('x_pixel')
azmoth_manifest=json.loads((O/'azmoth_light_cyan_manifest.json').read_text(encoding='utf-8'))
azmoth_first_x=int(azmoth_manifest['first_pixel_x'])

# Patch-kink x coordinates are read from the production curves, not from
# decorative NEW AGE/NEXT arrows (which can mark a presentation date).
anchor_dates=pd.to_datetime(['2023-06-15','2023-07-13','2024-12-19'])
anchor_week=np.array((anchor_dates-anchor_dates[0]).days/7,dtype=float)
anchor_x=np.array([554.,584.,1154.])
anchor_px_per_week,anchor_x_at_newage=np.polyfit(anchor_week,anchor_x,1)
# The kink spans several pixels, so patch dates determine the period better
# than the exact vertex phase.  Among uniform weekly lattices staying within
# ±3 px of *each* patch kink, choose the one whose piecewise-linear segments
# best reproduce both raw boss and field strokes.  This uses no canonical data.
traces=[]
for name in ('boss','field'):
    z=dense[(dense.snapshot=='250410')&(dense.series==name)&
            (dense.y_pixel.notna())].sort_values('x_pixel')
    traces.append((z.x_pixel.to_numpy(float),z.y_pixel.to_numpy(float)))
choices=[]
for p in np.arange(7.45,7.751,.005):
    for c in np.arange(551.,557.001,.125):
        if np.max(abs(c+p*anchor_week-anchor_x))>3:continue
        knots=c+p*np.arange(-30,100)
        loss=0.
        for xx,yy in traces:
            recovered=np.interp(knots,xx,yy)
            loss+=float(np.mean((np.interp(xx,knots,recovered)-yy)**2))
        choices.append((loss,float(p),float(c)))
polyline_loss,vertex_px_per_week,vertex_x_at_newage=min(choices)
# The user-specified datum is the *first cyan point*, whose original pixel is
# x=1087 on the 2024-10-17 launch week.  This fixes the grid phase for every
# source.  The patch kinks fix the 7-day spacing; the polyline fit above is now
# only an independent shape diagnostic, never an alternative date anchor.
px_per_week=float(anchor_px_per_week)
x_at_newage=float(azmoth_first_x-70*px_per_week)
azmoth_x=float(x_at_newage+70*px_per_week)
assert round(azmoth_x)==azmoth_first_x


def month_coordinate(day):
    return ((day.year-2023)*12+day.month-1+
            (day.day-1)/calendar.monthrange(day.year,day.month)[1])


month_slope,month_x0=np.polyfit([0,6,12,18,24,30],
                               [159,380,600,823,1045,1266],1)
grid=[]
for date in pd.date_range('2022-12-29','2025-03-27',freq='7D'):
    w=(date-anchor_dates[0]).days//7
    grid.append(('250410','production_sources',date,
                 float(x_at_newage+w*px_per_week),'azmoth_launch_first_pixel_plus_patch_week_spacing'))
for i,date in enumerate(pd.date_range('2025-04-17',periods=25,freq='7D')):
    grid.append(('251016','production_sources',date,136.+49*i,
                 'first_last_week_and_line_vertices'))
for i,date in enumerate(pd.date_range('2025-08-21',periods=53,freq='7D')):
    grid.append(('260910','production_sources',date,192.+(1130-192)*i/52,
                 'first_last_week_and_line_vertices'))
for date in pd.date_range('2022-12-29','2025-10-02',freq='7D'):
    grid.append(('251016','total_production',date,
                 float(month_x0+month_slope*month_coordinate(date)),
                 'six_printed_jan_jul_ticks'))
for date in pd.date_range('2023-04-06','2023-10-26',freq='7D'):
    grid.append(('231116','boss_tier_lines',date,
                 float(94+(date-pd.Timestamp('2023-04-01')).days*1560/214),
                 'two_printed_month_ticks_approximate'))

# Same source-image color classes as the dense independent trace.
specs={
 ('250410','production_sources'):[
    ('boss',[191,75,84],300,745,60),('field',[253,158,166],645,800,36),
    ('azmoth',[183,219,238],690,823,28),
    ('other_coin',[42,86,130],692,823,34),
    ('other',[188,190,189],812,828,25)],
 ('251016','production_sources'):[
    ('boss',[198,91,72],300,570,43),('field',[235,158,160],585,710,38),
    ('azmoth_coin',[34,77,111],685,753,35),
    ('other_coin',[169,217,231],620,755,29),
    ('other',[165,166,166],750,761,22)],
 ('260910','production_sources'):[
    ('boss',[205,91,73],330,655,44),('field',[234,151,154],625,710,38),
    ('serazar_coin',[40,77,109],684,717,35),
    ('coin_exchange',[166,215,231],650,717,30),
    ('other',[168,170,170],705,719,22)],
 ('251016','total_production'):[('total',[187,50,64],290,760,50)],
 ('231116','boss_tier_lines'):[
    ('hard_damien_to_hard_jinhilla',[42,50,131],570,1070,58),
    ('normal_suu_to_normal_dunkel',[119,130,197],740,1070,55),
    ('easy_cygnus_to_chaos_bellum',[155,155,156],680,1085,30),
    ('daily_boss',[107,131,202],1200,1340,46),
    ('normal_seren_to_extreme_kalos',[122,124,123],1260,1360,28)]}
images={('250410','production_sources'):'250410_생산처별장기추이.jpg',
        ('251016','production_sources'):'251016_생산처별.png',
        ('260910','production_sources'):'260910_생산처별.png',
        ('251016','total_production'):'251016_총생산.png',
        ('231116','boss_tier_lines'):'231116_보스구간별생산.png'}
arrays={k:np.asarray(Image.open(S/v).convert('RGB'),dtype=float) for k,v in images.items()}
rows=[]
for snap,chart,date,xf,grid_method in grid:
    x=int(round(xf));im=arrays[(snap,chart)]
    for series,palette,lo,hi,threshold in specs[(snap,chart)]:
        if snap=='250410' and series=='azmoth' and date<pd.Timestamp('2024-10-17'):
            rows.append(dict(snapshot=snap,chart=chart,date=str(date.date()),series=series,
                x_float=xf,x_pixel=x,y_pixel=np.nan,status='not_observable',
                color_distance=np.nan,grid_method=grid_method));continue
        if snap=='250410' and series=='azmoth':
            if x in azmoth.index:
                observed=azmoth.loc[x]
                rows.append(dict(snapshot=snap,chart=chart,date=str(date.date()),series=series,
                    x_float=xf,x_pixel=x,y_pixel=int(observed.y_pixel),
                    status='direct_weekly_rgb' if observed.status=='light_cyan_observed'
                           else 'crossing_or_occluded_path',
                    color_distance=float(observed.rgb_distance),grid_method=grid_method))
            else:
                rows.append(dict(snapshot=snap,chart=chart,date=str(date.date()),series=series,
                    x_float=xf,x_pixel=x,y_pixel=np.nan,status='unresolved_outside_cyan_line',
                    color_distance=np.nan,grid_method=grid_method))
            continue
        if snap=='250410' and series=='other_coin' and date<pd.Timestamp('2024-02-22'):
            rows.append(dict(snapshot=snap,chart=chart,date=str(date.date()),series=series,
                x_float=xf,x_pixel=x,y_pixel=np.nan,status='not_observable',
                color_distance=np.nan,grid_method=grid_method));continue
        g=dense[(dense.snapshot==snap)&(dense.chart==chart)&
                (dense.series==series)&(dense.y_pixel.notna())]
        # Only a nearby observed colored pixel may guide the color search.
        xx=g.x_pixel.to_numpy();yy=g.y_pixel.to_numpy()
        nearby=np.abs(xx-x)<=6
        if not nearby.any():
            y=np.nan;distance=np.nan;status='unresolved_no_local_guide'
        else:
            guide=float(np.interp(x,xx,yy))
            patch=im[lo:hi+1,max(0,x-2):x+3]
            dist=np.linalg.norm(patch-np.asarray(palette),axis=2)
            ys=np.arange(lo,hi+1)
            dist[np.abs(ys-guide)>12,:]=np.inf
            gray_boss=(snap=='231116' and series in
                ('easy_cygnus_to_chaos_bellum','normal_seren_to_extreme_kalos'))
            if gray_boss:
                dist[(np.ptp(patch,axis=2)>25)|(patch.mean(axis=2)<80)]=np.inf
            elif series!='other':
                dist[np.ptp(patch,axis=2)<12]=np.inf
            iy,ix=np.unravel_index(np.argmin(dist),dist.shape)
            distance=float(dist[iy,ix])
            if distance<threshold:
                y=int(lo+iy);status='direct_weekly_rgb'
            else:y=np.nan;distance=np.nan;status='unresolved_rgb'
        if series=='other' and status=='direct_weekly_rgb':
            status='candidate_axis_unverified'
        rows.append(dict(snapshot=snap,chart=chart,date=str(date.date()),series=series,
            x_float=xf,x_pixel=x,y_pixel=y,status=status,
            color_distance=distance,grid_method=grid_method))

out=pd.DataFrame(rows)
out['calendar_status']=np.where(out.snapshot=='250410',
    'patch_anchored_nominal_thursday_week_label',
    np.where(out.snapshot=='231116','approximate_month_tick_week_label',
             'printed_tick_or_endpoint_thursday_label'))
# A ±3-pixel x-phase change is plausible from the thickness of a steep kink.
# This is a diagnostic made from the dense raster trace, not a replacement y.
out['phase_span_y_px']=np.nan
for series in ('boss','field'):
    g=dense[(dense.snapshot=='250410')&(dense.series==series)&
            (dense.y_pixel.notna())].sort_values('x_pixel')
    mask=(out.snapshot=='250410')&(out.series==series)
    xp=out.loc[mask,'x_float'].to_numpy()
    lower=np.interp(xp-3,g.x_pixel,g.y_pixel)
    upper=np.interp(xp+3,g.x_pixel,g.y_pixel)
    out.loc[mask,'phase_span_y_px']=abs(upper-lower)
out['phase_sensitive_gt10px']=out.phase_span_y_px>10
out.to_csv(O/'weekly_line_pixels_all.csv',index=False)
counts=out.groupby(['snapshot','chart','series','status']).size().rename('weeks').reset_index()
counts.to_csv(O/'weekly_line_status.csv',index=False)
out[(out.snapshot=='250410')&(out.series.isin(['boss','field']))&
    (out.phase_sensitive_gt10px)].to_csv(O/'weekly_250410_phase_sensitive.csv',index=False)
for (snap,chart),group in out.groupby(['snapshot','chart']):
    canvas=Image.open(S/images[(snap,chart)]).convert('RGB')
    draw=ImageDraw.Draw(canvas)
    for r in group.itertuples():
        if r.status not in ('direct_weekly_rgb','crossing_or_occluded_path'):
            continue
        color='#ff00aa' if r.series=='azmoth' else '#08b534'
        draw.ellipse((r.x_pixel-3,int(r.y_pixel)-3,r.x_pixel+3,int(r.y_pixel)+3),fill=color)
    canvas.save(O/f'{snap}_{chart}_WEEKLY_qa.png')

manifest=dict(weekly_axis_250410=dict(anchors=[
    dict(date=str(d.date()),x_pixel=float(x)) for d,x in zip(anchor_dates,anchor_x)],
    patch_only_fit_x_at_newage=float(anchor_x_at_newage),
    patch_only_fit_pixels_per_week=float(anchor_px_per_week),
    unanchored_weekly_vertex_fit_x_at_newage=float(vertex_x_at_newage),
    unanchored_weekly_vertex_fit_pixels_per_week=float(vertex_px_per_week),
    weekly_vertex_fit_loss=float(polyline_loss),
    phase_anchor='first visible light-cyan Azmoth pixel x=1087 on 2024-10-17',
    azmoth_launch_first_x=int(azmoth_first_x),
    chosen_x_at_newage=float(x_at_newage),
    chosen_pixels_per_week=float(px_per_week),
    launch_anchor_check=dict(date='2024-10-17',chosen_x=azmoth_x,
        directly_read_first_x=int(azmoth_first_x)),
    first_week='2022-12-29',last_week='2025-03-27',weeks=118,
    phase_sensitivity_definition='abs(y(x+3px)-y(x-3px)) from raster trace; diagnostic only',
    caveat='Kink positions have several-pixel uncertainty; calendar convention of weekly window is unprinted. Weekly x and date labels are approximate near steep steps.'),
    charts={f'{s}/{c}':dict(weeks=int(g.date.nunique()),series=int(g.series.nunique()))
            for (s,c),g in out.groupby(['snapshot','chart'])})
(O/'weekly_grid_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(out[(out.snapshot=='250410')&(out.series=='boss')])==118
assert all(pd.Timestamp(t).dayofweek==3 for t in out.date.unique())
print(json.dumps(manifest,ensure_ascii=False,indent=2))
print(counts.to_string(index=False))
