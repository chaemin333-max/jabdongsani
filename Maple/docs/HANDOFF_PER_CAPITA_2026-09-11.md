# HANDOFF — Per-capita meso production project

## Goal hierarchy
The current deliverable is one canonical time series:

\[
\boxed{Q_t=P_t/E_t},\qquad \boxed{E_t=A_t+w_tC_t}.
\]

- `P_t`: canonical total meso production already reconstructed from Maple NOW charts.
- `A_t`: main-world active-account proxy from Meaegi `group1` (Eos/Helios excluded).
- `C_t`: Challenger active-account proxy from Meaegi `all-burning-character`; Item Burning is one per account, so this is treated as an account-count proxy.
- `w_t`: Challenger account boss-production capacity relative to an average main-world account.
- `E_t`: production-capacity-adjusted population, in main-account equivalents.

Everything else is a calibration or validation layer for the denominator. Do not allow residual decomposition or Challenger progression research to become the primary objective.

## Canonical input file
Use first:

`Maple/data/maple_production_calibration_inputs_weekly.csv`

It is already aligned to the Thursday population dates and contains:
- `P_total_newage100`
- `B_boss_newage100`
- `A_main_accounts`
- `C_challenger_accounts`
- `challenger_season`
- direct/backcast boss-series flags

Do not digitize the NOW charts again and do not rebuild population data from another website.

Raw/reference files remain available:
- `Maple/data/meaegi_population_weekly.csv`
- `Maple/data/challengers_population_weekly_seasons1_4.csv`
- `Maple/data/challengers_population_weekly_seasons1_4.json`
- `Maple/docs/meso_patch_dates_and_values.md`

## Fixed assumptions
Treat these as project axioms for this task.

1. Official total and boss meso-production figures include Challenger worlds.
2. Challenger participation does not materially reduce weekly main-world boss-crystal production.
3. Main-world account-level boss production evolves smoothly except at identifiable patch interventions.
4. Crystal-price changes, newly released bosses, and major growth-system shocks must not be misidentified as Challenger production.

## Why the old A+C model is not the final denominator
Main-world and Challenger accounts do not have equal production capacity.

A typical main account may contain a main character plus multiple boss mules. Challenger seasons are effectively one Item-Burning-centered production character per account, and seasons 1–3 had much lower practical progression ceilings than main worlds. Therefore an equal-weight denominator `A_t+C_t` can be severely biased.

The old unique-user overlap bounds are retained only as a historical benchmark, not as the final model.

## Calibration identity
Use boss production to infer the Challenger weight:

\[
B_t=A_t\mu_t^M+C_t\mu_t^C.
\]

Outside Challenger seasons:

\[
\mu_t^M=B_t/A_t.
\]

During Challenger seasons, estimate the counterfactual main-world productivity `muM_hat_t` using the adjacent non-Challenger periods and patch interventions. Then:

\[
\widehat{\mu_t^C}=\frac{B_t-A_t\widehat{\mu_t^M}}{C_t},
\qquad
w_t=\frac{\widehat{\mu_t^C}}{\widehat{\mu_t^M}}.
\]

Finally:

\[
E_t=A_t+w_tC_t,
\qquad
Q_t=P_t/E_t.
\]

## Counterfactual rule: minimum adequate complexity
Do not turn `B_t/A_t` smoothness into a standalone research project. Its only purpose is to choose the least complex adequate `muM_hat_t`.

Use this ladder:
1. local pre-season mean;
2. local linear trend if slope is visibly nonzero;
3. piecewise/smoothed model only if 1–2 clearly fail.

Patch boundaries may reset level or slope. The patch-date reference is `Maple/docs/meso_patch_dates_and_values.md`.

## Exact workflow
1. Load `maple_production_calibration_inputs_weekly.csv`.
2. Verify only mechanical integrity; do not alter canonical curves without a concrete inconsistency.
3. Calculate `B_t/A_t` on `C_t=0` weeks.
4. Choose the minimum adequate patch-adjusted main-world counterfactual.
5. Immediately compute residual `muC_t`, then `w_t`.
6. Compute `E_t=A_t+w_tC_t`.
7. Compute the first complete `Q_t=P_t/E_t` series.
8. Normalize for presentation only after the raw series exists; preferred display anchor is September 2025 average = 100.
9. Only after Q exists, use aggregate Challenger progression as an independent sanity check.

Do not stop after step 3 merely to report a smoothness plot.

## Required outputs
Create:

`Maple/data/per_capita_production_final_weekly.csv`

with at least:
- date
- P_total_newage100
- B_boss_newage100
- A_main_accounts
- C_challenger_accounts
- challenger_season
- muM_observed
- muM_counterfactual
- muC_residual
- w_challenger_main_equiv
- E_effective_accounts
- Q_raw
- Q_index_sep2025_100
- counterfactual_model
- patch_regime
- quality_flag

Also create:

`Maple/docs/PER_CAPITA_PRODUCTION_METHOD.md`

and explain exactly why the chosen counterfactual is the minimum adequate form.

## Canonical six total-production anchor points
Do not rediscover these from images.

- 2025-06-13: 372.5 — ASSEMBLE pre-slope local low
- 2025-06-28: 610.3 — first post-ASSEMBLE local high
- 2025-12-30: 593.4 — max between CROWN and Azmoth removal
- 2026-06-11: 634.7 — OVERDRIVE 1 pre-slope local low
- 2026-06-26: 1075.8 — first post-OVERDRIVE-1 local high
- 2026-08-21: 1183.7 — last canonical observation

These are annotation/validation points, not a replacement for the weekly calculation panel.

## Challenger progression data: validation only
After residual `muC_t` exists, it may be validated against aggregate population data such as:
- cumulative Challenger counts/ranks;
- Diamond/Master population counts;
- Genesis-liberation counts;
- boss-clear population counts.

Do not use individual guides, clear screenshots, individual combat-power achievements, individual character reviews, or anecdotal cases as population distribution data.

Known progression evidence so far:
- Season 2: an Inven post contains an aggregate day-by-day Challenger attainment series; final cumulative count is roughly mid-25k range. If used, extract the aggregate table rather than personal examples.
- Season 3: an aggregate day-by-day Challenger series exists; previously noted anchors include 2025-12-25=2, 2026-02-12=2,220, 2026-03-12=8,290, 2026-04-15=20,990. Recheck source before canonicalizing.
- Season 4 is ongoing; user-confirmed Challenger count on 2026-09-11 is 189,391. Earlier aggregate rank snapshots around late July/early August/late August may be used only as validation.
- Season 1 likely requires Diamond/Master aggregate counts rather than Challenger counts because Diamond-run behavior was common and the practical progression ceiling was lower. Do not delay first-pass Q_t waiting for these data.

## Tier-reward validation layer
If constructing a secondary progression-based `muC_t`, use time-dependent rewards `R_{j,t}`. Never back-project current combat-power cutoffs directly into older seasons because of specification inflation and boss-release chronology.

Recent user-provided weekly crystal-income anchors include approximately:
- 5만 초반 / 이카솔: 20.671억
- 6만 중반 / 노적솔: 28.299억
- 7만 중반 / 노흉솔: 37.384억
- 8만 후반: 54.7643억
- 9만 후반: 80.5143억
- 10만 후반: 92.996억
- 11만 중반: 125.446억
- 12만 중반: 181.879억

Bosses not yet released at a historical date must be removed from the corresponding reward path.

## Scope boundary
Starforce/sink/meso-stock reconstruction is a separate track. Do not mix it into the denominator calibration until the production-side Q_t series is closed.

## Definition of done for the next researcher
The next report should not be another literature-search memo. It should contain a reproducible first-pass `Q_t` series.

Report only after producing it, with:
1. the chosen counterfactual and patch treatment;
2. season-wise range/median of `w_t`;
3. whether residual `muC_t` remains nonnegative and reasonably smooth;
4. `Q_t` around the six canonical dates where available;
5. the final CSV and method document;
6. only then a short list of aggregate progression data that would most improve validation.
