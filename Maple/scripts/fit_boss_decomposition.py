"""Reproducible, conditional joint boss-production decomposition.

No V1/V2/V3 parameter or output is an input. Gaussian log-observation model
and explicit Gaussian regularizers give a MAP fit; Laplace intervals are
conditional approximations, not identification bounds or MCMC posteriors.
"""
import csv
import hashlib
import json
from dataclasses import dataclass, asdict, replace
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Maple/data/boss_decomposition_research_20260912'
OUT = ROOT / 'Maple/data/boss_decomposition_joint_v1'
CUTOFF = date(2026, 8, 21)
SCALE = 6.495250069  # shared source-index -> original NEW AGE chart scale
SEASONS = [('2024-12-19', '2025-05-22'), ('2025-06-19', '2025-11-20'),
           ('2025-12-18', '2026-04-16'), ('2026-06-18', '2026-09-17')]
JUMPS = ['2024-12-19', '2025-06-19', '2025-12-18', '2026-06-18',
         '2025-03-20', '2025-07-17', '2026-02-12', '2026-03-19', '2026-07-23']
CJUMPS = [(0, '2025-03-20'), (1, '2025-07-17'), (2, '2026-02-12'),
          (2, '2026-03-19'), (3, '2026-07-23')]


def read_csv(path):
    with path.open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def interpolation_basis(x, knots):
    return np.column_stack([np.interp(x, knots, v) for v in np.eye(len(knots))])


@dataclass(frozen=True)
class Spec:
    name: str = 'basic'
    inflow: bool = False
    progression: bool = False
    provider: str = 'meaegi'
    lag: int = 0  # A/C reference date relative to B, in weeks
    world4: bool = True
    main_sd: float = .25  # log curvature over 12-week knots
    challenger_sd: float = .7
    jump_sd: float = .35
    reward_c: bool = True
    recovery_weeks: float = 2.


def load(spec):
    rows = read_csv(SOURCE / 'boss_input_through_20260821.csv')
    dates = [date.fromisoformat(r['date']) for r in rows]
    source_dates = {d: i for i, d in enumerate(dates)}
    A0 = np.array([float(r['A_main_accounts']) for r in rows])
    C0 = np.array([float(r['C_challenger_accounts']) for r in rows])
    ch = json.loads((SOURCE / 'chuchu_population_initial_data.json').read_text(encoding='utf-8'))
    ch_by_date = {}
    for key in ['populationChallenger', 'populationChallenger2', 'populationChallenger3']:
        for r in ch[key]:
            d = date.fromisoformat(r['date'])
            if d <= CUTOFF:
                ch_by_date[d] = sum(v['changedCount'] for world, v in r['worlds'].items()
                                    if spec.world4 or world != '챌린저스4')
    A, C, sid, flags = [], [], [], []
    for i, d in enumerate(dates):
        ref = d + timedelta(weeks=spec.lag)
        flag = []
        k = next((s for s, (a, b) in enumerate(SEASONS)
                  if date.fromisoformat(a) <= ref < date.fromisoformat(b)), -1)
        if ref not in source_dates or ref > CUTOFF:
            a, c = A0[i], C0[i]
            flag.append('no_shifted_population_observation')
        else:
            j = source_dates[ref]
            a, c = A0[j], C0[j]
        if k >= 1 and spec.provider == 'chuchu':
            if ref in ch_by_date:
                c = ch_by_date[ref]
            else:
                flag.append('missing_chuchu_observation')
        if k >= 0 and c == 0:
            flag.append('season_open_missing_count_not_zero')
        if k < 0:
            c = 0.
        # Exclude all near-boundary rows from fitting, rather than use them as clean anchors.
        if any(abs((d - date.fromisoformat(s)).days) <= 7 for pair in SEASONS for s in pair):
            flag.append('boundary_window_excluded')
        A.append(a); C.append(c); sid.append(k); flags.append('|'.join(flag))
    A, C, sid = np.array(A) / 1e5, np.array(C) / 1e5, np.array(sid)
    B = np.array([float(r['B_boss_newage100']) for r in rows]) * SCALE
    sigma = np.array([.10 if r['boss_source'] == 'conditional_backcast' else .05 for r in rows])
    train = np.array([not f for f in flags])
    valid = np.array(['missing' not in f and 'no_shifted' not in f for f in flags])
    # Canonical values are used unchanged. Interpolation is a model covariate,
    # never written back as an additional canonical observation.
    H = np.zeros(len(rows)); observed_H = np.full(len(rows), np.nan)
    canon = read_csv(SOURCE / 'challenger_progression_canonical_s2_s3.csv')
    for s in [1, 2]:
        rr = [r for r in canon if r['season'] == f'season{s+1}' and r['challenger_count']]
        dd = np.array([date.fromisoformat(r['date']).toordinal() for r in rr])
        hh = np.array([float(r['challenger_count']) for r in rr])
        for i, d in enumerate(dates):
            ref = d + timedelta(weeks=spec.lag)
            if sid[i] == s and dd.min() <= ref.toordinal() <= dd.max():
                H[i] = np.log1p(np.interp(ref.toordinal(), dd, hh)) / np.log1p(hh[-1])
            if ref.toordinal() in dd:
                observed_H[i] = hh[np.where(dd == ref.toordinal())[0][0]]
    return dict(rows=rows, dates=dates, A=A, C=C, B=B, sigma=sigma, sid=sid,
                flags=flags, train=train, valid=valid, H=H, observed_H=observed_H)


class Model:
    def __init__(self, spec):
        self.spec = spec
        self.d = d = load(spec)
        n = len(d['dates']); t = np.arange(n, dtype=float)
        knots = np.unique(np.r_[np.arange(0, n, 12), n-1]).astype(float)
        base = interpolation_basis(t, knots); nm = len(knots)
        jumps = np.array([[float(day >= date.fromisoformat(j)) for j in JUMPS]
                          for day in d['dates']])
        Cbasis = np.zeros((n, 16))
        for s, (start, end) in enumerate(SEASONS):
            a, b = date.fromisoformat(start), date.fromisoformat(end)
            age = np.array([((day + timedelta(weeks=spec.lag)) - a).days / (b-a).days
                            for day in d['dates']])
            Cbasis[:, 4*s:4*s+4] = interpolation_basis(age, [0, 1/3, 2/3, 1]) * (d['sid'] == s)[:, None]
        p = nm + len(JUMPS) + 16 + len(CJUMPS) + int(spec.inflow) + 2*int(spec.progression)
        M = np.zeros((n, p)); C = np.zeros((n, p))
        M[:, :nm] = base; M[:, nm:nm+len(JUMPS)] = jumps
        self.cstart = nm + len(JUMPS)
        C[:, self.cstart:self.cstart+16] = Cbasis
        at = self.cstart+16
        for season, ds in CJUMPS:
            C[:, at] = np.array([float(day >= date.fromisoformat(ds) and d['sid'][i] == season)
                                  for i, day in enumerate(d['dates'])]); at += 1
        if spec.inflow:
            growth = np.maximum(np.r_[0, np.diff(np.log(d['A']))], 0)
            filtered = growth.copy()
            for i in range(1, n):
                filtered[i] += np.exp(-1/spec.recovery_weeks) * filtered[i-1]
            M[:, at] = filtered; at += 1
        if spec.progression:
            for s in [1, 2]:
                C[:, at] = d['H'] * (d['sid'] == s); at += 1
        self.M, self.C = M, C
        self.rm = np.array([sum(np.log(f) for ds, f in [('2025-04-17', .919031579), ('2025-10-23', .784338896)]
                               if day >= date.fromisoformat(ds)) for day in d['dates']])
        self.rc = np.zeros(n)
        if spec.reward_c:
            for s, ds, f in [(0, '2025-04-17', .919031579), (1, '2025-10-23', .784338896)]:
                self.rc += np.array([np.log(f) if d['sid'][i] == s and day >= date.fromisoformat(ds) else 0.
                                     for i, day in enumerate(d['dates'])])
        # Explicit weak log-level priors and curvature penalties; no V3 anchors.
        prior = np.zeros(p); prior[:nm] = np.log(100); prior[self.cstart:self.cstart+16] = np.log(50)
        R = np.diag(np.full(p, 1/3.))
        R[nm:self.cstart, nm:self.cstart] = np.eye(len(JUMPS))/spec.jump_sd
        cj = slice(self.cstart+16, self.cstart+16+len(CJUMPS))
        R[cj, cj] = np.eye(len(CJUMPS))/spec.jump_sd
        extra = []
        for block, sd in [(list(range(nm)), spec.main_sd)] + [
                (list(range(self.cstart+4*s, self.cstart+4*s+4)), spec.challenger_sd) for s in range(4)]:
            for i in range(len(block)-2):
                row = np.zeros(p); row[block[i:i+3]] = np.array([1., -2., 1.])/sd; extra.append(row)
        self.R = np.vstack([R, extra]); self.target = np.r_[R @ prior, np.zeros(len(extra))]
        self.initial = prior

    def predict(self, theta):
        m = np.exp(self.M @ theta + self.rm)
        c = np.exp(self.C @ theta + self.rc)
        bm = self.d['A']*m; bc = self.d['C']*c
        return m, c, bm+bc, bc/(bm+bc)

    def fit(self, mask=None, y=None, initial=None, profile=None):
        d = self.d; mask = d['train'] if mask is None else mask
        y = d['B'] if y is None else y
        def residual(theta):
            _, _, pred, share = self.predict(theta)
            z = np.r_[(np.log(pred[mask])-np.log(y[mask]))/d['sigma'][mask], self.R@theta-self.target]
            if profile is not None:
                ix, goal = profile
                z = np.r_[z, (share[ix]-goal)/.0001]
            return z
        def jac(theta):
            _, _, pred, share = self.predict(theta)
            J = (1-share[:, None])*self.M + share[:, None]*self.C
            J = np.vstack([J[mask]/d['sigma'][mask, None], self.R])
            if profile is not None:
                ix, _ = profile
                J = np.vstack([J, share[ix]*(1-share[ix])*(self.C[ix]-self.M[ix])/.0001])
            return J
        fit = least_squares(residual, self.initial if initial is None else initial, jac=jac,
                            max_nfev=600, ftol=1e-9, xtol=1e-9, gtol=1e-7)
        return fit


def metrics(model, fit):
    d = model.d; m, c, b, share = model.predict(fit.x); mask=d['train']
    return dict(name=model.spec.name, success=bool(fit.success), n_train=int(mask.sum()),
                parameter_count=len(fit.x), log_rmse=float(np.sqrt(np.mean(np.log(b[mask]/d['B'][mask])**2))),
                objective=float(2*fit.cost), endpoint_valid=bool(d['valid'][-1]),
                endpoint_share=float(share[-1]) if d['valid'][-1] else '',
                endpoint_bM=float(m[-1]) if d['valid'][-1] else '',
                endpoint_bC=float(c[-1]) if d['valid'][-1] else '', nfev=fit.nfev)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    specs = [Spec(), Spec(name='inflow', inflow=True),
             Spec(name='progression', inflow=True, progression=True)]
    fitted=[]; scores=[]; cvrows=[]
    for spec in specs:
        model=Model(spec)
        starts=[model.initial, model.initial+np.random.default_rng(11).normal(0,.2,len(model.initial)),
                model.initial+np.random.default_rng(29).normal(0,.2,len(model.initial))]
        start_fits=[model.fit(initial=x) for x in starts]
        fit=min(start_fits,key=lambda x:x.cost); metric=metrics(model,fit)
        metric['multistart_objective_range']=float(max(x.cost for x in start_fits)*2-min(x.cost for x in start_fits)*2)
        # Reconstruction CV: contiguous held-out B blocks; observed H covariate remains available.
        for lo in [25, 56, 78, 94, 110, 130]:
            test=np.zeros(len(model.d['B']),dtype=bool); test[lo:lo+6]=True; test &= model.d['train']
            if not test.any(): continue
            mask=model.d['train'] & ~test; cv=model.fit(mask=mask)
            pred=model.predict(cv.x)[2]
            cvrows.append(dict(model=spec.name, first=model.d['dates'][lo].isoformat(), n=int(test.sum()),
                               squared_log_error=float(np.sum(np.log(pred[test]/model.d['B'][test])**2)),
                               success=bool(cv.success)))
        relevant=[x for x in cvrows if x['model']==spec.name]
        metric['cv_log_rmse']=float(np.sqrt(sum(x['squared_log_error'] for x in relevant)/sum(x['n'] for x in relevant)))
        fitted.append((model,fit)); scores.append(metric);print('CANDIDATE',metric,flush=True)
    best=min(range(3),key=lambda i:scores[i]['cv_log_rmse'])
    # Prefer a simpler candidate within 2% of minimum CV error, fixed before fitting.
    chosen=next(i for i in range(3) if scores[i]['cv_log_rmse']<=scores[best]['cv_log_rmse']*1.02)
    model,fit=fitted[chosen]; spec=model.spec
    # All documented scenarios are kept, not filtered for attractive trajectories.
    scenarios=[replace(spec,name='chuchu_C',provider='chuchu'),
               replace(spec,name='chuchu_C_without_world4',provider='chuchu',world4=False),
               replace(spec,name='population_lag_minus1',lag=-1),
               replace(spec,name='population_lag_plus1',lag=1),
               replace(spec,name='flexible_main',main_sd=.5,jump_sd=.7),
               replace(spec,name='stiff_main',main_sd=.125,jump_sd=.175),
               replace(spec,name='challenger_reward_unchanged',reward_c=False)]
    allfits=fitted.copy()
    for ss in scenarios:
        mo=Model(ss); ff=mo.fit(); allfits.append((mo,ff));print('SCENARIO',metrics(mo,ff),flush=True)
    write_csv(OUT/'model_comparison.csv',scores);write_csv(OUT/'blocked_reconstruction_cv.csv',cvrows)
    write_csv(OUT/'scenario_summary.csv',[metrics(mo,ff) for mo,ff in allfits])
    # Conditional Gaussian/Laplace approximation to the fitted posterior curvature.
    rng=np.random.default_rng(20260912)
    hess=fit.jac.T@fit.jac; vals,vecs=np.linalg.eigh(hess)
    draws=fit.x+rng.normal(size=(1500,len(fit.x)))@(vecs@np.diag(1/np.sqrt(np.maximum(vals,1e-12)))).T
    samples=np.array([model.predict(x)[3] for x in draws]); low,high=np.quantile(samples,[.05,.95],axis=0)
    scenario_shares=np.array([np.where(mo.d['valid'],mo.predict(ff.x)[3],np.nan) for mo,ff in allfits])
    d=model.d; m,c,b,share=model.predict(fit.x)
    rows=[]; scenario_rows=[]
    for i,day in enumerate(d['dates']):
        valid=d['valid'][i]
        # Reconciliation is explicit: allocations of OBSERVED B use fitted shares.
        # It is not an independent goodness-of-fit test.
        bm=d['B'][i]*(1-share[i]);bc=d['B'][i]*share[i]
        rows.append(dict(date=day.isoformat(),selected_model=spec.name,B_observed=d['B'][i],B_fitted=b[i],
                         bM_fitted_per_100k=m[i] if valid else '',bC_fitted_per_100k=c[i] if valid and d['C'][i]>0 else '',
                         B_main_reconciled=bm if valid else '',B_challenger_reconciled=bc if valid else '',
                         bM_reconciled_per_100k=bm/d['A'][i] if valid else '',
                         bC_reconciled_per_100k=bc/d['C'][i] if valid and d['C'][i]>0 else '',
                         challenger_share=share[i] if valid else '',conditional_laplace_p05=low[i] if valid else '',
                         conditional_laplace_p95=high[i] if valid else '',scenario_min=float(np.nanmin(scenario_shares[:,i])),
                         scenario_max=float(np.nanmax(scenario_shares[:,i])),A_accounts=d['A'][i]*1e5,C_accounts=d['C'][i]*1e5,
                         season=int(d['sid'][i]+1),in_fit=bool(d['train'][i]),alignment_note=d['flags'][i],
                         canonical_challenger_count=d['observed_H'][i] if np.isfinite(d['observed_H'][i]) else '',
                         boss_source=d['rows'][i]['boss_source']))
        for mo,ff in allfits:
            mm,cc,bb,ss=mo.predict(ff.x)
            scenario_rows.append(dict(date=day.isoformat(),model=mo.spec.name,valid=bool(mo.d['valid'][i]),
                                      share=ss[i] if mo.d['valid'][i] else '',B_fitted=bb[i]))
    write_csv(OUT/'weekly_decomposition.csv',rows);write_csv(OUT/'scenario_weekly.csv',scenario_rows)
    # Profile both early and final S4 shares: data fit versus prior/penalty fit.
    profiles=[]
    for target in ['2026-03-26','2026-08-20']:
        ix=d['dates'].index(date.fromisoformat(target))
        for goal in [.05,.15,.25,.35,.45,.55,.65,.75]:
            pf=model.fit(initial=fit.x,profile=(ix,goal));met=metrics(model,pf)
            profiles.append(dict(date=target,target_share=goal,achieved_share=float(model.predict(pf.x)[3][ix]),
                                 log_rmse=met['log_rmse'],penalized_objective=met['objective'],success=met['success']))
    write_csv(OUT/'share_profile.csv',profiles)
    # Synthetic recovery: generated model truth, and a different split with IDENTICAL total.
    synthetic=[]; true_b=b.copy(); cshare=share.copy()
    noises=[np.convolve(rng.normal(0,d['sigma']),[.25,.5,.25],mode='same') for _ in range(8)]
    for label,true_share in [('model_truth',cshare),('equivalent_split',np.where(d['C']>0,.5*cshare+.20,0.))]:
        for rep in range(8):
            noise=noises[rep]
            simulated=true_b*np.exp(noise); sf=model.fit(y=simulated,initial=fit.x)
            got=model.predict(sf.x)[3];mask=d['train']&(d['C']>0)
            synthetic.append(dict(truth=label,replicate=rep,mean_abs_share_error=float(np.mean(abs(got[mask]-true_share[mask]))),
                                  max_abs_share_error=float(np.max(abs(got[mask]-true_share[mask]))),success=bool(sf.success)))
    write_csv(OUT/'synthetic_recovery.csv',synthetic)
    season_rows=[]
    for s in range(4):
        mask=(d['sid']==s)&d['valid']&d['train']
        season_rows.append(dict(season=s+1,valid_interior_weeks=int(mask.sum()),
                                boss_weighted_challenger_share=float(np.sum(d['B'][mask]*share[mask])/np.sum(d['B'][mask])),
                                A_weighted_bM_per_100k=float(np.sum(d['B'][mask]*(1-share[mask]))/np.sum(d['A'][mask])),
                                C_weighted_bC_per_100k=float(np.sum(d['B'][mask]*share[mask])/np.sum(d['C'][mask]))))
    write_csv(OUT/'season_summary.csv',season_rows)
    # Historical comparator is read only AFTER every new fit and diagnostic.
    old_path=ROOT/'Maple/data/per_capita_production_v3_weekly.csv'
    old={r['date']:r for r in read_csv(old_path)}
    comparison=[]
    for r in rows:
        vr=old[r['date']]; aw=float(vr['A_effective_main_accounts'])
        cw=float(vr['C_challenger_accounts']); ww=float(vr['w_v3'])
        old_share=cw*ww/(aw+cw*ww)
        comparison.append(dict(date=r['date'],joint_challenger_share=r['challenger_share'],
                               v3_implied_challenger_share=old_share,note='Comparator only; never used in fitting'))
    write_csv(OUT/'v3_comparison.csv',comparison)
    diagnostics=dict(selected=asdict(spec),cutoff=CUTOFF.isoformat(),last_joint_week=d['dates'][-1].isoformat(),
                     scale=SCALE,conditional_interval='90% Laplace; not identification bounds; conditional Gaussian assumptions',
                     hessian_condition=float(vals.max()/vals.min()),data_fit_and_decomposition_identification_are_separate=True,
                     inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [
                         SOURCE/'boss_input_through_20260821.csv',SOURCE/'challenger_progression_canonical_s2_s3.csv',
                         SOURCE/'chuchu_population_initial_data.json']},
                     specs=[asdict(mo.spec) for mo,ff in allfits])
    import scipy, platform
    diagnostics['runtime']={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}
    diagnostics['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    diagnostics['assessment']='WEAK_IDENTIFICATION; conditional point estimates are not new canonical truth'
    (OUT/'run_manifest.json').write_text(json.dumps(diagnostics,indent=2),encoding='utf-8')
    np.savez_compressed(OUT/'fit_parameters.npz',theta=fit.x,hessian=hess)
    print('SELECTED',spec.name,'endpoint',share[-1],'conditional',low[-1],high[-1],
          'scenario',np.nanmin(scenario_shares[:,-1]),np.nanmax(scenario_shares[:,-1]),flush=True)


if __name__=='__main__':
    run()
