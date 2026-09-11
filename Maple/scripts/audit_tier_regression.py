"""Observed-data regressions, four-episode meta-summary, and official reverse audit.

Regress observed tiers, NOT the fitted C allocation. Four episodes are not
four randomized studies, and scenarios are never counted as independent studies.
"""
import csv,json,hashlib
import itertools
from datetime import date,timedelta
from pathlib import Path
import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar
from PIL import Image
from digitize_now_20260910 import stack_profile

ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Maple/data/now_20260910';OUT=ROOT/'Maple/data/tier_regression_audit'
def read(p):
    with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(name,rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)

def hac_cov(X,e,positions,lag=4):
    """Bartlett Newey-West using true weekly spacing, including omitted gaps."""
    n,k=X.shape;scores=X*e[:,None];lookup={int(p):i for i,p in enumerate(positions)}
    meat=scores.T@scores
    for h in range(1,lag+1):
        cross=np.zeros((k,k))
        for i,p in enumerate(positions):
            j=lookup.get(int(p)-h)
            if j is not None:cross+=np.outer(scores[i],scores[j])
        meat+=(1-h/(lag+1))*(cross+cross.T)
    bread=np.linalg.inv(X.T@X)
    return bread@meat@bread*n/(n-k)

def regress(y,X,names,pos,label,lag=4):
    if np.linalg.matrix_rank(X)<X.shape[1]:raise ValueError(f'Rank deficient {label}')
    beta=np.linalg.lstsq(X,y,rcond=None)[0];e=y-X@beta;cov=hac_cov(X,e,pos,lag)
    se=np.sqrt(np.maximum(np.diag(cov),0));df=len(y)-X.shape[1];q=stats.t.ppf(.975,df)
    rows=[dict(model=label,term=nm,coefficient=float(b),hac_se=float(s),ci_lower=float(b-q*s),ci_upper=float(b+q*s),
               p_value=float(2*stats.t.sf(abs(b/s),df)) if s>0 else '',n=len(y),df=df,hac_lag_weeks=lag)
          for nm,b,s in zip(names,beta,se)]
    summary=dict(model=label,n=len(y),k=X.shape[1],r_squared=float(1-e@e/np.sum((y-y.mean())**2)),
                 rmse=float(np.sqrt(np.mean(e**2))),condition_number=float(np.linalg.cond(X)),hac_lag_weeks=lag)
    return rows,summary

def panel_regressions():
    bars=read(D/'boss_tier_weekly.csv');windows=read(D/'season_identification_windows.csv')
    dates=[date.fromisoformat(r['date']) for r in bars]
    src={r['date']:r for r in read(ROOT/'Maple/data/maple_production_calibration_inputs_weekly.csv')}
    B=np.array([[float(r[f'tier{j}_raw']) for j in range(1,8)] for r in bars])
    A=np.array([float(src[str(d)]['A_main_accounts']) for d in dates]);C=np.array([float(src[str(d)]['C_challenger_accounts']) for d in dates])
    good=np.array([not any(abs((d-date.fromisoformat(w[k])).days)<=7 for w in windows for k in ['start','season_end']) for d in dates])
    growth_dates={'2025-03-20','2025-07-17','2026-02-12','2026-03-19','2026-07-23'}
    reward_dates={'2025-04-17','2025-10-23'}
    pulse=np.array([float(str(d) in growth_dates) for d in dates]);reward=np.array([float(str(d) in reward_dates) for d in dates])
    dxA=np.diff(np.log(A));dxC=np.diff(np.log1p(C/1e5));dxH=np.diff(np.log1p(B[:,4:].sum(1)/2.944717415))
    mask=good[1:]&good[:-1];pos=np.arange(1,len(dates))[mask]
    rows=[];summaries=[]
    for label,values in [('low2',B[:,:2].sum(1)),('tier3',B[:,2]),('tier4',B[:,3])]:
        transformed=np.log(values) if label=='low2' else np.log1p(values/2.944717415)
        y=np.diff(transformed)[mask]
        for upper in [False,True]:
            x=[np.ones(len(dxA)),dxA,dxC,reward[1:],pulse[1:]]
            names=['intercept','dlog_A','dlog1p_C_100k','reward_pulse','growth_pulse']
            if upper:x.append(dxH);names.append('dlog1p_upper5plus_pixels')
            X=np.array(x).T[mask]
            for lag in [4,8]:
                name=f'{label}_difference'+('_upper_control' if upper else '')+f'_HAC{lag}'
                rr,ss=regress(y,X,names,pos,name,lag);rows.extend(rr);summaries.append(ss)
    # A level regression is descriptive; first differences are the primary specification.
    X=np.column_stack([np.ones(len(dates)),np.log(A),np.log1p(C/1e5),np.arange(len(dates))/52])
    rr,ss=regress(np.log(B[:,:2].sum(1))[good],X[good],['intercept','log_A','log1p_C_100k','linear_time_years'],
                   np.arange(len(dates))[good],'low2_level_trend_HAC4');rows.extend(rr);summaries.append(ss)
    # Separate local opening regression; do not conflate it with the
    # boundary-excluded weekly regression above. Post dummy tests shared patch confounding.
    event_indices=[];event_X=[];event_y=[];event_groups=[]
    for s,w in enumerate(windows):
        start=date.fromisoformat(w['start']);leap=date.fromisoformat(w['first_leap'])
        before=[i for i,d in enumerate(dates) if start-timedelta(weeks=3)<=d<start]
        a0=np.mean(A[before])
        for i,d in enumerate(dates):
            if not start-timedelta(weeks=3)<=d<leap:continue
            post=float(d>=start)
            if post and C[i]==0:continue  # unobserved opening-day C is not a true zero
            fe=[1.]+[float(s==j) for j in [1,2,3]]
            event_X.append(fe+[np.log(A[i]/a0),np.log1p(C[i]/1e5),post]);event_y.append(np.log(B[i,:2].sum()));event_indices.append(i);event_groups.append(s)
    ex=np.array(event_X);ey=np.array(event_y);ep=np.array(event_indices)
    en=['intercept','season2','season3','season4','log_A_over_pre','log1p_C_100k','post_opening']
    wild=[]
    for control_post in [False,True]:
        xx=ex if control_post else ex[:,:-1];nn=en if control_post else en[:-1]
        name='opening_local_FE'+('_post_control' if control_post else '')+'_HAC2'
        rr,ss=regress(ey,xx,nn,ep,name,2)
        rows.extend(rr);summaries.append(ss)
        k=nn.index('log1p_C_100k');observed=rr[k]['coefficient']/rr[k]['hac_se']
        restricted=np.delete(xx,k,axis=1);fitted=restricted@np.linalg.lstsq(restricted,ey,rcond=None)[0];resid=ey-fitted
        statistics=[]
        for signs in itertools.product([-1.,1.],repeat=4):
            ys=fitted+resid*np.array(signs)[event_groups]
            br,_=regress(ys,xx,nn,ep,'bootstrap',2);statistics.append(br[k]['coefficient']/br[k]['hac_se'])
        wild.append(dict(model=name,clusters=4,sign_patterns=16,observed_t=observed,
                         restricted_wild_sign_p=float(np.mean(np.abs(statistics)>=abs(observed)-1e-9)),
                         interpretation='four-event cluster sign sensitivity; not randomization inference from an experiment'))
    write('opening_wild_cluster_sensitivity.csv',wild)
    # BH is exploratory across the predeclared differenced C coefficients only.
    crows=[r for r in rows if r['term']=='dlog1p_C_100k'];order=np.argsort([r['p_value'] for r in crows]);m=len(order)
    adj=np.minimum.accumulate((np.array([crows[i]['p_value'] for i in order])*m/np.arange(1,m+1))[::-1])[::-1]
    qvalues={id(crows[i]):min(float(q),1.) for i,q in zip(order,adj)}
    for r in rows:r['exploratory_BH_q']=qvalues.get(id(r),'')
    write('regression_coefficients.csv',rows);write('regression_models.csv',summaries)
    return bars,windows,A,C

def block_sample(a,rng):
    # Circular 2-week block resampling, retaining within-block temporal order.
    n=len(a);idx=[]
    while len(idx)<n:
        j=int(rng.integers(n));idx.extend([j,(j+1)%n])
    return a[np.array(idx[:n])]

def random_meta(effects,variances):
    k=len(effects)
    def reml(tau):
        v=variances+tau;w=1/v;mu=np.sum(w*effects)/w.sum()
        return .5*(np.sum(np.log(v))+np.log(w.sum())+np.sum(w*(effects-mu)**2))
    opt=minimize_scalar(reml,bounds=(0,2),method='bounded');tau=opt.x if reml(opt.x)<reml(0) else 0.
    w=1/(variances+tau);mu=np.sum(w*effects)/w.sum()
    hk=max(1.,np.sum(w*(effects-mu)**2)/(k-1));se=np.sqrt(hk/w.sum());crit=stats.t.ppf(.975,k-1)
    wf=1/variances;muf=np.sum(wf*effects)/wf.sum();Q=float(np.sum(wf*(effects-muf)**2))
    return dict(k=k,pooled_log_ratio=float(mu),pooled_pct=float(100*np.expm1(mu)),
                ci_lower_pct=float(100*np.expm1(mu-crit*se)),ci_upper_pct=float(100*np.expm1(mu+crit*se)),
                tau_squared=float(tau),I_squared=float(max(0,(Q-(k-1))/Q)) if Q else 0.,
                hk_scale=float(hk),interpretation='Descriptive four-episode synthesis; not independent randomized studies')

def episode_meta(bars,windows,A,C):
    ds=[date.fromisoformat(r['date']) for r in bars];lookup={d:i for i,d in enumerate(ds)}
    L=np.array([float(r['tier1_raw'])+float(r['tier2_raw']) for r in bars]);rng=np.random.default_rng(20260912)
    records=[]
    for w in windows:
        start=date.fromisoformat(w['start']);leap=date.fromisoformat(w['first_leap'])
        pre=np.array([lookup[start-timedelta(weeks=j)] for j in [3,2,1]])
        post=np.array([i for i,d in enumerate(ds) if start<=d<leap])
        effect=np.log(L[post].mean()/L[pre].mean())
        boot=np.array([np.log(block_sample(L[post],rng).mean()/block_sample(L[pre],rng).mean()) for _ in range(3000)])
        records.append(dict(season=int(w['season']),pre_start=str(ds[pre[0]]),post_end=str(ds[post[-1]]),
                            n_pre=3,n_post=len(post),pre_low_mean=L[pre].mean(),post_low_mean=L[post].mean(),
                            log_ratio=float(effect),increase_pct=float(100*np.expm1(effect)),bootstrap_se=float(np.std(boot,ddof=1)),
                            bootstrap_lower_pct=float(100*np.expm1(np.quantile(boot,.025))),
                            bootstrap_upper_pct=float(100*np.expm1(np.quantile(boot,.975))),
                            log_ratio_se_variance=float(np.var(boot,ddof=1)),
                            C_peak_over_pre_A=float(max(C[post])/A[pre[-1]]),fast_genesis=int(w['season'] in ['2','4'])))
    write('opening_episode_effects.csv',records)
    e=np.array([r['log_ratio'] for r in records]);v=np.array([r['log_ratio_se_variance'] for r in records]);meta=random_meta(e,v)
    (OUT/'episode_meta_summary.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    loo=[dict(omitted_season=i+1,**random_meta(np.delete(e,i),np.delete(v,i))) for i in range(4)]
    write('meta_leave_one_season_out.csv',loo)
    metareg=[]
    for term in ['C_peak_over_pre_A','fast_genesis']:
        X=np.column_stack([np.ones(4),[r[term] for r in records]]);ww=1/(v+meta['tau_squared']);bread=np.linalg.inv(X.T@(ww[:,None]*X))
        beta=bread@X.T@(ww*e);res=e-X@beta;hk=max(1.,np.sum(ww*res**2)/2);se=np.sqrt(np.diag(bread)*hk);crit=stats.t.ppf(.975,2)
        metareg.append(dict(predictor=term,slope=beta[1],hk_se=se[1],ci_lower=beta[1]-crit*se[1],ci_upper=beta[1]+crit*se[1],
                            p_value=2*stats.t.sf(abs(beta[1]/se[1]),2),k=4,df=2,interpretation='exploratory single-moderator meta-regression'))
    write('meta_regression.csv',metareg)
    return meta

def official_reverse_audit(bars):
    # Previously unscored 2025 screenshot: pixel extraction independent of 2026 ratios.
    path=next(p for p in ROOT.glob('251016*.png') if '보스별' in p.name)
    im=np.array(Image.open(path).convert('RGB'),dtype=float)
    palette=np.array([np.median(im[y-2:y+3,1186:1197],axis=(0,1)) for y in [309,339,371,401,433,463]])
    old=[]
    for i,x in enumerate(np.linspace(127,1147.5,132)):
        day=date(2025,10,2)-timedelta(weeks=131-i)
        # A black event dash crosses the ASSEMBLE bar. Select the intact
        # contiguous stack among adjacent interior columns, not the darkest base.
        candidates=[]
        for xx in [int(round(x))+z for z in [-1,0,1]]:
            hh,tt,bb=stack_profile(im,xx,757,260,palette);candidates.append((hh.sum(),xx,hh,tt,bb))
        _,xx,heights,top,bottom=max(candidates,key=lambda z:z[0])
        row=dict(date=str(day),x_pixel=xx,height_pixels=float(heights.sum()))
        for j in range(6):row[f'old_tier{j+1}_pixels']=float(heights[j])
        old.append(row)
    write('official_20251016_pixels.csv',old)
    oldby={r['date']:r for r in old};newby={r['date']:r for r in bars}
    overlap=sorted(set(oldby)&set(newby));cal=overlap[:16];test=overlap[16:]
    # Only the early overlap chooses scale; later observations remain held out.
    ox=np.array([oldby[d]['height_pixels'] for d in cal]);ny=np.array([float(newby[d]['B_digitized_raw']) for d in cal])
    scale=float(ox@ny/(ox@ox));comparison=[]
    for d in overlap:
        pred=oldby[d]['height_pixels']*scale;observed=float(newby[d]['B_digitized_raw'])
        comparison.append(dict(date=d,role='scale_calibration' if d in cal else 'held_out_cross_broadcast',
                               old_official_scaled=pred,new_official_raw=observed,relative_difference=observed/pred-1))
    write('cross_broadcast_holdout.csv',comparison)
    h=[r for r in comparison if r['role']=='held_out_cross_broadcast'];p=np.array([r['old_official_scaled'] for r in h]);y=np.array([r['new_official_raw'] for r in h])
    metrics=dict(source=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),old_bars=132,
                 calendar='last bar Oct 2 2025; ASSEMBLE June 19 at x~1031; weekly backwards',
                 calibration_n=len(cal),holdout_n=len(test),scale=scale,holdout_MAPE=float(np.mean(abs(y/p-1))),
                 holdout_r_squared=float(1-np.sum((y-p)**2)/np.sum((y-y.mean())**2)),
                 scope='Aggregate total only. Old/new tier taxonomy not assumed identical.')
    (OUT/'official_holdout_summary.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    broad=[];broad_summary=[]
    for name,oldjs,newjs in [('through_hard_jinhilla',[1,2,3],[1,2]),('above_hard_jinhilla',[4,5,6],[3,4,5,6,7])]:
        for d in test:
            old_value=sum(oldby[d][f'old_tier{j}_pixels'] for j in oldjs)*scale
            new_value=sum(float(newby[d][f'tier{j}_raw']) for j in newjs)
            broad.append(dict(band=name,date=d,old_official_scaled=old_value,new_official_raw=new_value,
                              relative_difference=new_value/old_value-1,
                              crosswalk='broad named threshold only; finer boss membership not assumed identical'))
        rr=[r for r in broad if r['band']==name]
        broad_summary.append(dict(band=name,n=len(rr),MAPE=float(np.mean([abs(r['relative_difference']) for r in rr])),
                                  median_ratio=float(np.median([1+r['relative_difference'] for r in rr]))))
    write('official_broad_band_holdout.csv',broad);write('official_broad_band_summary.csv',broad_summary)
    checks=[]
    for r in read(D/'official_boss_production_growth.csv'):
        checks.append(dict(check='production_YoY',tier=r['tier'],official_multiplier=r['official_multiplier'],
                           reconstructed_raw_multiplier=r['raw_multiplier'],
                           constrained_multiplier=float(r['new_constrained_pixels'])/float(r['old_constrained_pixels']),
                           evidence_class='constraint_reproduction_not_independent_validation'))
    write('official_constraint_audit.csv',checks)
    # Full 2025 printed user distribution, not confused with a production share.
    shares=[[18.64,30.08,36.,10.,5.06,.22],[4.11,13.89,48.94,21.97,10.13,.96]]
    share_rows=[]
    for d,values in zip(['2025-06-12','2025-10-02'],shares):
        for j,vv in enumerate(values):share_rows.append(dict(date=d,old_tier=j+1,share_pct=vv,
             extraction='complement_to_100' if (d=='2025-06-12' and j==4) or (d=='2025-10-02' and j==0) else 'printed_value',
             reverse_prediction_status='not_predictable_from_production_split_without_reward_participation_mapping'))
    write('official_20251016_solo_distribution.csv',share_rows)
    return metrics

def scope_periodicity_regression(bars):
    by={r['date']:r for r in bars};source=[r for r in read(D/'production_by_source_weekly.csv') if r['series']=='boss_rewards' and r['production_index']]
    rows=[]
    for r in source:
        ds=date.fromisoformat(r['date']);weekly=float(by[r['date']]['B_digitized_raw']);reward=float(r['production_index'])
        month=any((ds+timedelta(days=j)).day==1 for j in range(7))
        s4=ds>=date(2026,6,18)
        rows.append(dict(date=r['date'],boss_rewards=reward,weekly_boss_tier_total=weekly,log_ratio=np.log(reward/weekly),
                         week_contains_month_start=int(month),S4=int(s4)))
    X=np.array([[1,r['week_contains_month_start'],r['S4'],r['week_contains_month_start']*r['S4']] for r in rows],float)
    y=np.array([r['log_ratio'] for r in rows]);pos=np.arange(len(rows))
    coefs=[];summ=[]
    for lag in [4,8]:
        c,s=regress(y,X,['intercept','month_start','S4','month_start_x_S4'],pos,f'boss_scope_log_ratio_HAC{lag}',lag);coefs.extend(c);summ.append(s)
    write('boss_scope_periodicity_observations.csv',rows);write('boss_scope_periodicity_regression.csv',coefs);write('boss_scope_periodicity_models.csv',summ)

def run():
    OUT.mkdir(exist_ok=True,parents=True);bars,windows,A,C=panel_regressions();meta=episode_meta(bars,windows,A,C)
    audit=official_reverse_audit(bars);scope_periodicity_regression(bars)
    manifest=dict(seed=20260912,regression_outcome='observed RAW tier amounts, not estimated Challenger allocations',
                  primary_regression='low2_difference_upper_control_HAC4',
                  meta_sampling='3 pre-weeks vs 4/5 no-leap weeks; circular 2-week bootstrap, 3000 draws; REML modified HK',
                  assumptions='Four seasons descriptive; contemporaneous patches/confounding remain. Official imposed rates are not holdouts.',
                  official= audit,meta=meta,
                  source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
                      D/'boss_tier_weekly.csv',D/'official_boss_production_growth.csv',D/'solo_clear_distribution.csv',
                      D/'season_identification_windows.csv',ROOT/'Maple/data/maple_production_calibration_inputs_weekly.csv',
                      D/'production_by_source_weekly.csv',
                      ROOT/'251016 보스격파율.png',
                      ROOT/'Maple/data/tier_boss_decomposition_v1/weekly_decomposition.csv']})
    import platform,scipy,statsmodels
    manifest['runtime']={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'statsmodels':statsmodels.__version__}
    manifest['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (OUT/'run_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('META',json.dumps(meta));print('OFFICIAL',json.dumps(audit))
    for r in read(OUT/'regression_coefficients.csv'):
        if r['term']=='dlog1p_C_100k' and r['model'].endswith('HAC4'):print('REGRESSION',r)

if __name__=='__main__':run()
