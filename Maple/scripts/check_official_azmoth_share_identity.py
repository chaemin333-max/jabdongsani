"""Use official production shares without digitizing the overlapped Azmoth line."""
from pathlib import Path
import calendar
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/official_azmoth_share_identity_20260913';D.mkdir(parents=True,exist_ok=True)
s=pd.read_csv(R/'data/now_20250410_overlay_v2/digitized_overlay.csv',parse_dates=['date']).sort_values('date')
old=pd.read_csv(R/'data/total_origin_audit_20260913/original_total_pixels.csv')
windows=[('Sep','2024-09-12','2024-09-22',.675,.243),('Oct','2024-10-17','2024-10-27',.611,.198)]
rows=[]
for z in [824,826,828,832,836]:
    vals={}
    for name,start,end,bshare,fshare in windows:
        days=pd.date_range(start,end)+pd.Timedelta(hours=12)
        ns=days.as_unit('ns').astype('int64')
        bh=(z-np.interp(ns,s.date.astype('datetime64[ns]').astype('int64'),s.boss_y)).mean()
        fh=(z-np.interp(ns,s.date.astype('datetime64[ns]').astype('int64'),s.field_y)).mean()
        mm=np.array([(d.year-2023)*12+d.month-1+(d.day-1)/calendar.monthrange(d.year,d.month)[1] for d in days])
        oldy=np.interp(mm,old.month,old.y).mean()
        vals[name]=(bh,fh,oldy)
    bp=vals['Oct'][0]/vals['Sep'][0];fp=vals['Oct'][1]/vals['Sep'][1]
    implied_b=bp*(.675/.611);implied_f=fp*(.243/.198)
    for zero2510 in [750,778.38]:
        p=(zero2510-vals['Oct'][2])/(zero2510-vals['Sep'][2])
        rows.append(dict(source_zero_candidate=z,total_zero_candidate=zero2510,boss_post_over_pre=bp,field_post_over_pre=fp,official_total_ratio_from_boss=implied_b,official_total_ratio_from_field=implied_f,old_2510_total_post_over_pre=p,boss_field_implied_gap_pp=100*(implied_b-implied_f),boss_vs_2510_gap_pp=100*(implied_b-p)))
d=pd.DataFrame(rows);d.to_csv(D/'ratio_identity.csv',index=False);print(d.to_string(index=False))
bars=pd.read_csv(R/'data/tier_regression_audit/official_20251016_pixels.csv',parse_dates=['date'])
pre=bars[(bars.date>='2024-09-12')&(bars.date<='2024-09-22')].height_pixels.mean()
post=bars[(bars.date>='2024-10-17')&(bars.date<='2024-10-27')].height_pixels.mean()
printed=pd.DataFrame([dict(source='2510_weekly_boss_bars',boss_pre_pixels=pre,boss_post_pixels=post,boss_ratio=post/pre,total_oct_over_sep_if_same_scope=(post/pre)*.675/.611,conditional_note='Official boss shares may include a wider scope than weekly boss bars')])
printed.to_csv(D/'weekly_bar_ratio_identity.csv',index=False)
print(printed.to_string(index=False))
