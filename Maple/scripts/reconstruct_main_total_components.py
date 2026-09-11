"""Conditional total productivity: retain canonical total and weekly boss allocation."""
import calendar,json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/main_total_components_20260912'

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    paths=[ROOT/'data/boss_productivity_weights_20260912/weekly_weights.csv',ROOT/'data/meso_total_production_raw_canonical.json',ROOT/'data/now_20260910/production_by_source_weekly.csv']
    d=pd.read_csv(paths[0]); raw=json.loads(paths[1].read_text(encoding='utf-8'))['total']
    t=pd.to_datetime(d.date)
    x=[(z.year-2023)*12+z.month-1+(z.day-1)/calendar.monthrange(z.year,z.month)[1] for z in t]
    assert min(x)>=min(raw['month_coordinate']) and max(x)<=max(raw['month_coordinate'])
    d['P_total']=np.interp(x,raw['month_coordinate'],raw['index'])*6.495250069
    d['residual_outside_weekly_boss']=d.P_total-d.B_total
    assert (d.residual_outside_weekly_boss>=0).all()
    valid=d.weight_status.isin(['valid','outside_season'])
    d['q_main_lower_fixed_boss']=np.where(valid,d.M_boss/d.A_accounts,np.nan)
    d['q_main_upper_fixed_boss']=np.where(valid,(d.M_boss+d.residual_outside_weekly_boss)/d.A_accounts,np.nan)
    # Outside seasons the residual is necessarily all main-world production.
    outside=d.weight_status.eq('outside_season')
    d.loc[outside,'q_main_lower_fixed_boss']=d.loc[outside,'q_main_upper_fixed_boss']
    scenarios=[]
    for ratio in [0.,0.5,1.,2.]:
        z=d[['date','season','weight_status','P_total','A_accounts','C_accounts','M_boss','C_boss']].copy()
        z['residual_C_to_M_productivity_assumed']=ratio
        z['main_residual']=np.where(valid,d.residual_outside_weekly_boss*d.A_accounts/(d.A_accounts+ratio*d.C_accounts),np.nan)
        z['main_total']=z.M_boss+z.main_residual
        z['challenger_total']=z.P_total-z.main_total
        z['q_main']=z.main_total/z.A_accounts
        ref=z.loc[z.date.str.startswith('2025-09'),'q_main'].mean()
        z['q_main_sep2025_100']=100*z.q_main/ref
        z['own_scenario_baseline']=ref
        scenarios.append(z)
    s=pd.concat(scenarios,ignore_index=True)
    # Source-level difference is not automatically a measured Black Mage series.
    src=pd.read_csv(paths[2]); piv=src.pivot(index='date',columns='series',values='production_index').add_prefix('source_')
    audit=d.merge(piv,left_on='date',right_index=True,how='inner')
    audit['extra_boss_scope_difference']=audit.source_boss_rewards-audit.B_total
    audit['nonboss_residual']=audit.P_total-audit.source_boss_rewards
    audit['three_component_feasible']=(audit.extra_boss_scope_difference>=0)&(audit.nonboss_residual>=0)
    audit['detected_sources_sum']=audit.filter(regex='^source_').sum(axis=1,min_count=1)
    audit['total_minus_detected_sources']=audit.P_total-audit.detected_sources_sum
    three=[]
    for boss_extra_C_share in [0.,0.5,1.]:
        for r in [0.,0.5,1.,2.]:
            a=audit.copy(); ok=a.three_component_feasible & a.weight_status.isin(['valid','outside_season'])
            share=np.where(a.weight_status.eq('outside_season'),0,boss_extra_C_share)
            a['extra_boss_C_share_assumed']=share;a['nonboss_C_to_M_ratio_assumed']=r
            a['q_main_three_component']=np.where(ok,(a.M_boss+(1-share)*a.extra_boss_scope_difference+a.nonboss_residual*a.A_accounts/(a.A_accounts+r*a.C_accounts))/a.A_accounts,np.nan)
            three.append(a[['date','extra_boss_C_share_assumed','nonboss_C_to_M_ratio_assumed','three_component_feasible','q_main_three_component']])
    d.to_csv(OUT/'weekly_components.csv',index=False)
    s.to_csv(OUT/'residual_allocation_scenarios.csv',index=False)
    audit.to_csv(OUT/'source_scope_audit.csv',index=False)
    pd.concat(three).to_csv(OUT/'three_component_scenarios.csv',index=False)
    end=s[s.date.eq(d.date.max())]
    end.to_csv(OUT/'endpoint_summary.csv',index=False)
    meta={'status':'CONDITIONAL_TOTAL_RECONSTRUCTION_NO_SELECTED_CENTRAL_LINE','last_week':d.date.max(),'cutoff':'2026-08-21','scale':6.495250069,'source_weeks':len(audit),'three_component_feasible_weeks':int(audit.three_component_feasible.sum()),'residual_definition':'total minus weekly boss; includes nonweekly boss and nonboss','scenario_ratios':'0, 0.5, 1, 2 are sensitivity choices, not estimated or confidence bounds','baseline':'Each scenario uses its own September 2025 mean; compare raw q for level uncertainty','bounds':'Residual allocation bounds conditional on fixed primary weekly boss allocation; not full model uncertainty','no_clipping':True,'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (OUT/'manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False));print(end[['residual_C_to_M_productivity_assumed','q_main','q_main_sep2025_100']].to_string(index=False))
    print(d.iloc[-1][['P_total','B_total','residual_outside_weekly_boss','q_main_lower_fixed_boss','q_main_upper_fixed_boss']].to_string())

if __name__=='__main__':build()
