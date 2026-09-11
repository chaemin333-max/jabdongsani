# Dual-anchor calibration pilot: pure-main dilution + late-season mature Challenger anchors

## Objective

This pilot does not yet replace V2. It tests a narrower identification strategy for a future V3:

1. estimate the short-run active-account composition distortion from periods with **no Challenger world**;
2. independently estimate a mature / late-season Challenger productivity anchor after most character growth has saturated;
3. use the overlap between the two to diagnose whether apparent late-season residual collapses are true Challenger productivity declines or main-world denominator contamination.

The core mixture remains

\[
B_t=A_t\mu_t^M+C_t\mu_t^C.
\]

The key refinement is that observed `A_t` is not automatically a homogeneous productive exposure after a large influx.

---

## 1. Pure-main entrant dilution

Write

\[
A_t=A_t^{inc}+A_t^{ent},
\qquad
A_t^{eff}=A_t^{inc}+\lambda_t A_t^{ent},
\qquad 0\le \lambda_t\le 1.
\]

For a short pure-main event window, if the pre-event `B/A` is used as the incumbent productivity reference and direct boss/reward shocks are small, an immediate entrant exposure can be backed out from

\[
B_1\approx \mu_0\left(A_0+\lambda\Delta A\right).
\]

Thus

\[
\lambda\approx\frac{B_1/\mu_0-A_0}{\Delta A}.
\]

This is descriptive, not structural. It is intentionally calculated only in `C_t=0` intervals.

### Pure-main pilot episodes

| episode | account inflow | implied immediate entrant exposure `lambda` | interpretation |
|---|---:|---:|---|
| MILESTONE, 2024-06-13 -> 06-27 | +21.6% | 0.639 | moderate inflow; dilution present but entrants are not near-zero producers |
| NEXT pre-launch, 2024-12-05 -> 12-12 | +30.6% | 0.053 | explosive influx with almost flat boss production |
| ASSEMBLE pre-launch, 2025-06-05 -> 06-12 | +34.5% | 0.032 | strongest clean dilution case |
| CROWN, 2025-12-11 -> 12-18 | +13.0% | 0.443 | moderate winter inflow |

The important empirical result is not a universal scalar lambda. It is the regime split:

- explosive `~30%+` influxes can enter with **near-zero immediate boss exposure**;
- moderate `~10-20%` influxes show substantially larger, but still sub-incumbent, exposure.

Therefore a fixed `A_t` head-count denominator is not defensible through large launch weeks.

### Recovery information

MILESTONE is the only clean pure-main case with a reasonably long post-inflow window before a Challenger season. Relative to the 2024-06-13 pre-event `B/A`, the observed ratio is approximately:

- 06-27: 0.936
- 07-04: 1.003
- 07-11: 1.063
- 07-18: 1.118

The initial dilution therefore disappears quickly in the observed aggregate. This recovery combines entrant attrition, entrant progression and genuine patch productivity, so it should not be interpreted as a clean biological-style half-life. But it does show that the composition distortion is concentrated in the first several weeks rather than remaining permanent.

---

## 2. Late-season Challenger mature anchors

A second identification channel becomes available late in a Challenger season.

After roughly three months in the slower seasons, or materially earlier in fast-Genesis-Pass regimes, the remaining characters are much closer to a mature state: most intended transfer characters have settled into their final progression band, growth slows, and the cohort composition becomes much less like the explosive opening weeks.

This does **not** mean `C_t` is literally constant. Weak accounts can still leave and the remaining population can become selected. The useful assumption is narrower: late-season `muC` / `w` should not exhibit a large unexplained collapse absent a direct reward or power shock.

For each season the pilot chooses a window immediately before a known contaminating intervention where possible. The values below are `C_t`-weighted summaries of the V2 residual over those windows; they are treated as candidate mature anchors, not as V3 outputs.

| season | mature window | C-weighted mature `w` | C-weighted `muC` | reason for window |
|---|---|---:|---:|---|
| S1 | 2025-04-03 to 04-10 | 0.636 | 6.84e-05 | >3 months after launch; after 3/20 power update, before 4/17 crystal change |
| S2 | 2025-09-25 to 10-16 | 0.493 | 6.91e-05 | ~3-4 months after launch; before 10/23 crystal change |
| S3 | 2026-03-05 to 03-12 | 0.672 | 1.22e-04 | ~11-12 weeks after launch; immediately before 3/19 main-world inflow shock |
| S4 broad | 2026-08-13 to 09-03 | 0.560 | 1.66e-04 | accelerated Genesis regime and near season end |
| S4 terminal | 2026-08-20 to 09-03 | 0.578 | 1.73e-04 | last three available weekly observations |

These mature weights are **not season averages**. They are endpoint / plateau calibration targets.

Official Challenger durations support the distinction between early-growth and late-static regimes:

- S1: 2024-12-19 to 2025-05-22
- S2: 2025-06-19 to 2025-11-20
- S3: 2025-12-18 to 2026-04-16
- S4: 2026-06-18 to 2026-09-17

Season 4 is therefore already in its terminal phase in the current dataset; the official end is 2026-09-17.

---

## 3. The overlap is the key identification test

### Season 3

V2 gives, immediately before the 3/19 population shock:

- 2026-03-05: `muC ~ 1.174e-4`, `w ~ 0.653`
- 2026-03-12: `muC ~ 1.268e-4`, `w ~ 0.692`

The C-weighted mature anchor is therefore

\[
\mu_C^{late,S3}\approx1.22\times10^{-4},
\qquad w^{late,S3}\approx0.67.
\]

Now keep `muC` near this mature level after 3/19 instead of allowing it to collapse. Model the incumbent main population as a continuation of the pre-3/19 cohort and solve for the entrant exposure needed to explain total boss production.

Using a simple continuation of the pre-shock main-account trend, the implied post-shock entrant exposures are approximately:

- 03-19: `lambda ~ 0.64`
- 03-26: `~0.23`
- 04-02: `~0.60`
- 04-09: `~0.51`
- 04-16: `~0.54`

The week-to-week values are noisy, but their scale is striking: they sit inside the range already observed in the **independent pure-main episodes**. The especially low 3/26 value occurs near the peak account influx.

This is the central dual-anchor result:

> the late-S3 Challenger collapse is not required by the data. A mature Challenger productivity near the pre-3/19 level, combined with entrant dilution of the magnitude independently seen in pure-main launch periods, explains the apparent residual collapse without forcing Challenger characters to become dramatically weaker.

Therefore S3 should be reclassified from `late progression contradiction` to **main-world composition-contaminated after 2026-03-19**.

### Season 4

S4 needs different treatment because there is not yet a post-season pure-main observation in the aligned panel. However it is no longer an early/open-growth season in an economic sense.

The official season runs only through 2026-09-17, and the last available rows are 2026-08-20, 08-27 and 09-03. Under the accelerated Genesis regime these are mature terminal observations.

The V2 terminal C-weighted anchor is

\[
w^{late,S4}\approx0.58,
\qquad
\mu_C^{late,S4}\approx1.73\times10^{-4}.
\]

Treating terminal `muC` in the rough `1.7-1.8e-4` range implies main-world productivity around `3.1e-4` by 9/03, which is compatible with a surviving / selected main population recovering from the large 6/18 influx and progressing under OVERDRIVE. This is materially different from treating the late S4 rows as merely another open-season extrapolation.

A particularly important future cross-check is available almost immediately: the first pure-main row after 2026-09-17 will directly anchor `muM` on the other side of the season boundary. That row will turn the current terminal S4 estimate from a one-sided mature anchor into the same two-sided structure available for S1-S3.

---

## 4. Implications for V3

The next model should use two independent constraints rather than a more flexible arbitrary smoother.

### Main-world constraint from Challenger-free history

Large entrant shocks should be represented as a temporary productive-exposure discount:

\[
A_t^{eff}=A_t^{inc}+\lambda(\Delta A/A,\tau)A_t^{ent}.
\]

Current evidence supports at least a coarse regime split:

- explosive launch influx (`~30%+`): initial lambda near 0-0.1;
- moderate influx (`~10-20%`): initial lambda roughly 0.4-0.7;
- the distortion then decays over the following weeks through attrition/progression, but a clean universal recovery kernel is not yet identified.

Do not overfit a continuous lambda function from four episodes.

### Challenger constraint from mature endpoints

For each season introduce a late-season mature anchor `w_late,s` rather than letting a boundary bridge freely imply a terminal collapse.

Current pilot anchors are roughly:

\[
(w_{late,1},w_{late,2},w_{late,3},w_{late,4})
\approx
(0.64,0.49,0.67,0.56\text{--}0.58).
\]

They are not required to be equal because season growth systems, Genesis timing, boss accessibility and reward schedules differ.

### Known interventions remain external

The dual-anchor correction must not erase real productivity shocks:

- direct crystal reward changes;
- Genesis / liberation acceleration;
- HEXA skill releases;
- boss HP / pattern reductions;
- new upper-tail bosses.

The purpose is specifically to remove denominator-composition artifacts, not to flatten economic reality.

---

## 5. Immediate next calculation

A V3 pilot can now be constructed with very few additional degrees of freedom:

1. preserve V2 reward-table factors;
2. replace the smooth main-world bridge around large inflow weeks with a pure-main-informed temporary entrant discount;
3. constrain each season's late portion toward its mature anchor rather than toward an arbitrary bridge endpoint;
4. leave genuine boss/power shocks discrete;
5. recompute `w_t`, `E_t`, and `Q_t`;
6. compare V2 vs V3 and re-run progression validation without fitting to progression.

For S4, defer final two-sided closure until the first post-2026-09-17 pure-main weekly row is available. Until then the `0.56-0.58` late-season range is a provisional terminal anchor, not a final calibrated season weight.
