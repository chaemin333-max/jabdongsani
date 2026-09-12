"""Explicit Thursday coordinates for the lines and bar series used in the audit."""
from pathlib import Path
import calendar,json
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/thursday_month_boundary_audit_20260913'
rows=[]
def mark(name,df,xcol,ycol,method):
    for r in df.itertuples():
        day=pd.Timestamp(r.date).normalize();assert day.weekday()==3,(name,day)
        days=[day+pd.Timedelta(days=i) for i in range(7)]
        rows.append(dict(source=name,date=str(day.date()),x_pixel=getattr(r,xcol) if xcol else np.nan,y_pixel=getattr(r,ycol) if ycol else np.nan,
                         week_contains_day_1_or_2=any(d.day in (1,2) for d in days),date_itself_day_1_or_2=day.day in (1,2),method=method))

# April daily subpixel line traces: sample at dates independently recovered from printed month ticks.
apr=pd.read_csv(R/'data/now_20250410_overlay_v2/digitized_overlay.csv',parse_dates=['date']).sort_values('date')
thurs=pd.date_range('2023-01-05','2025-03-27',freq='W-THU')
ns=thurs.as_unit('ns').astype('int64');observed=apr.date.astype('datetime64[ns]').astype('int64')
ap=pd.DataFrame(dict(date=thurs,x_pixel=np.interp(ns,observed,apr.x_pixel),y_pixel=np.interp(ns,observed,apr.boss_y)))
mark('2504_source_boss',ap,'x_pixel','y_pixel','printed six month ticks to Thursday; interpolate line color trace')
bar=pd.read_csv(R/'data/four_boss_window_alignment/2504_pixels.csv',parse_dates=['date'])
bar['x_pixel']=133+(bar.date-pd.Timestamp('2023-03-30')).dt.total_seconds()/86400*7.96/7
mark('2504_boss_bars',bar,'x_pixel','top_y','weekly bar centers; pixels detected')
oct=pd.read_csv(R/'data/field_share_reconstruction_20260912/source_pixels.csv',parse_dates=['date'])
oct=oct[(oct.source.astype(str)=='251016')&(oct.series=='boss')].dropna(subset=['y_pixel'])
mark('2510_source_boss',oct,'x_pixel','y_pixel','original polyline weekly vertices')
ob=pd.read_csv(R/'data/tier_regression_audit/official_20251016_pixels.csv',parse_dates=['date'])
mark('2510_boss_bars',ob,'x_pixel',None,'weekly bar centers; total height separate column')
sep=pd.read_csv(R/'data/now_20260910/production_by_source_weekly.csv',parse_dates=['date'])
sep=sep[(sep.series=='boss_rewards')].dropna(subset=['line_y_pixel'])
mark('2609_source_boss',sep,'x_pixel','line_y_pixel','original polyline weekly vertices')
sb=pd.read_csv(R/'data/now_20260910/boss_tier_weekly.csv',parse_dates=['date'])
mark('2609_boss_bars',sb,'x_pixel',None,'weekly bar centers; total height separate columns')
nov=pd.read_csv(R/'data/four_boss_change_alignment/2311_line_pixels.csv',parse_dates=['date'])
grid=pd.date_range('2023-04-06','2023-11-02',freq='W-THU')
xn=nov.date.astype('datetime64[ns]').astype('int64');q=grid.as_unit('ns').astype('int64')
nd=pd.DataFrame(dict(date=grid,x_pixel=np.interp(q,xn,nov.pixel_x),y_pixel=np.interp(q,xn,nov.pixel_y)))
mark('2311_HardDamian_HardJinHilla',nd,'x_pixel','y_pixel','printed Apr/Nov tick endpoints to Thursdays; screen line trace')
d=pd.DataFrame(rows).sort_values(['source','date']);d.to_csv(D/'recovered_thursday_coordinates.csv',index=False)
summary=d.groupby('source').agg(weeks=('date','count'),removed=('week_contains_day_1_or_2','sum'),start=('date','first'),end=('date','last')).reset_index()
summary.to_csv(D/'thursday_coverage.csv',index=False)
assert len(summary)==7
print(summary.to_string(index=False))
