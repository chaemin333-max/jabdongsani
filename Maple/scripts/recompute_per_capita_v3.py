#!/usr/bin/env python3
import csv, math
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[2]
INP = ROOT / 'Maple/data/maple_production_calibration_inputs_weekly.csv'
V2 = ROOT / 'Maple/data/per_capita_production_v2_weekly.csv'
OUT = ROOT / 'Maple/data/per_capita_production_v3_weekly.csv'
SUM = ROOT / 'Maple/data/per_capita_production_v3_season_summary.csv'

with INP.open(encoding='utf-8') as f:
    inp = list(csv.DictReader(f))
with V2.open(encoding='utf-8') as f:
    v2rows = list(csv.DictReader(f))
v2 = {r['date']: r for r in v2rows}

# Pure-main informed composition correction windows.
# A_eff = A0 + lambda * max(A-A0, 0) within each identified clean inflow window.
# These are descriptive, externally calibrated from Challenger-free history.
composition_events = [
    dict(label='MILESTONE_DILUTION', start='2024-06-20', end='2024-06-27', baseline_date='2024-06-13', lam=0.639201, confidence='medium'),
    dict(label='NEXT_PRELAUNCH_DILUTION', start='2024-12-12', end='2024-12-12', baseline_date='2024-12-05', lam=0.053227, confidence='high'),
    dict(label='ASSEMBLE_PRELAUNCH_DILUTION', start='2025-06-12', end='2025-06-12', baseline_date='2025-06-05', lam=0.032182, confidence='high'),
    dict(label='CROWN_DILUTION', start='2025-12-18', end='2025-12-18', baseline_date='2025-12-11', lam=0.442960, confidence='medium'),
    # Season 3: apply the pure-main regime split, not progression fitting.
    dict(label='S3_MAIN_INFLOW_MODERATE', start='2026-03-19', end='2026-03-19', baseline_date='2026-03-12', lam=(0.639201+0.442960)/2, confidence='external_prior'),
    dict(label='S3_MAIN_INFLOW_EXPLOSIVE', start='2026-03-26', end='2026-03-26', baseline_date='2026-03-12', lam=(0.053227+0.032182)/2, confidence='external_prior'),
]

# Mature Challenger production anchors. These are muC, not season averages.
# Direct Strong Crystal reward changes are applied exogenously after the anchor window.
anchors = {
    'season1': dict(start='2025-04-03', end='2025-05-15', muC_pre=0.0000683845, reward_date='2025-04-17', reward_factor=0.919031579, source='late_static_S1'),
    'season2': dict(start='2025-09-25', end='2025-11-20', muC_pre=0.0000690614, reward_date='2025-10-23', reward_factor=0.7843388960, source='late_static_S2'),
    'season3': dict(start='2026-03-05', end='2026-04-16', muC_pre=0.0001219910, reward_date=None, reward_factor=1.0, source='late_static_S3'),
    # User instruction 2026-09-11: treat current terminal state as season-end estimate; recalibrate later.
    'season4': dict(start='2026-08-20', end='2026-09-03', muC_pre=0.0001728904, reward_date=None, reward_factor=1.0, source='terminal_S4_current_as_end'),
}

# Live validation metadata only; NOT substituted for the activity-count C_t denominator.
S4_LIVE_CHALLENGER_TIER_COUNT = 189757
S4_LIVE_DATE = '2026-09-11'

bydate = {r['date']: r for r in inp}

def f(x):
    if x is None or x == '': return math.nan
    return float(x)

def in_range(d,a,b): return a <= d <= b

rows=[]
for r in inp:
    d=r['date']; A=float(r['A_main_accounts']); C=float(r['C_challenger_accounts']); B=float(r['B_boss_newage100']); P=float(r['P_total_newage100'])
    season=r['challenger_season']
    Aeff=A; comp_label='none'; comp_lambda=1.0; comp_discount=0.0
    for ev in composition_events:
        if in_range(d, ev['start'], ev['end']):
            A0=float(bydate[ev['baseline_date']]['A_main_accounts'])
            entrants=max(A-A0,0.0)
            Aeff=A0+ev['lam']*entrants
            comp_discount=A-Aeff
            comp_label=ev['label']; comp_lambda=ev['lam']
            break

    vr=v2[d]
    muM_base=f(vr['muM_counterfactual'])
    if math.isnan(muM_base):
        muM_base=B/A if A>0 else math.nan

    # Baseline incumbent productivity: preserve V2's externally cleaned counterfactual.
    muM_inc=muM_base
    mature_anchor=False; mature_source='none'; muC=math.nan

    if season in anchors:
        an=anchors[season]
        if in_range(d,an['start'],an['end']):
            mature_anchor=True; mature_source=an['source']
            muC=an['muC_pre']
            if an['reward_date'] and d >= an['reward_date']:
                muC *= an['reward_factor']
            # Reverse-track main productivity from the mature Challenger anchor.
            muM_inc=(B-C*muC)/Aeff if Aeff>0 else math.nan
        else:
            # Before mature anchoring, use pure-main-informed A_eff with the V2 incumbent path.
            muC=(B-Aeff*muM_inc)/C if C>0 else math.nan
    elif C>0:
        muC=(B-Aeff*muM_inc)/C

    if C>0 and not math.isnan(muC) and not math.isnan(muM_inc) and muM_inc>0:
        w=muC/muM_inc
    else:
        w=0.0 if C==0 else math.nan

    # Identification flag only if the model implies non-positive incumbent productivity or negative Challenger productivity.
    id_fail = (C>0 and (math.isnan(muC) or math.isnan(muM_inc) or muM_inc<=0 or muC<0))
    if id_fail:
        w_canon=math.nan; E=math.nan; Q=math.nan
    else:
        w_canon=w
        E=Aeff + (w_canon*C if C>0 else 0.0)
        Q=P/E

    rows.append(dict(
        date=d,
        P_total_newage100=P,
        B_boss_newage100=B,
        A_main_accounts=A,
        A_effective_main_accounts=Aeff,
        A_composition_discount=comp_discount,
        composition_event=comp_label,
        entrant_lambda=comp_lambda,
        C_challenger_accounts=C,
        challenger_season=season,
        muM_incumbent_v3=muM_inc,
        muC_v3=muC if C>0 else '',
        w_v3=w_canon,
        mature_anchor=mature_anchor,
        mature_anchor_source=mature_source,
        identification_failed=id_fail,
        E_effective_accounts_v3=E,
        Q_raw_v3=Q,
        Q_raw_v2=f(vr['Q_raw_plot']) if vr.get('Q_raw_plot','') else f(vr['Q_raw']),
        w_v2=f(vr['w_plot']) if vr.get('w_plot','') else f(vr['w_challenger_main_equiv']),
        s4_live_challenger_tier_count=(S4_LIVE_CHALLENGER_TIER_COUNT if d=='2026-09-03' else ''),
        s4_live_count_observed_date=(S4_LIVE_DATE if d=='2026-09-03' else ''),
    ))

# Plot-only interpolation across any V3 identification failures, kept separate from canonical columns.
valid_idx=[i for i,r in enumerate(rows) if not math.isnan(r['Q_raw_v3'])]
for i,r in enumerate(rows):
    r['w_plot_v3']=r['w_v3']; r['E_plot_v3']=r['E_effective_accounts_v3']; r['Q_raw_plot_v3']=r['Q_raw_v3']
    if math.isnan(r['Q_raw_v3']):
        prev=max((j for j in valid_idx if j<i), default=None); nxt=min((j for j in valid_idx if j>i), default=None)
        if prev is not None and nxt is not None and rows[prev]['challenger_season']==r['challenger_season']==rows[nxt]['challenger_season']:
            t=(i-prev)/(nxt-prev)
            wp=rows[prev]['w_v3']+(rows[nxt]['w_v3']-rows[prev]['w_v3'])*t
            r['w_plot_v3']=wp; r['E_plot_v3']=r['A_effective_main_accounts']+wp*r['C_challenger_accounts']; r['Q_raw_plot_v3']=r['P_total_newage100']/r['E_plot_v3']

# Normalize to September 2025 weekly plotting mean, consistent with prior versions.
sep=[r['Q_raw_plot_v3'] for r in rows if r['date'].startswith('2025-09') and not math.isnan(r['Q_raw_plot_v3'])]
sepden=sum(sep)/len(sep)
for r in rows:
    r['Q_index_sep2025_100_v3']=100*r['Q_raw_plot_v3']/sepden if not math.isnan(r['Q_raw_plot_v3']) else math.nan
    q2=r['Q_raw_v2']
    r['raw_Q_change_vs_v2_pct']=100*(r['Q_raw_plot_v3']/q2-1) if (not math.isnan(r['Q_raw_plot_v3']) and not math.isnan(q2) and q2!=0) else math.nan

fields=list(rows[0].keys())
with OUT.open('w',newline='',encoding='utf-8') as f:
    wri=csv.DictWriter(f,fieldnames=fields); wri.writeheader()
    for r in rows:
        wri.writerow(r)

# Season summaries.
summ=[]
for s in ['season1','season2','season3','season4']:
    rr=[r for r in rows if r['challenger_season']==s and not math.isnan(r['w_v3'])]
    ww=[r['w_v3'] for r in rr]; cc=[r['C_challenger_accounts'] for r in rr]
    weighted=sum(w*c for w,c in zip(ww,cc))/sum(cc)
    mature=[r for r in rr if r['mature_anchor']]
    summ.append(dict(
        season=s,
        start=rr[0]['date'],end=rr[-1]['date'],
        v3_median_w=median(ww),v3_C_weighted_mean_w=weighted,
        v3_min_w=min(ww),v3_max_w=max(ww),
        mature_anchor_mean_w=(sum(r['w_v3']*r['C_challenger_accounts'] for r in mature)/sum(r['C_challenger_accounts'] for r in mature) if mature else math.nan),
        mature_anchor_muC=(sum(float(r['muC_v3'])*r['C_challenger_accounts'] for r in mature)/sum(r['C_challenger_accounts'] for r in mature) if mature else math.nan),
        failed_weeks=sum(r['identification_failed'] for r in rows if r['challenger_season']==s),
    ))
with SUM.open('w',newline='',encoding='utf-8') as f:
    wri=csv.DictWriter(f,fieldnames=list(summ[0].keys())); wri.writeheader(); wri.writerows(summ)

# Machine-readable stdout for workflow logs.
print('sep2025_den',sepden)
for s in summ: print('SUMMARY',s)
for d in ['2025-06-12','2025-06-26','2026-01-01','2026-02-26','2026-03-12','2026-03-19','2026-03-26','2026-04-16','2026-06-11','2026-06-25','2026-07-30','2026-08-20','2026-09-03']:
    r=next(x for x in rows if x['date']==d); print('POINT',d,'w',r['w_v3'],'Aeff',r['A_effective_main_accounts'],'Qidx',r['Q_index_sep2025_100_v3'],'dQv2%',r['raw_Q_change_vs_v2_pct'])
