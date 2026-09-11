# Per-capita meso production — first-pass canonical method

## Objective

The current deliverable is

\[
Q_t=\frac{P_t}{E_t}, \qquad E_t=A_t+w_tC_t,
\]

where `E_t` is not a unique-human count but a production-capacity-adjusted population measured in main-world-account equivalents.

The sole purpose of the boss-production decomposition is to calibrate `w_t`.

## Input

Primary input:

`Maple/data/maple_production_calibration_inputs_weekly.csv`

Mechanical integrity check:

- rows: 141
- date range: 2023-12-28 to 2026-09-03
- strictly weekly Thursday spacing: yes
- duplicate dates: 0
- non-positive `A_main_accounts`: 0
- missing `P_total_newage100`: 0
- non-zero Challenger count outside Challenger seasons: 0

No canonical production or population series was rebuilt.

## Observed main-world boss productivity

For non-Challenger weeks,

\[
\mu_t^M=\frac{B_t}{A_t}.
\]

This observed series is written to `muM_observed`. During Challenger weeks it is left blank because `B_t/A_t` is then a mixture of main-world and Challenger production.

## Counterfactual choice: minimum adequate patch-adjusted model

A single local constant is not adequate for the completed Challenger seasons because the pure-main boundary values materially differ from the beginning to the end of each season. Pure pre-season extrapolation is also unstable across long seasons containing known patch interventions.

The first-pass therefore uses the least complicated retrospective bridge that honors both adjacent pure-main boundaries:

1. anchor on the last pure-main observation immediately before the season;
2. evolve a constant additive weekly drift;
3. apply a discrete multiplicative factor at a known within-season patch boundary;
4. choose the drift so that the path lands exactly on the first pure-main observation after the season.

For a bridge with weekly drift `g` and patch multiplier `r_k`,

\[
m_t=(m_{t-1}+g)r_t,
\]

with `r_t=1` except at the specified patch week. The scalar `g` is solved from the endpoint condition.

This is a descriptive retrospective counterfactual, not a structural causal estimate.

### Season 1

- main anchor before season: 2024-12-12, `muM = 8.7378047086e-05`
- first pure-main anchor after season: 2025-05-22, `muM = 0.000106646368147`
- within-season intervention: crystal-price adjustment on 2025-04-17
- patch multiplier: 0.833280116
- fitted additive weekly drift: 1.69187998093e-06

Season 1 begins on the NEXT patch date, so its first weeks are intrinsically less well identified. This is reflected in `quality_flag`.

### Season 2

- post-ASSEMBLE pure-main anchor: 2025-06-19, `muM = 8.67685449971e-05`
- first pure-main anchor after season: 2025-11-27, `muM = 0.000134348690175`
- within-season intervention: crystal-price adjustment on 2025-10-23
- patch multiplier: 0.876573374
- fitted additive weekly drift: 2.80531302965e-06

### Season 3

- post-CROWN pure-main anchor: 2025-12-18, `muM = 0.000140256465798`
- first pure-main anchor after season: 2026-04-23, `muM = 0.000204876443294`
- within-season intervention: Azmoth removal on 2026-01-15
- patch multiplier: 1.101369081
- fitted additive weekly drift: 2.73844086402e-06

### Season 4

Season 4 is still open in the panel, so no post-season pure-main endpoint exists. It is therefore the least certain season.

- post-OVERDRIVE-1 main-only anchor: 2026-06-18, `muM = 0.000262344899703`
- local pre-season slope estimated on pure-main observations from 2026-04-23 through 2026-06-11: `3.69618249939e-06` per week
- the path is anchored at the 2026-06-18 post-OVERDRIVE-1 observation and then advanced with that local slope
- OVERDRIVE 2 multiplier at 2026-07-23: 1.118547577
- OVERDRIVE 3 multiplier at 2026-08-20: 1.015197389

These patch multipliers are first-pass local discontinuity adjustments from the aligned boss-per-main-account series. They should be rechecked after the first `Q_t` series is validated against aggregate Challenger progression.

## Non-negativity constraint

Economic feasibility requires

\[
\mu_t^C\ge 0
\quad\Longrightarrow\quad
\widehat{\mu_t^M}\le \frac{B_t}{A_t}.
\]

The unconstrained bridge violated this inequality only on three boundary-sensitive weeks:

- 2024-12-19
- 2025-04-24
- 2025-11-20

For those three rows only, `muM_counterfactual` is clipped to `B_t/A_t`, yielding `muC_residual=0`. They are explicitly marked `nonnegative_boundary_clip` rather than silently smoothed away.

## Challenger residual and main-equivalent weight

For Challenger weeks,

\[
\widehat{\mu_t^C}
=
\frac{B_t-A_t\widehat{\mu_t^M}}{C_t},
\qquad
w_t=
\frac{\widehat{\mu_t^C}}{\widehat{\mu_t^M}}.
\]

For non-Challenger weeks, `w_t=0` and `E_t=A_t`.

First-pass season summaries:

| season | start | end | min w | median w | max w |
|---|---|---|---:|---:|---:|
| season1 | 2024-12-19 | 2025-05-15 | 0.000 | 0.229 | 0.508 |
| season2 | 2025-06-26 | 2025-11-20 | 0.000 | 0.509 | 0.721 |
| season3 | 2025-12-25 | 2026-04-16 | 0.012 | 0.326 | 0.744 |
| season4 | 2026-06-25 | 2026-09-03 | 0.154 | 0.357 | 0.517 |

After the explicit feasibility clips, all residual Challenger productivity values are nonnegative and every first-pass `w_t` remains below 1.

## Effective population and final series

\[
E_t=A_t+w_tC_t
\]

and

\[
Q_t=\frac{P_t}{E_t}.
\]

`Q_raw` is the unnormalized series. `Q_index_sep2025_100` divides `Q_raw` by the arithmetic mean of September 2025 weekly values and multiplies by 100.

September 2025 normalization denominator:

`0.000193420032338`

## Canonical production-date cross-check

The input panel is Thursday-aligned, whereas several canonical NOW anchors are not Thursdays. Therefore the table below reports the nearest weekly panel row; it does not relabel the weekly value as an exact daily observation.

| canonical point | canonical date | weekly row | offset | Q index (Sep-2025=100) |
|---|---|---|---:|---:|
| ASSEMBLE pre local low | 2025-06-13 | 2025-06-12 | -1 d | 69.72 |
| ASSEMBLE first post local high | 2025-06-28 | 2025-06-26 | -2 d | 85.31 |
| CROWN~Azmoth removal max | 2025-12-30 | 2026-01-01 | +2 d | 129.47 |
| OVERDRIVE1 pre local low | 2026-06-11 | 2026-06-11 | +0 d | 151.26 |
| OVERDRIVE1 first post local high | 2026-06-26 | 2026-06-25 | -1 d | 169.07 |
| last canonical observation | 2026-08-21 | 2026-08-20 | -1 d | 205.72 |

## Quality flags

- `boss_backcast`: boss production is the repository's conditional backcast rather than a direct boss-series observation.
- `boss_direct`: direct boss-production series is available.
- `counterfactual`: `muM_counterfactual` is estimated because Challenger is active.
- `nonnegative_boundary_clip`: one-sided feasibility constraint was binding.
- `open_ended_season4`: no post-season pure-main endpoint exists yet.

## Interpretation and limitations

`Q_t` should be described technically as **meso production per main-world-equivalent effective production account**, not literal meso production per unique human.

The first-pass counterfactual is deliberately low-dimensional. It uses only the aligned canonical panel and known patch dates. It does not use Inven Challenger/Diamond/liberation data to fit the answer.

The next stage is validation only: compare the implied `muC_residual`/`w_t` trajectories against aggregate Challenger progression counts, ranks, liberation counts, and boss-clear population counts. Individual guides, clear screenshots, individual combat-power achievements, and anecdotes must not be used as population-distribution evidence.
