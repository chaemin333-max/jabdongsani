"""Tier-supported decomposition with exact pre-leap low-band anchors.

Kai and Meirin are included in tier 3, not added as unobserved new production.
Post-leap exits are a scenario proxy, never reported as measured transfers.
"""
import csv,json,hashlib
from dataclasses import dataclass,asdict,replace
from datetime import date,timedelta
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,Bounds,LinearConstraint

ROOT=Path(__file__).resolve().parents[2];SOURCE=ROOT/'Maple/data/now_20260910'
OUT=ROOT/'Maple/data/tier_boss_decomposition_v1'

def read(p):
    with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(p,rows):
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)

@dataclass(frozen=True)
class Assumptions:
    name:str='primary'
    transfer_fraction:float=.5
    transferred_productivity:float=.8
    main_tolerance:float=.15
    final_upper_elasticity:float=0.
    high_control_weight:float=0.
    growth_regularizer:float=.35
    include_progression:bool=True
    population_provider:str='meaegi'
    solo_upper_control:bool=False

def inputs():
    rows=read(SOURCE/'boss_tier_weekly.csv');windows=read(SOURCE/'season_identification_windows.csv')
    pops=read(ROOT/'Maple/data/challengers_population_weekly_seasons1_4.csv')
    C={r['date']:float(r['challenger_accounts']) for r in pops}
    A={r['date']:float(r['A_main_accounts']) for r in read(ROOT/'Maple/data/maple_production_calibration_inputs_weekly.csv')}
    H={s:{r['date']:float(r['challenger_count']) for r in read(ROOT/'Maple/data/boss_decomposition_research_20260912/challenger_progression_canonical_s2_s3.csv')
          if r['season']==f'season{s}' and r['challenger_count']} for s in [2,3]}
    cj=json.loads((ROOT/'Maple/data/boss_decomposition_research_20260912/chuchu_population_initial_data.json').read_text(encoding='utf-8'))
    CC={r['date']:sum(v['changedCount'] for v in r['worlds'].values()) for key in ['populationChallenger','populationChallenger2','populationChallenger3'] for r in cj[key] if r['date']<='2026-08-21'}
    return rows,windows,C,A,H,CC

def fit_season(spec,win,rows,C,H):
    s=int(win['season']);cap=int(win['production_support_cap_tier'])
    start=date.fromisoformat(win['start']);leap=date.fromisoformat(win['first_leap']);end=date.fromisoformat(win['season_end'])
    by={r['date']:r for r in rows};sr=[r for r in rows if str(start)<=r['date']<str(end)]
    ds=[date.fromisoformat(r['date']) for r in sr];n=len(sr);p=n*cap
    B=np.array([[float(r[f'tier{j+1}'])/100 for j in range(cap)] for r in sr])
    total=np.array([float(r['B_digitized_constrained']) for r in sr])/100
    pre=by[str(start-timedelta(weeks=1))];pre_b=np.array([float(pre[f'tier{j+1}'])/100 for j in range(cap)])
    counts=np.array([C.get(str(d),0) for d in ds]);no_leap=np.array([d<leap for d in ds])
    closed=(end+timedelta(weeks=2)).isoformat() in by
    post=by[str(end+timedelta(weeks=2))] if closed else None
    # T_t = K_t x. The declining count is only a scenario proxy for exits.
    K=np.zeros((n,n));transfer_count=np.zeros(n)
    for t in range(1,n):
        K[t]=K[t-1]*.995
        if ds[t]>=leap and counts[t-1]>0 and counts[t]>0:
            transfer_count[t]=spec.transfer_fraction*max(counts[t-1]-counts[t],0)
            K[t,t-1]+=spec.transferred_productivity*transfer_count[t]/counts[t-1]
    kp=K[-1].copy()*.995**3
    if closed:kp[-1]+=spec.transferred_productivity*spec.transfer_fraction*.995**2
    R=[];target=[]
    high=np.array([sum(float(r[f'tier{j}']) for j in range(cap+1,8)) for r in sr])
    high0=sum(float(pre[f'tier{j}']) for j in range(cap+1,8))
    if spec.solo_upper_control and not closed:
        solo=read(SOURCE/'solo_clear_distribution.csv')
        upper=[r for r in solo if int(r['tier'])>cap]
        n0=sum(float(r['constrained_share_reference']) for r in upper)
        n1=sum(float(r['constrained_share_comparison'])*float(r['implied_population_growth_multiplier']) for r in upper)
        anchor_dates=[date(2026,2,12).toordinal(),date(2026,8,20).toordinal()]
        npre=np.interp((start-timedelta(weeks=1)).toordinal(),anchor_dates,[n0,n1])
        nn=np.interp([d.toordinal() for d in ds],anchor_dates,[n0,n1])
        high=high/(nn/npre)  # upper-boss production per upper-clearing population proxy
    main_reference=[]
    for j in range(cap):
        if closed:
            post_b=float(post[f'tier{j+1}'])/100
            time=np.array([(d-start).days+7 for d in ds])/((end+timedelta(weeks=2)-start).days+7)
            highpost=sum(float(post[f'tier{k}']) for k in range(cap+1,8))
            ht=np.clip((high-high0)/(highpost-high0),0,1) if abs(highpost-high0)>10 else time
            weight=(1-spec.high_control_weight)*time+spec.high_control_weight*ht
            reference=(1-weight)*pre_b[j]+weight*post_b
        else:
            # No post-cutoff anchor. Stable main is primary; observed upper tiers
            # support explicit positive/negative elasticity sensitivity only.
            weight=np.zeros(n)
            reference=pre_b[j]*np.maximum(high/max(high0,3),.25)**spec.final_upper_elasticity
        main_reference.append(reference)
        scale=max(spec.main_tolerance*max(pre_b[j],np.median(B[:,j])),.06)
        Q=-np.eye(n)-K+weight[:,None]*kp[None,:]
        for t in range(n):
            rr=np.zeros(p);rr[np.arange(n)*cap+j]=Q[t]/scale
            R.append(rr);target.append((reference[t]-B[t,j])/scale)
        # Permit growth and changes; do not impose constant late capacity.
        for t in range(1,n-1):
            if np.all(counts[t-1:t+2]>0):
                rr=np.zeros(p)
                rr[(np.arange(t-1,t+2))*cap+j]=np.array([1,-2,1])/(counts[t-1:t+2]/1e5)/.5
                R.append(rr);target.append(0.)
    # Exact canonical H affects a low-dimensional growth subspace, not H/C.
    valid=np.flatnonzero(counts>0);age=np.array([(d-start).days/7 for d in ds])[valid]
    lib=float(win['liberation_weeks_user_assumption'] or 12)
    G=[np.ones(len(valid)),age/max(age.max(),1),np.minimum(age/lib,1)]
    if s in H and spec.include_progression:
        hd=sorted(H[s]);xx=np.array([date.fromisoformat(x).toordinal() for x in hd]);yy=np.array([H[s][x] for x in hd])
        hv=np.interp([ds[t].toordinal() for t in valid],xx,yy,left=0,right=yy[-1])
        G.append(np.log1p(hv)/np.log1p(yy[-1]))
    G=np.array(G).T;project=np.eye(len(valid))-G@np.linalg.pinv(G)
    mapping=np.zeros((len(valid),p))
    for q,t in enumerate(valid):mapping[q,t*cap:(t+1)*cap]=1/(counts[t]/1e5)
    R.extend(project@mapping/spec.growth_regularizer);target.extend(np.zeros(len(valid)))
    R=np.array(R);target=np.array(target)
    # Hard low-2 anchor before the first legal leap, exactly the user assumption.
    E=[];eb=[]
    for t in np.flatnonzero(no_leap):
        delta=B[t,:2].sum()-pre_b[:2].sum()
        if delta< -1e-9:raise ValueError(f'Stable-main assumption infeasible: {ds[t]}')
        rr=np.zeros(p);rr[t*cap:t*cap+2]=1;E.append(rr);eb.append(delta)
    E=np.array(E);eb=np.array(eb)
    # Transfers cannot exceed observed main production; incumbent stays >=0.
    F=[];fb=[]
    for j in range(cap):
        for t in range(n):
            rr=np.zeros(p);rr[np.arange(n)*cap+j]=K[t];rr[t*cap+j]+=1
            F.append(rr);fb.append(B[t,j])
        if closed:
            rr=np.zeros(p);rr[np.arange(n)*cap+j]=kp;F.append(rr);fb.append(float(post[f'tier{j+1}'])/100)
    F=np.array(F);fb=np.array(fb)
    initial=np.maximum(B-pre_b,0)
    for t in np.flatnonzero(no_leap):
        delta=B[t,:2].sum()-pre_b[:2].sum();initial[t,:2]=delta*B[t,:2]/B[t,:2].sum()
    def fun(x):res=R@x-target;return .5*res@res
    def jac(x):return R.T@(R@x-target)
    fit=minimize(fun,initial.ravel(),jac=jac,method='SLSQP',bounds=Bounds(np.zeros(p),B.ravel()),
                 constraints=[LinearConstraint(E,eb,eb),LinearConstraint(F,np.full(len(fb),-np.inf),fb)],
                 options={'maxiter':1500,'ftol':1e-10})
    x=fit.x.reshape(n,cap);trans=K@x
    eq_error=float(np.max(abs(E@fit.x-eb)))
    inequality_error=float(np.max(np.maximum(F@fit.x-fb,0)))
    if not fit.success or eq_error>1e-6 or inequality_error>1e-6:raise RuntimeError((spec.name,s,fit.message,eq_error,inequality_error))
    result=[]
    for t,d in enumerate(ds):
        c=x[t].sum()*100;m=total[t]*100-c
        row=dict(date=str(d),season=s,scenario=spec.name,C_boss=c,M_boss=m,B_total=total[t]*100,
                 C_share=c/(total[t]*100),C_accounts=counts[t] if counts[t] else '',
                 C_mean_per_100k=c/counts[t]*1e5 if counts[t] else '',
                 estimated_transfer_count=transfer_count[t],transferred_production_in_main=trans[t].sum()*100,
                 stage='pre_leap' if no_leap[t] else 'post_leap',cap_tier=cap,season_boss_tier=3)
        fixed_low=(B[t,:2].sum()-pre_b[:2].sum())*100 if no_leap[t] else 0.
        row['assumption_only_share_lower']=fixed_low/(total[t]*100)
        row['assumption_only_share_upper']=(fixed_low+B[t,2:].sum()*100)/(total[t]*100) if no_leap[t] else B[t].sum()/total[t]
        for j in range(7):
            c_j=x[t,j]*100 if j<cap else 0.;b_j=float(sr[t][f'tier{j+1}'])
            row[f'C_tier{j+1}']=c_j;row[f'M_tier{j+1}']=b_j-c_j
        result.append(row)
    diagnostic=dict(scenario=spec.name,season=s,success=bool(fit.success),objective=float(fit.fun),
                    equality_max_error=eq_error,inequality_max_error=inequality_error,n_weeks=n,
                    closure_anchor=post['date'] if post else '',last_share=result[-1]['C_share'],
                    transferred_production_last=result[-1]['transferred_production_in_main'])
    return result,diagnostic

def run():
    OUT.mkdir(exist_ok=True,parents=True);rows,windows,C,A,H,CC=inputs();primary=Assumptions()
    specs=[primary,replace(primary,name='no_transfers',transfer_fraction=0),
           replace(primary,name='all_declines_transfer',transfer_fraction=1),
           replace(primary,name='all_declines_full_productivity',transfer_fraction=1,transferred_productivity=1),
           replace(primary,name='full_productivity_retained',transferred_productivity=1),
           replace(primary,name='main_upper_positive',final_upper_elasticity=.2,high_control_weight=.5),
           replace(primary,name='main_upper_negative',final_upper_elasticity=-.2,high_control_weight=.5),
           replace(primary,name='solo_upper_control',final_upper_elasticity=.2,solo_upper_control=True),
           replace(primary,name='chuchu_population',population_provider='chuchu'),
           replace(primary,name='without_progression',include_progression=False),
           replace(primary,name='weaker_main_bridge',main_tolerance=.3)]
    results=[];diagnostics=[]
    for spec in specs:
        ccounts=C if spec.population_provider=='meaegi' else {**C,**CC}
        for win in windows:
            result,diag=fit_season(spec,win,rows,ccounts,H);results.extend(result);diagnostics.append(diag)
        print(spec.name,'complete',flush=True)
    write(OUT/'scenario_weekly.csv',results);write(OUT/'fit_diagnostics.csv',diagnostics)
    lookup={(r['scenario'],r['date']):r for r in results};by={r['date']:r for r in rows};primary_rows=[]
    for ds,br in by.items():
        if (primary.name,ds) in lookup:r=lookup[(primary.name,ds)].copy()
        else:
            boundary=ds in [w['season_end'] for w in windows]
            r=dict(date=ds,season=0,scenario='primary',C_boss='' if boundary else 0.,
                   M_boss='' if boundary else float(br['B_digitized_constrained']),B_total=float(br['B_digitized_constrained']),
                   C_share='' if boundary else 0.,C_accounts='',C_mean_per_100k='',estimated_transfer_count='',
                   transferred_production_in_main='',stage='end_boundary_unresolved' if boundary else 'outside_season',cap_tier='',season_boss_tier=3)
            r['assumption_only_share_lower']='' if boundary else 0.;r['assumption_only_share_upper']='' if boundary else 0.
            for j in range(1,8):r[f'C_tier{j}']='' if boundary else 0.;r[f'M_tier{j}']='' if boundary else float(br[f'tier{j}'])
        r['A_accounts']=A.get(ds,'');r['M_mean_per_100k']=float(r['M_boss'])/A[ds]*1e5 if r['M_boss']!='' else ''
        shares=[x['C_share'] for x in results if x['date']==ds]
        r['scenario_share_min']=min(shares) if shares else r['C_share'];r['scenario_share_max']=max(shares) if shares else r['C_share']
        primary_rows.append(r)
    write(OUT/'weekly_decomposition.csv',primary_rows)
    summary=[]
    for s in range(1,5):
        rr=[r for r in primary_rows if r['season']==s];last=rr[-1];noleap=[r for r in rr if r['stage']=='pre_leap']
        summary.append(dict(season=s,n_weeks=len(rr),pre_leap_last_date=noleap[-1]['date'],
                            pre_leap_last_share=noleap[-1]['C_share'],last_date=last['date'],last_share=last['C_share'],
                            last_share_scenario_min=last['scenario_share_min'],last_share_scenario_max=last['scenario_share_max'],
                            last_C_mean_per_100k=last['C_mean_per_100k'],last_M_mean_per_100k=last['M_mean_per_100k']))
    write(OUT/'season_summary.csv',summary)
    manifest=dict(cutoff='2026-08-21',last_observation='2026-08-20',season_boss_assignment={'Kai':3,'Meirin':3},
                  no_added_season_boss_mass=True,scenarios=[asdict(x) for x in specs],
                  inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
                      SOURCE/'boss_tier_weekly.csv',SOURCE/'season_identification_windows.csv',
                      SOURCE/'solo_clear_distribution.csv',
                      ROOT/'Maple/data/boss_decomposition_research_20260912/challenger_progression_canonical_s2_s3.csv',
                      ROOT/'Maple/data/challengers_population_weekly_seasons1_4.csv',
                      ROOT/'Maple/data/maple_production_calibration_inputs_weekly.csv',
                      ROOT/'Maple/data/boss_decomposition_research_20260912/chuchu_population_initial_data.json']},
                  scope='User-assumption-conditional tier decomposition; scenario envelopes are not confidence intervals')
    (OUT/'run_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('SUMMARY',json.dumps(summary),flush=True)

if __name__=='__main__':run()
