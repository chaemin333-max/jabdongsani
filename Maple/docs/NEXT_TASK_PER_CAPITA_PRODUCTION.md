# NEXT TASK — Final per-capita meso production series

## 0. Objective hierarchy — do not change
The current target is **not** a new Challenger-economy model. The deliverable is the single time series

\[
Q_t = \frac{P_t}{E_t},\qquad E_t=A_t+w_tC_t.
\]

- `P_t`: already reconstructed total meso production.
- `A_t`: main-world active-account proxy from Meaegi `group1` (Eos/Helios excluded).
- `C_t`: Challenger active-account proxy from Meaegi `all-burning-character` (one Item Burning character per account).
- `w_t`: Challenger account production capacity relative to an average main-world account.
- `E_t`: production-capacity-adjusted population, measured in main-account equivalents.

Residual decomposition exists only to calibrate `w_t`.

## 1. Inputs to use — do not reconstruct again
Start from these repository files only:

1. `Maple/data/maple_production_calibration_inputs_weekly.csv`
   - single aligned Thursday panel containing `P_t`, `B_t`, `A_t`, `C_t`.
   - this is the primary input for the next calculation.
2. `Maple/data/meaegi_population_weekly.csv`
   - raw `group1` population source.
3. `Maple/data/challengers_population_weekly_seasons1_4.csv`
   - Challenger seasons 1–4 weekly account proxy.
4. `Maple/docs/meso_patch_dates_and_values.md`
   - canonical patch dates and six canonical total-production anchor points.
5. `Maple/docs/HANDOFF_2026-09-11.md`
   - full context and methodological constraints.

Do **not**:
- digitize NOW charts again;
- search Inven before running the core calculation;
- rebuild population series from another site;
- replace the canonical production curve with a newly reconstructed curve;
- use the old equal-weight `A+C` per-user master as the final denominator.

## 2. Fixed project assumptions
Treat these as axioms for this task.

1. Official total/boss production includes Challenger worlds.
2. Challenger participation does not materially reduce weekly main-world boss-crystal production.
3. Main-world account productivity changes smoothly except at identifiable patch interventions.
4. Patch effects must be separated from Challenger effects.

## 3. Primary calibration identity
For boss-meso production:

\[
B_t=A_t\mu^M_t+C_t\mu^C_t.
\]

When Challenger is closed (`C_t=0`):

\[
\mu^M_t=B_t/A_t.
\]

During Challenger seasons estimate the main-world counterfactual `muM_hat_t`, then:

\[
\widehat{\mu^C_t} = \frac{B_t-A_t\widehat{\mu^M_t}}{C_t},
\qquad
w_t=\frac{\widehat{\mu^C_t}}{\widehat{\mu^M_t}}.
\]

Then:

\[
E_t=A_t+w_tC_t,
\qquad
Q_t=P_t/E_t.
\]

## 4. Exact execution order
Do these in one continuous pass. Do not stop after step 2 and turn smoothness into a separate research project.

### Step 1 — Verify the aligned input panel
Check only mechanical integrity:
- dates ascending and weekly;
- no duplicate dates;
- `A_t>0`;
- `C_t=0` outside Challenger seasons;
- `P_t` nonmissing;
- `B_t` source flag understood (`direct` preferred; `conditional_backcast` only where direct unavailable).

Do not change data unless a concrete inconsistency is found.

### Step 2 — Compute observed main productivity in non-Challenger periods

\[
q^M_t=B_t/A_t.
\]

Inspect level, local slope, and week-to-week variance. Overlay the intervention dates from `meso_patch_dates_and_values.md`.

The question is only: **what is the least complex counterfactual that is adequate?**

### Step 3 — Choose the minimum-complexity counterfactual
Default ladder:

- Model A: local pre-season mean.
- Model B: local linear trend if a visible pre-season slope exists.
- Model C: piecewise linear / smooth latent trend only if A/B fail clearly.

Patch boundaries may reset level/slope. Do not let a crystal-price adjustment or new-boss addition be absorbed as a Challenger residual.

Use the simplest model that leaves no obvious structured error in adjacent non-Challenger periods.

### Step 4 — Immediately estimate Challenger productivity
For every Challenger week:

\[
\widehat{\mu^C_t}=(B_t-A_t\widehat{\mu^M_t})/C_t.
\]

Sanity checks:
- persistent negative values => counterfactual or alignment failure;
- extreme one-week spikes => check patch boundary/date alignment first;
- `w_t` should be economically plausible and generally below 1.

Do not yet use Inven progression data to force-fit the answer.

### Step 5 — Build `w_t`, `E_t`, and the final `Q_t`

\[
w_t=\widehat{\mu^C_t}/\widehat{\mu^M_t}
\]

\[
E_t=A_t+w_tC_t
\]

\[
Q_t=P_t/E_t
\]

For non-Challenger weeks set `w_t=0` and `E_t=A_t`.

Normalize final `Q_t` for presentation only after all calculations are complete. Preferred display normalization: `2025-09 average Q_t = 100` unless the user requests another anchor.

### Step 6 — Output the canonical calculation files
Create at minimum:

`Maple/data/per_capita_production_final_weekly.csv`

Required columns:
```text
date
P_total_newage100
B_boss_newage100
A_main_accounts
C_challenger_accounts
challenger_season
muM_observed
muM_counterfactual
muC_residual
w_challenger_main_equiv
E_effective_accounts
Q_raw
Q_index_sep2025_100
counterfactual_model
patch_regime
quality_flag
```

Also create:

`Maple/docs/PER_CAPITA_PRODUCTION_METHOD.md`

It must state the chosen counterfactual form and why it was the minimum adequate model.

### Step 7 — Only after Q_t exists, use aggregate progression as validation
Aggregate sources only:
- Challenger cumulative counts/ranks;
- Diamond/Master counts;
- Genesis liberation counts;
- boss-clear population counts.

Never use individual clear screenshots, individual combat-power achievements, personal guides, or anecdotal samples as population-distribution data.

Progression-derived tier rewards are a secondary validation channel for residual `muC_t`, not the primary estimator.

## 5. Canonical six production points
These are fixed and are not to be rediscovered:

| point | date | total-production index (NEW AGE=100) |
|---|---|---:|
| ASSEMBLE pre-slope local low | 2025-06-13 | 372.5 |
| ASSEMBLE first post-slope local high | 2025-06-28 | 610.3 |
| max between CROWN and Azmoth removal | 2025-12-30 | 593.4 |
| OVERDRIVE 1 pre-slope local low | 2026-06-11 | 634.7 |
| OVERDRIVE 1 first post-slope local high | 2026-06-26 | 1075.8 |
| last canonical observation | 2026-08-21 | 1183.7 |

These points are for validation/annotation; the weekly input panel is the calculation source.

## 6. Stop conditions / reporting
Do not pause after merely plotting `B_t/A_t`.
Return after producing the first complete `Q_t` series.

Report:
1. chosen counterfactual model and intervention handling;
2. season-wise range/median of `w_t`;
3. whether residual `muC_t` is nonnegative and smooth enough;
4. the six canonical dates' corresponding `Q_t` values where available;
5. final CSV path;
6. only then list progression data that would most improve validation.

The task is successful when a reproducible first-pass `Q_t=P_t/E_t` exists. Further Inven research is refinement, not a prerequisite.
