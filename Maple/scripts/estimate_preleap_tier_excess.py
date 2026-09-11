"""Conditional pre-leap increments under the user's stable-main assumption.

This is a band-level calculation, not another total-only latent decomposition.
"""
import csv
from datetime import date,timedelta
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Maple/data/now_20260910'
def read(p):
    with p.open(encoding='utf-8') as f:return list(csv.DictReader(f))
bars=read(D/'boss_tier_weekly.csv');by={r['date']:r for r in bars}
windows=read(D/'season_identification_windows.csv')
pop={r['date']:float(r['challenger_accounts']) for r in read(ROOT/'Maple/data/challengers_population_weekly_seasons1_4.csv')}
def band(row,k):return sum(float(row[f'tier{j}']) for j in range(1,k+1))
rows=[]
for win in windows:
    start=date.fromisoformat(win['start']);end=date.fromisoformat(win['first_leap']);cap=int(win['production_support_cap_tier'])
    baseline=by[(start-timedelta(days=7)).isoformat()]
    prior=[by[(start-timedelta(weeks=j)).isoformat()] for j in [1,2,3]]
    for row in bars:
        day=date.fromisoformat(row['date'])
        if not start<=day<end:continue
        low=band(row,2);lo0=band(baseline,2);prefix=band(row,cap);pre0=band(baseline,cap)
        delta=low-lo0;excess=prefix-pre0;c=pop.get(str(day),0)
        rows.append(dict(date=str(day),season=int(win['season']),first_leap=str(end),baseline_date=baseline['date'],
                         low2_current=low,low2_main_baseline=lo0,challenger_low2_increment=delta,
                         low2_increment_3week_baseline=low-np.mean([band(r,2) for r in prior]),
                         low2_increment_main_minus5pct=low-.95*lo0,low2_increment_main_plus5pct=low-1.05*lo0,
                         cap_tier=cap,cap_prefix_current=prefix,cap_prefix_main_baseline=pre0,
                         challenger_cap_excess_if_main_prefix_stable=excess,
                         observed_stack_total=row['B_digitized_constrained'],
                         cap_excess_share_if_main_prefix_stable=excess/float(row['B_digitized_constrained']),
                         C_observed=c if c else '',
                         challenger_low2_mean_per_100k=delta/c*1e5 if c else '',
                         challenger_cap_mean_per_100k=excess/c*1e5 if c else '',
                         negative_increment=bool(delta<0 or excess<0),
                         interpretation='User-assumed stable main band before first leap; season-boss coverage not yet reconciled'))
with (D/'preleap_tier_excess.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
for s in range(1,5):
    rr=[r for r in rows if r['season']==s];print(s,'weeks',len(rr),'last low2',rr[-1]['challenger_low2_increment'],
    'cap_share',rr[-1]['cap_excess_share_if_main_prefix_stable'])
