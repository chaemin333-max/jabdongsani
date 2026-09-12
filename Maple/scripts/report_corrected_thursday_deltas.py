from pathlib import Path
import calendar
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/total_ratio_exact_thursday_20260913'
a=pd.read_csv(D/'weekly_exact_thursday.csv',parse_dates=['date']);a=a[a.source_zero_y==824].set_index('date')
b=pd.read_csv(R/'data/tier_regression_audit/official_20251016_pixels.csv',parse_dates=['date']).set_index('date')
s=pd.read_csv(R/'data/field_share_reconstruction_20260912/source_pixels.csv',parse_dates=['date']);s=s[(s.source.astype(str)=='251016')&(s.series=='boss')].set_index('date')
c=pd.read_csv(R/'data/now_20260910/boss_tier_weekly.csv',parse_dates=['date']).set_index('date')
original=pd.read_csv(R/'data/total_origin_audit_20260913/original_total_pixels.csv')
t=pd.read_csv(R/'data/now_20260910/production_by_source_weekly.csv',parse_dates=['date']);t=t[t.series=='boss_rewards'].set_index('date')
intervals=[('아즈모스 도입','2024-10-10','2024-10-17'),('도입 다음 주','2024-10-17','2024-10-24'),('NEXT 시작','2024-12-12','2024-12-19'),('NEXT 다음 주','2024-12-19','2024-12-26'),('2510·2609 겹침','2025-08-21','2025-08-28'),('9월 관측','2025-09-18','2025-09-25'),('2609 2차 이후','2026-07-23','2026-07-30')]
def delta(frame,d0,d1,col,sign=1):
    if pd.Timestamp(d0) not in frame.index or pd.Timestamp(d1) not in frame.index:return np.nan
    x=frame.loc[d0,col];y=frame.loc[d1,col]
    if isinstance(x,pd.Series):x=x.iloc[0]
    if isinstance(y,pd.Series):y=y.iloc[0]
    return sign*(y-x) if pd.notna(x) and pd.notna(y) else np.nan
def total_negative_y(day):
    p=pd.Timestamp(day);m=(p.year-2023)*12+p.month-1+(p.day-1)/calendar.monthrange(p.year,p.month)[1]
    return -np.interp(m,original.month,original.y) if original.month.min()<=m<=original.month.max() else np.nan
rows=[]
for label,d0,d1 in intervals:
    az0=0 if d0<'2024-10-17' and pd.Timestamp(d0) in a.index else (824-a.loc[d0,'azmoth_y'] if pd.Timestamp(d0) in a.index else np.nan)
    az1=0 if d1<'2024-10-17' and pd.Timestamp(d1) in a.index else (824-a.loc[d1,'azmoth_y'] if pd.Timestamp(d1) in a.index else np.nan)
    rows.append(dict(interval=label,start=d0,end=d1,
        apr_source_boss_up_px=delta(a,d0,d1,'boss_y',-1),apr_source_field_up_px=delta(a,d0,d1,'field_y',-1),
        apr_source_azmoth_change_px=az1-az0 if np.isfinite(az0) and np.isfinite(az1) else np.nan,
        apr_source_sum_change_px=delta(a,d0,d1,'source_sum'),apr_source_sum_without_az_change_px=delta(a,d0,d1,'source_sum')-(az1-az0) if np.isfinite(az0) and np.isfinite(az1) else np.nan,
        apr_boss_bar_up_px=delta(a,d0,d1,'total_px'),oct_total_up_px=total_negative_y(d1)-total_negative_y(d0),oct_boss_bar_up_px=delta(b,d0,d1,'height_pixels'),oct_source_boss_up_px=delta(s,d0,d1,'y_pixel',-1),
        sep_boss_bar_up_px=delta(c,d0,d1,'B_digitized_raw')/2.944717415035746,sep_source_boss_up_px=delta(t,d0,d1,'line_y_pixel',-1)))
d=pd.DataFrame(rows);d.to_csv(D/'named_thursday_pixel_deltas.csv',index=False);print(d.to_string(index=False))
assert abs(d.loc[d.interval=='아즈모스 도입','apr_source_azmoth_change_px'].iloc[0]-101.5007)<1
