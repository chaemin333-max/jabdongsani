"""Compare source-image period shares with official eleven-day observations."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]
D=R/'data/now_20250410_overlay_v2'
d=pd.read_csv(D/'digitized_overlay.csv');t=pd.to_datetime(d.date)
official=pd.read_csv(R/'data/production_evidence_search_20260912/official_20241028_shares.csv')
mapping={'boss':'boss_pct','field':'field_pct','azmoth':'coin_azmoth_pct','other_coin':'coin_other_pct','etc':'other_pct'}
rows=[]
for w in official.itertuples():
    # Equal-day numerical integration; never compare one nearest pixel to eleven days.
    days=pd.date_range(w.start,w.end)+pd.Timedelta(hours=12)
    values={}
    for key in mapping:
        v=d[key+'_px'];good=v.notna()
        values[key]=np.interp(days.as_unit('ns').astype('int64'),t[good].astype('datetime64[ns]').astype('int64'),v[good]).sum()
    total=sum(values.values())
    for key,column in mapping.items():
        measured=100*values[key]/total;target=getattr(w,column)
        rows.append({'window':w.window_label,'start':w.start,'end':w.end,'component':key,'official_pct':target,'image_integrated_pct':measured,'difference_pp':measured-target})
a=pd.DataFrame(rows);a.to_csv(D/'official_window_audit.csv',index=False)
# Recompute counterfactual omission checks after corrected field/cyan tracing.
results=[]
for label,mask in [('before_azmoth',(t>='2024-07-01')&(t<'2024-10-17')),('azmoth_before_NEXT',(t>='2024-10-17')&(t<'2024-12-19')),('after_NEXT',t>='2025-01-01')]:
    for omit in ['none','azmoth','other_coin']:
        v=d.read_total if omit=='none' else d.read_total-d[omit+'_index']
        error=v[mask]/d.canonical_total[mask]-1
        results.append(dict(period=label,omit=omit,MAPE_pct=error.abs().mean()*100,bias_pct=error.median()*100))
pd.DataFrame(results).to_csv(D/'omission_diagnostic.csv',index=False)
assert len(a)==10
for _,g in a.groupby('window'):
    np.testing.assert_allclose(g.image_integrated_pct.sum(),100)
    np.testing.assert_allclose(g.official_pct.sum(),100)
print(a.to_string(index=False));print(pd.DataFrame(results).to_string(index=False))
