# Per-capita meso production V2 — endogenous patch contamination removed

## Status

This is the second-pass calibration for

\[
Q_t=\frac{P_t}{E_t},\qquad E_t=A_t+w_tC_t.
\]

V1 is preserved as a historical first pass. V2 changes only the identification issue exposed by the independent Challenger-progression validation: **a within-season patch multiplier must not be estimated from the mixed series `B_t/A_t` while Challenger is open.**

Progression data are not used to fit V2. They are used only after the V2 series has been generated.

Primary output:

`Maple/data/per_capita_production_v2_weekly.csv`

## V1 arithmetic audit / erratum

The stored historical file `Maple/data/per_capita_production_final_weekly.csv` contains a selective arithmetic inconsistency in some Challenger rows: its stored `muC_residual` is not always equal to

\[
(B_t-A_t\widehat{\mu_t^M})/C_t.
\]

For example, the stored 2026-01-15 row has `B=53.4142215898`, `A=284602`, `muM_counterfactual=0.000166571312981`, and `C=234425`; those inputs imply `muC≈2.563e-05`, not the stored `0.000123781...`.

Therefore the stored V1 CSV is retained only as a historical artifact. Model sensitivity in this document uses a **V1-recomputed comparator** obtained by applying the counterfactual rules stated in `PER_CAPITA_PRODUCTION_METHOD.md` and then recomputing every residual row from the identity above.

This also resolves the apparent Season-3 maximum discrepancy: the correctly recomputed documented V1 model has `max w = 0.744439639` on 2026-02-26. The `0.797` value visible in the historical CSV is not a valid output of the documented V1 calculation.

## V2 counterfactual specification

### Common residual identity

For every Challenger week,

\[
\mu^C_{t,raw}=\frac{B_t-A_t\widehat{\mu_t^M}}{C_t},
\qquad
w_{t,raw}=\frac{\mu^C_{t,raw}}{\widehat{\mu_t^M}}.
\]

No progression statistic enters this calculation.

### Season 1 — boundary bridge + external 2025-04-17 crystal factor

The pure-main anchors remain 2024-12-12 and 2025-05-22. The endogenous V1 multiplier is removed.

The 2025-04-17 update directly changed boss-crystal prices, so a reward-table intervention is conceptually warranted. Official before/after crystal prices are in the live update:

- https://maplestory.nexon.com/news/update/768

For this V2 first pass the external factor is

\[
r_{2025-04-17}=0.919031579.
\]

This factor is **provisional**. It is not estimated from mixed `B/A`. It is a coarse reward-mix approximation using the pre-patch 2025-03-31 aggregate tier-production estimates (39.7, 44.0, 43.7, 42.7, 59.7, 110 trillion meso; reported total about 380 trillion) together with the official direction/magnitude of the reward-table changes. The aggregate tier source is:

- https://www.inven.co.kr/board/maple/5974/5802009

The exact pre-patch boss-by-boss main-world production shares are not currently available in machine-readable form, so this factor is explicitly lower-confidence than the 2025-10-23 factor. It must not be presented as an official aggregate multiplier.

### Season 2 — boundary bridge + external 2025-10-23 crystal factor

The pure-main anchors remain 2025-06-19 and 2025-11-27. The endogenous V1 multiplier is removed.

The 2025-10-23 patch directly changed crystal rewards. Official prices are in:

- https://maplestory.nexon.com/news/update/786

An independent aggregate route/tier calculation reports pre-patch production potential of about 779 trillion and post-patch about 611 trillion using the same character-tier population base. Therefore V2 uses

\[
r_{2025-10-23}=\frac{611}{779}=0.7843388960.
\]

Source:

- https://www.inven.co.kr/board/maple/5974/5802009

This is a community aggregate model rather than an official total-production statistic, but unlike V1 it is external to the mixed `B/A` residual being estimated. As an additional composition check, the October Maple NOW summary reported that Hard Damien and above contributed roughly 80% of crystal meso production and the `검밑솔` band alone about 50% at that time:

- https://www.inven.co.kr/board/maple/5974/5782167

### Season 3 — boundary bridge only

The pure-main anchors are 2025-12-18 and 2026-04-23. V2 removes the 2026-01-15 Azmoth-removal multiplier entirely.

Azmoth removal was not a direct mechanical change to boss-crystal rewards, and the V1 factor `1.101369081` was inferred from a mixed series. The V2 bridge is therefore a single additive linear bridge with no within-season jump.

Fitted weekly drift:

\[
g_3=3.589998750\times10^{-6}.
\]

### Season 4 — pre-season local trend only

The anchor remains the pure-main 2026-06-18 post-OVERDRIVE-1 observation. V2 extends the previously estimated pre-season local slope

\[
g_4=3.696182499\times10^{-6}\text{ per week}
\]

without any multiplier at OVERDRIVE 2 or 3.

The 2026-07-23 and 2026-08-20 rows are flagged `uncertain_growth_intervention=True`. They are not given endogenous level jumps.

## Boundary identification failures

V2 does not convert an infeasible residual into an economic `w=0`.

The unconstrained `w_raw` is retained. If `w_raw<0`, then:

- `identification_failed_boundary=True`;
- canonical `muC_residual` and `w_challenger_main_equiv` are `NA`;
- canonical `E_effective_accounts` and `Q_raw` are `NA` for that row;
- `w_plot` is a separate linear interpolation used only to draw a continuous presentation series;
- `E_effective_accounts_plot`, `Q_raw_plot`, and the displayed normalized index use `w_plot`.

The same three boundary-sensitive weeks fail in V2:

- 2024-12-19
- 2025-04-24
- 2025-11-20

They must be interpreted as **decomposition not identified for that week**, not as zero Challenger production.

## Season-level V1 vs V2 summary

V1 values below are from the documented V1 model recomputed row-by-row, not from the arithmetic-inconsistent historical CSV.

| season | V1 median w | V2 median w | V2 C-weighted mean w | V2 min | V2 max | failed weeks |
|---|---:|---:|---:|---:|---:|---:|
| Season 1 | 0.2291 | 0.3091 | 0.2856 | 0.0060 | 0.6435 | 2 |
| Season 2 | 0.5087 | 0.4601 | 0.3955 | 0.0880 | 0.7074 | 1 |
| Season 3 | 0.3259 | 0.3625 | 0.3590 | 0.0051 | 0.8387 | 0 |
| Season 4 | 0.3567 | 0.5022 | 0.3890 | 0.1536 | 0.6814 | 0 |

The account-weighted statistic is

\[
\bar w_s^{(C)}=\frac{\sum_{t\in s}C_tw_t}{\sum_{t\in s}C_t},
\]

computed over valid canonical weeks only.

## Independent progression re-validation

No progression information was used above.

### Season 2 — substantially improved, provisional pass

Aggregate daily Challenger-attainment data are available at:

- https://www.inven.co.kr/board/maple/2304/46432

The V1 early-season trajectory contained an implausibly large apparent July spike. Under V2:

- 2025-06-26: `w=0.088`
- 2025-07-03: `0.231`
- 2025-07-10: `0.277`
- 2025-07-17: `0.384`
- 2025-07-31: `0.460`

Thus the abnormal early-July/high-0.7 behavior disappears. The late October jump remains (`w≈0.707` on 2025-10-23), but it now comes from an external reward-table intervention rather than a multiplier read from mixed `B/A`.

Verdict: **provisional pass / materially improved**. The overall level still deserves reward-tier validation, but the main early-season falsification is removed.

### Season 3 — jump fixed, late contradiction remains

Aggregate Challenger cumulative anchors previously extracted from the day-by-day table include approximately:

- 2026-01-01: 20
- 2026-01-15: 246
- 2026-01-29: 1,017
- 2026-02-12: 2,220
- 2026-02-26: 3,788
- 2026-03-12: 8,290
- 2026-03-26: 13,307
- 2026-04-15: 20,990

Removing the Azmoth multiplier fixes the artificial 2026-01-15 discontinuity: V2 has `w=0.260`, not the V1 jump generated by the endogenous multiplier.

However the trajectory still reaches `w=0.839` on 2026-02-26 and then declines to `0.148` by 2026-04-16 while the upper-tail attainment count and weak-account attrition move strongly in the opposite direction. Challenger attainment is only a tail statistic, so monotonicity is not imposed; nevertheless this reversal remains large enough to require an explanation.

Verdict: **validation fail, although the specific 1/15 contamination is fixed**. Season 3 is now the highest-priority residual-identification problem.

### Season 4 — broad trend supported, 7/30 spike persists

Independent rank/count snapshots:

- 2026-07-25: over 40k Challenger — https://www.inven.co.kr/board/maple/5974/6939414
- 2026-08-11: rank 100,000 reached — https://www.inven.co.kr/board/maple/5974/7014203
- 2026-08-30: about 155k — https://www.inven.co.kr/board/maple/5974/7108291
- 2026-09-11: 189,391, user-confirmed

V2 without OVD2/OVD3 multipliers gives:

`0.154 → 0.178 → 0.185 → 0.229 → 0.343 → 0.681 → 0.502 → 0.510 → 0.539 → 0.591 → 0.607`.

The broad rise is compatible with the progression snapshots. But the 2026-07-30 spike to `0.681` remains and is actually clearer once the endogenous OVD2 jump is removed. Therefore that transient cannot be blamed on the V1 OVD2 multiplier; it comes from the observed boss-production residual structure or another unmodeled intervention.

Verdict: **provisionally supported at the broad-trend level; 7/30 remains unresolved**.

## Q sensitivity: does the economic conclusion survive?

`Q_index_sep2025_100` in V2 is normalized to the September-2025 mean of the V2 plotting series. Because V1 and V2 have different September denominators, model sensitivity should also be compared in raw `Q`.

Selected points:

| date | V1-recomputed index | V2 index | V2 vs V1 raw Q |
|---|---:|---:|---:|
| 2025-06-12 | 69.72 | 65.28 | 0.0% |
| 2025-06-26 | 85.31 | 80.47 | +0.7% |
| 2026-01-15 | 118.39 | 102.92 | -7.2% |
| 2026-02-26 | 121.61 | 109.63 | -3.7% |
| 2026-06-25 | 169.07 | 158.30 | 0.0% |
| 2026-07-30 | 192.66 | 161.50 | -10.5% |
| 2026-08-20 | 205.72 | 170.54 | -11.5% |
| 2026-09-03 | 210.28 | 174.80 | -11.2% |

The maximum absolute raw-Q difference on Challenger weeks in this V1↔V2 comparison is about **11.5%**, at 2026-08-20.

Thus denominator calibration is materially important, especially in the open-ended Season 4. But the long-run result survives: even under V2 the latest displayed index is about **175 versus September 2025 = 100**. The conclusion that total-production growth is not explained by population exposure alone is therefore robust to this specific contamination fix, while its exact late-2026 magnitude is not yet final.

## Current interpretation

The public-facing label may remain “1인당 메소 생산량” for readability, but the definition must be stated at least once as:

> **본섭 평균 계정 생산능력으로 보정한 유효 생산계정당 메소 생산량**

or equivalently “meso production per main-world-equivalent effective production account.”

## What V2 does and does not establish

V2 successfully removes the identification contamination that motivated this revision. It does **not** make every within-season residual smooth, nor should it be tuned to do so.

The remaining problems are informative:

1. Season 2 is much more progression-compatible after the correction.
2. Season 3 still has a large mid-season high and late collapse; this is not explained by the removed Azmoth multiplier.
3. Season 4 still has a 7/30 transient despite removing OVD2/3 multipliers; therefore that spike has another source.
4. The long-run rise in adjusted per-capita production remains robust, but late-2026 levels retain roughly 10%+ model sensitivity.

The next step should diagnose the remaining Season-3 and 7/30 residuals before adding any further counterfactual degrees of freedom.