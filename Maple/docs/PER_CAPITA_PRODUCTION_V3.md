# Per-capita meso production V3 — dual-anchor calibration

## Status

V3 is the current dual-anchor recalculation of

\[
Q_t=\frac{P_t}{E_t}.
\]

Unlike V2, V3 does not treat every observed main-world active account as one homogeneous unit of productive exposure through large influxes. It combines two independent identification channels:

1. **Challenger-free main-world inflow episodes** to estimate temporary entrant dilution;
2. **late/static Challenger windows** to reverse-track mature Challenger production rather than allowing an arbitrary late-season residual collapse.

Progression counts are not used to fit the model.

Primary outputs:

- `Maple/data/per_capita_production_v3_weekly.csv`
- `Maple/data/per_capita_production_v3_season_summary.csv`
- reproducible script: `Maple/scripts/recompute_per_capita_v3.py`

## Core V3 identity

V3 distinguishes raw active-account headcount from productive-equivalent main exposure:

\[
A_t^{eff}=A_t^{inc}+\lambda_t A_t^{ent}.
\]

Boss production is decomposed as

\[
B_t=A_t^{eff}\mu_t^M+C_t\mu_t^C,
\qquad
w_t=\frac{\mu_t^C}{\mu_t^M},
\]

and the denominator becomes

\[
\boxed{E_t=A_t^{eff}+w_tC_t}.
\]

Therefore V3 is more specifically a **productive-equivalent exposure-adjusted per-capita series**. It should not be interpreted as meso production per literal unique human.

## 1. Pure-main composition prior

The pure-main pilot established that large influxes are not homogeneous productive exposure. The current V3 uses only previously identified clean episodes:

| event | pure-main estimated entrant exposure |
|---|---:|
| MILESTONE | 0.639201 |
| NEXT pre-launch | 0.053227 |
| ASSEMBLE pre-launch | 0.032182 |
| CROWN | 0.442960 |

For Season 3's 2026-03-19/03-26 main-world influx, V3 does **not** fit Challenger progression. It imports the coarse regime split from the pure-main episodes:

- moderate inflow: mean of MILESTONE and CROWN = `0.5410805`;
- explosive inflow: mean of NEXT and ASSEMBLE = `0.0427045`.

This produces:

- 2026-03-19: raw `A=279,166`, productive-equivalent `A_eff=263,148`;
- 2026-03-26: raw `A=327,578`, productive-equivalent `A_eff=247,821`.

No entrant discount is forced onto OVERDRIVE 1 because that week contains a strong direct boss-accessibility/productivity shock and is not a clean dilution episode.

## 2. Late/static Challenger reverse anchors

The mature anchors are production anchors (`muC`), not season-average weights.

| season | mature anchor | base mature `muC` |
|---|---|---:|
| S1 | 2025-04-03 onward | `6.83845e-05` |
| S2 | 2025-09-25 onward | `6.90614e-05` |
| S3 | 2026-03-05 onward | `1.21991e-04` |
| S4 | 2026-08-20 onward | `1.728904e-04` |

For S1 and S2, the independently identified Strong Crystal reward factors are applied after the direct reward-schedule changes:

- S1 after 2025-04-17: multiply mature `muC` by `0.919031579`;
- S2 after 2025-10-23: multiply mature `muC` by `0.7843388960`.

During a mature-anchor week, V3 fixes `muC` to the relevant mature production anchor and reverse-solves main incumbent productivity:

\[
\mu_t^M=\frac{B_t-C_t\mu_t^C}{A_t^{eff}}.
\]

This deliberately prevents a main-world denominator-composition shock from being misread as a sudden collapse in mature Challenger production.

## 3. Season 4 terminal treatment

User instruction on 2026-09-11: **treat the current Season 4 state as the season-end estimate and recalibrate later after actual post-season data arrive.**

Accordingly V3 uses the terminal S4 production anchor

\[
\mu_C^{terminal,S4}=1.728904\times10^{-4}
\]

for 2026-08-20 through the final aligned weekly row, 2026-09-03.

The live Challenger-tier count supplied on 2026-09-11 is

\[
\boxed{189,757}.
\]

This is stored as validation metadata on the final weekly row. It is **not** substituted for `C_challenger_accounts`, because Challenger-tier attainment count and the aligned active-account proxy measure different populations.

The current terminal state is treated as economically mature; V3 does not leave an additional open-season growth extrapolation beyond it.

## 4. V3 season summaries

| season | median w | C-weighted mean w | min | max | mature-anchor mean w | failed weeks |
|---|---:|---:|---:|---:|---:|---:|
| S1 | 0.350 | 0.321 | 0.036 | 0.751 | 0.665 | 1 |
| S2 | 0.423 | 0.381 | 0.088 | 0.546 | 0.460 | 0 |
| S3 | 0.567 | 0.436 | 0.005 | 0.839 | 0.673 | 0 |
| S4 | 0.502 | 0.389 | 0.154 | 0.681 | 0.580 | 0 |

These season-wide means are not substitutes for the late anchors. Early Challenger growth weeks remain much weaker than mature weeks and appropriately pull the full-season averages downward.

## 5. Season 3: the main validation success

V2 allowed the apparent Challenger weight to collapse after the 2026-03-19 main-world population shock. V3 instead combines the independently estimated pure-main entrant discount with the late S3 production anchor.

Selected values:

| date | V2 w | V3 w | V3 A_eff |
|---|---:|---:|---:|
| 2026-03-12 | 0.692 | 0.656 | 244,263 |
| 2026-03-19 | 0.553 | 0.647 | 263,148 |
| 2026-03-26 | 0.187 | 0.616 | 247,821 |
| 2026-04-02 | 0.362 | 0.705 | 320,130 |
| 2026-04-09 | 0.271 | 0.711 | 313,838 |
| 2026-04-16 | 0.148 | 0.708 | 329,305 |

The late-season collapse disappears without fitting to Challenger progression. This is exactly the overlap test proposed in the dual-anchor pilot: a mature Challenger production plateau and entrant dilution of a magnitude independently observed during Challenger-free history are simultaneously compatible with the observed boss-production total.

This substantially strengthens the interpretation that the V2 late-S3 collapse was primarily a **main-world denominator-composition artifact**, not an actual collapse of Challenger boss productivity.

## 6. Season 4 terminal result

The current endpoint is intentionally treated as terminal.

| date | V3 w | V3 Q index (Sep-2025=100) |
|---|---:|---:|
| 2026-08-20 | 0.614 | 164.39 |
| 2026-08-27 | 0.570 | 176.95 |
| 2026-09-03 | 0.551 | 182.95 |

The C-weighted terminal-anchor mean is

\[
w_{late,S4}^{V3}\approx0.580.
\]

The 2026-07-30 peak remains `w≈0.681`. V3 does not smooth it away because the patch study found a credible structural explanation: accelerated Genesis liberation plus the 7/23 HEXA/power shock and improved upper-boss access.

## 7. Q sensitivity

V3 changes both sides of the denominator logic:

- on selected pure-main influx weeks, `A_eff < A`;
- in mature Challenger windows, `muC` is anchored and main productivity is reverse-solved.

Therefore local changes can be materially larger than V2. The strongest clean example is the ASSEMBLE pre-launch dilution week:

- 2025-06-12: `A=425,334`, `A_eff≈319,686`;
- V3 raw Q is about **33% above V2** on that single week.

This is not a numerical error. It is the direct consequence of no longer treating a massive low-productivity influx as fully mature productive exposure on entry.

At the current terminal endpoint the sensitivity is much smaller:

- 2026-09-03 V3 raw Q is about **+3.47%** versus V2;
- V3 normalized endpoint is `182.95` with September 2025 = 100.

Thus the long-run conclusion remains robust: after production-capacity-adjusted population exposure is removed, the meso-production capacity series remains far above its 2025 baseline.

## 8. Important limitations

1. The entrant-discount prior is deliberately coarse. Four pure-main episodes do not identify a universal continuous `lambda(inflow,tau)` function.
2. V3 applies composition correction only to identified clean dilution episodes and the S3 shock where the external prior is used. It does not automatically discount every positive weekly change in `A_t`.
3. Mature `muC` is treated as approximately static over each late anchor segment absent a direct reward shock. This is a stronger assumption than V2 and should be rechecked when richer late-season aggregate data are available.
4. S4's current state is provisionally treated as terminal by explicit user instruction. Actual post-2026-09-17 pure-main rows should later be used for two-sided recalibration.
5. The live `189,757` Challenger-tier count is validation metadata only and must not be confused with `C_t`.

## Interpretation

The current preferred technical label is:

> **meso production per main-world-equivalent productive exposure account**

A public-facing graph may still be titled “1인당 메소 생산량,” but the note should define that the denominator is production-capacity adjusted rather than literal unique-human headcount.
