"""Publish conditional boss-productivity weights and event comparisons.

The source decomposition is immutable. These weights use actual main accounts,
not the previous V3 incumbent/A_eff definition. No total-production Q is changed.
"""
import csv,json,hashlib,math
from datetime import date,timedelta
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'Maple/data/tier_boss_decomposition_reward_adjusted'
OUT=ROOT/'Maple/data/boss_productivity_weights_20260912'

def read(path):
    with path.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def value(r,k):return float(r[k]) if r.get(k,'')!='' else math.nan
def summarize(rows):
    joint=[r for r in rows if r['weight_status']=='valid']
    main=[r for r in rows if math.isfinite(value(r,'bM_per_account'))]
    m=sum(r['M_boss'] for r in main)/sum(r['A_accounts'] for r in main) if main else math.nan
    c=sum(r['C_boss'] for r in joint)/sum(r['C_accounts'] for r in joint) if joint else math.nan
    wc=sum(r['C_accounts']*r['w'] for r in joint)/sum(r['C_accounts'] for r in joint) if joint else math.nan
    # Matched-week ratio makes the seasonal mean comparison explicit.
    matched_m=sum(r['M_boss'] for r in joint)/sum(r['A_accounts'] for r in joint) if joint else math.nan
    return dict(n_main=len(main),n_joint=len(joint),main_mean=m,challenger_mean=c,
                matched_main_mean=matched_m,ratio_of_period_means=c/matched_m if joint else math.nan,
                C_weighted_w=wc,median_w=float(np.median([r['w'] for r in joint])) if joint else math.nan)

def build():
    OUT.mkdir(exist_ok=True,parents=True)
    src=read(SOURCE/'weekly_decomposition.csv');scenarios=read(SOURCE/'scenario_weekly.csv')
    A={r['date']:float(r['A_accounts']) for r in src};by_scenario={}
    for r in scenarios:
        c=value(r,'C_accounts');m=value(r,'M_boss');cb=value(r,'C_boss')
        if c>0 and m>0:
            w=(cb/c)/(m/A[r['date']]);by_scenario.setdefault(r['date'],[]).append(w)
    rows=[]
    for r in src:
        a=A[r['date']];c=value(r,'C_accounts');m=value(r,'M_boss');cb=value(r,'C_boss');total=float(r['B_total'])
        if r['stage']=='outside_season':c=0.;w=0.;status='outside_season';bm=m/a;bc=math.nan;E=a
        elif math.isfinite(m) and m>0 and c>0:
            bm=m/a;bc=cb/c;w=bc/bm;E=a+w*c;status='valid'
        else:
            bm=m/a if math.isfinite(m) else math.nan;bc=w=E=math.nan
            status='season_end_boundary' if r['stage']=='end_boundary_unresolved' else 'missing_challenger_count'
        lo=value(r,'assumption_only_share_lower');hi=value(r,'assumption_only_share_upper')
        wlo=a/c*lo/(1-lo) if status=='valid' and lo<1 else math.nan
        whi=a/c*hi/(1-hi) if status=='valid' and hi<1-1e-12 else math.nan
        alternatives=by_scenario.get(r['date'],[])
        rows.append(dict(date=r['date'],season=int(r['season']),stage=r['stage'],weight_status=status,
                         A_accounts=a,C_accounts=c,M_boss=m,C_boss=cb,B_total=total,
                         bM_per_account=bm,bC_per_account=bc,w=w,E_main_equivalent_accounts=E,
                         C_weighted_contribution=w*c if status=='valid' else 0. if status=='outside_season' else math.nan,
                         w_scenario_min=min(alternatives) if alternatives else w,w_scenario_max=max(alternatives) if alternatives else w,
                         w_assumption_only_lower=wlo,w_assumption_only_upper=whi,
                         w_assumption_upper_unbounded=bool(status=='valid' and hi>=1-1e-12),
                         identity_relative_error=abs(total/E-bm)/bm if status=='valid' else 0. if status=='outside_season' else math.nan))
    ref=np.mean([r['bM_per_account'] for r in rows if r['date'].startswith('2025-09') and math.isfinite(r['bM_per_account'])])
    for r in rows:r['main_productivity_index']=100*r['bM_per_account']/ref;r['challenger_productivity_index']=100*r['bC_per_account']/ref
    # Preserve explicit blanks rather than exporting NaN as an economic zero.
    cleaned=[{k:('' if isinstance(v,float) and not math.isfinite(v) else v) for k,v in r.items()} for r in rows]
    write('weekly_weights.csv',cleaned)
    seasonal=[];stages=[]
    for s in range(1,5):
        rr=[r for r in rows if r['season']==s];sm=summarize(rr);last=next(r for r in rr[::-1] if r['weight_status']=='valid')
        seasonal.append(dict(season=s,start=rr[0]['date'],end=rr[-1]['date'],n_calendar=len(rr),**sm,
                             main_index=100*sm['matched_main_mean']/ref,challenger_index=100*sm['challenger_mean']/ref,
                             last_date=last['date'],last_w=last['w'],last_w_scenario_min=last['w_scenario_min'],last_w_scenario_max=last['w_scenario_max']))
        for stage in ['pre_leap','post_leap']:
            rs=[r for r in rr if r['stage']==stage];stages.append(dict(season=s,stage=stage,**summarize(rs)))
    write('season_summary.csv',seasonal);write('stage_summary.csv',stages)
    events={}
    for e in read(ROOT/'Maple/data/maple_patch_event_layer_2024_2026.csv'):
        events.setdefault(e['date'],[]).append(e['event_code'])
    for e in read(ROOT/'Maple/data/now_20260910/season_identification_windows.csv'):
        events.setdefault(e['first_leap'],[]).append(f"S{e['season']}_FIRST_LEAP")
        events.setdefault(e['season_end'],[]).append(f"S{e['season']}_END")
    patches=[]
    for ds,codes in sorted(events.items()):
        day=date.fromisoformat(ds)
        if not rows[0]['date']<=ds<=rows[-1]['date']:continue
        pre=[r for r in rows if day-timedelta(weeks=3)<=date.fromisoformat(r['date'])<day]
        post=[r for r in rows if day<=date.fromisoformat(r['date'])<day+timedelta(weeks=3)]
        a,b=summarize(pre),summarize(post)
        same_season=bool(a['n_joint'] and b['n_joint'] and {r['season'] for r in pre if r['weight_status']=='valid'}=={r['season'] for r in post if r['weight_status']=='valid'})
        change=lambda x,y:100*(y/x-1) if math.isfinite(x) and math.isfinite(y) and x>0 else ''
        patches.append(dict(date=ds,events=';'.join(codes),pre_calendar=len(pre),post_calendar=len(post),
                            main_pre_n=a['n_main'],main_post_n=b['n_main'],C_pre_n=a['n_joint'],C_post_n=b['n_joint'],
                            main_mean_pre=a['main_mean'],main_mean_post=b['main_mean'],main_change_pct=change(a['main_mean'],b['main_mean']),
                            C_mean_pre=a['challenger_mean'],C_mean_post=b['challenger_mean'],
                            C_change_pct=change(a['challenger_mean'],b['challenger_mean']) if same_season else '',
                            w_pre=a['C_weighted_w'],w_post=b['C_weighted_w'],
                            w_change_pct=change(a['C_weighted_w'],b['C_weighted_w']) if same_season else '',
                            coverage='full_3plus3' if len(pre)==3 and len(post)==3 and a['n_main']==3 and b['n_main']==3 else 'partial_or_boundary',
                            interpretation='descriptive window comparison; not a causal patch coefficient'))
    write('patch_window_comparison.csv',[{k:('' if isinstance(v,float) and not math.isfinite(v) else v) for k,v in r.items()} for r in patches])
    old={r['date']:r for r in read(ROOT/'Maple/data/per_capita_production_v3_weekly.csv')};comparison=[]
    for r in rows:
        if r['date'] not in old:continue
        oldw=value(old[r['date']],'w_v3')
        comparison.append(dict(date=r['date'],new_w=r['w'] if math.isfinite(r['w']) else '',
                               V3_w=oldw if math.isfinite(oldw) else '',
                               interpretation='different estimands: actual A mean versus V3 incumbent/A_eff; comparison only'))
    write('v3_weight_comparison.csv',comparison)
    manifest=dict(status='CONDITIONAL_BOSS_WEIGHTS',source='tier_boss_decomposition_reward_adjusted',
                  cutoff='2026-08-21',last_joint_week='2026-08-20',definition='w=(C_boss/C_accounts)/(M_boss/A_accounts)',
                  E_definition='A+w*C',quantity='weekly boss production, not all boss rewards or total meso',
                  baseline='arithmetic mean of weekly main productivity during September 2025 = 100',baseline_raw=float(ref),
                  no_total_production_Q_updated=True,identity='B/E=bM is an algebraic identity, not new independent evidence',
                  patch_windows='3 calendar weeks before; event week and next 2 weeks after; missing observations preserved',
                  inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE/'weekly_decomposition.csv',SOURCE/'scenario_weekly.csv',
                     ROOT/'Maple/data/maple_patch_event_layer_2024_2026.csv',ROOT/'Maple/data/now_20260910/season_identification_windows.csv']})
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('BASELINE',ref);print('SEASONS',json.dumps(seasonal));print('LAST',json.dumps(cleaned[-1]))

if __name__=='__main__':build()
