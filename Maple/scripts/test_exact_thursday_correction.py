from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/total_ratio_exact_thursday_20260913'
d=pd.read_csv(D/'weekly_exact_thursday.csv',parse_dates=['date']);d=d[d.source_zero_y==824]
pre=d.loc[d.date.eq('2024-10-10')].iloc[0];start=d.loc[d.date.eq('2024-10-17')].iloc[0];after=d.loc[d.date.eq('2024-10-24')].iloc[0]
assert not pre.azmoth_active and start.azmoth_active and after.azmoth_active
assert pre.date.day_name()==start.date.day_name()==after.date.day_name()=='Thursday'
assert 100<824-start.azmoth_y<103
assert 25<start.source_sum_prediction-start.target_negative_y<35
assert abs((start.source_sum-pre.source_sum)-58.414132)<.01
assert abs((after.source_sum-start.source_sum)+19.044342)<.01
s=pd.read_csv(D/'azmoth_zero_sensitivity.csv')
q=s.pivot(index='source_zero_y',columns='scenario',values='post_RMSE_2510_total_pixels')
assert (q.without_azmoth<q.with_azmoth).all()
j=pd.read_csv(D/'named_thursday_pixel_deltas.csv')
assert abs(j.loc[j.start.eq('2024-10-10'),'oct_total_up_px'].iloc[0]+15.536252)<.01
print('exact Thursday and Azmoth correction checks passed')
