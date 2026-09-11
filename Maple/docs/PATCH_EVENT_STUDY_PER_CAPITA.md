# Patch-event study for per-capita meso production calibration

## Purpose

This document adds an event layer to the per-capita production project. It does **not** replace V2 or fit progression data into the model. The purpose is to test whether the raw main-world quantity

\[
\frac{B_t}{A_t}
\]

can be treated as a smooth main-account productivity process across large updates.

The event catalogue is `Maple/data/maple_patch_event_layer_2024_2026.csv`.

## Event taxonomy

- `population_inflow_shock`: patches/events likely to bring many returning/new/low-progression accounts into `A_t`.
- `boss_accessibility_shock`: HP reductions, pattern simplification, HEXA/skill power, Genesis acceleration, or other changes that alter boss-clear capacity.
- `reward_schedule_shock`: direct changes to Strong Crystal prices/caps or other mechanical meso rewards.
- `new_boss_frontier_shock`: new bosses that open a new production frontier for the upper tail.
- `growth_support`: broad progression support that can change account productivity with a lag.

A single patch may have several tags. This matters because population dilution and genuine productivity shocks can act in opposite directions in the same week.

## Pure-main event study

The following comparisons use only weeks with `C_t=0` unless explicitly noted. `B/A` means the aligned boss-production index divided by main-world active accounts.

### MILESTONE: clear population-composition dilution

2024-06-13 -> 2024-06-27:

- `A`: 301,131 -> 366,107, **+21.6%**
- `B`: 19.954 -> 22.706, **+13.8%**
- `B/A`: **-6.4%**

The update and its growth events expanded the active population faster than boss production. This is exactly the sign expected if new/returning accounts have lower boss-production capacity than the incumbent population.

### Talahat / September 2024: genuine productivity dominates

2024-09-05 -> 2024-09-19:

- `A`: 303,541 -> 309,978, **+2.1%**
- `B`: 24.426 -> 26.834, **+9.9%**
- `B/A`: **+7.6%**

There is little population dilution here. Production rises substantially faster than accounts.

### Azmoth introduction: modest negative movement

2024-10-10 -> 2024-10-24:

- `A`: 308,321 -> 294,497, **-4.5%**
- `B`: 27.349 -> 25.399, **-7.1%**
- `B/A`: **-2.8%**

This is not an entrant-dilution episode because the account count falls. It should not be pooled with summer/winter population shocks.

### Special World / What's NEXT period

2024-11-14 -> 2024-11-28:

- `A`: 259,181 -> 282,394, **+9.0%**
- `B`: 24.770 -> 26.498, **+7.0%**
- `B/A`: **-1.8%**

The sign again matches mild compositional dilution.

### NEXT pre-launch inflow is extremely strong

The largest composition warning occurs even before the 2024-12-19 Challenger opening. From 2024-12-05 to 2024-12-12:

- `A`: 270,955 -> 353,878, **+30.6%**
- `B`: 30.426 -> 30.921, **+1.6%**
- `B/A`: **-22.2%**

The exact cause should be described as a pre-launch/showcase/event inflow rather than attributed mechanically to the 12/19 patch itself, because the weekly population jump precedes the live date. Econometrically, however, the point is decisive: `A_t` can change composition so sharply that `B/A` moves by more than twenty percent without a comparable change in total boss production.

### ASSEMBLE 2025: dilution before the patch, productivity shock on the patch

2025-06-05 -> 2025-06-12:

- `A`: 316,173 -> 425,334, **+34.5%**
- `B`: 33.961 -> 34.338, **+1.1%**
- `B/A`: **-24.8%**

Then 2025-06-12 -> 2025-06-19:

- `A`: **+14.1%**
- `B`: **+22.6%**
- `B/A`: **+7.5%**

This two-stage pattern is especially informative. A large pre-launch population influx first dilutes average boss productivity; the live update then raises boss production faster than the population. A one-factor smooth counterfactual cannot represent both mechanisms.

### CROWN: another dilution episode

2025-12-11 -> 2025-12-18:

- `A`: 283,675 -> 320,480, **+13.0%**
- `B`: 42.506 -> 44.949, **+5.7%**
- `B/A`: **-6.4%**

Again a major winter growth update brings `A` up faster than boss production.

### OVERDRIVE 1: the key counterexample

2026-06-11 -> 2026-06-18:

- `A`: 336,357 -> 393,763, **+17.1%**
- `B`: 77.884 -> 103.302, **+32.6%**
- `B/A`: **+13.3%**

This does **not** contradict the composition hypothesis. OVERDRIVE 1 simultaneously introduced a very large genuine boss-accessibility shock: broad boss HP reductions/system changes and Genesis acceleration. That direct productivity effect was strong enough to dominate entrant dilution.

## Empirical conclusion from non-Challenger weeks

The pure-main history rejects the simple assumption that

\[
\mu_t^M=B_t/A_t
\]

is a single smooth process through major updates.

At least two distinct mechanisms are visible:

\[
\text{population inflow} \Rightarrow A_t \text{ rises faster than }B_t \Rightarrow B_t/A_t \text{ falls},
\]

and

\[
\text{boss/power shock} \Rightarrow B_t \text{ can rise faster than }A_t \Rightarrow B_t/A_t \text{ rises}.
\]

Therefore the V2 linear boundary bridges are useful low-dimensional historical decompositions, but they are not yet sufficient around major population-composition shocks.

## Season 1 reinterpretation

Three events matter materially.

1. **2025-01-16 Strong Crystal weekly world cap 180 -> 90.** This is a direct production constraint on multi-boss-account behavior and was not represented in V2 S1. It is especially relevant because the main-world average account can contain multiple bossing characters.
2. **2025-02-20 Baldriks / Champion update.** A new upper-tail boss frontier and progression support can increase boss capacity.
3. **2025-03-20 Destiny/HEXA/Starforce/boss-system update.** V2 S1 rises from roughly `w=0.40` on 3/13 to `0.49` on 3/20, `0.57` on 3/27 and `0.64` on 4/03. A large genuine power/accessibility update is therefore a plausible structural explanation rather than evidence that the residual model is merely noisy.

The 4/17 crystal price adjustment remains a direct reward-schedule intervention and should continue to use an external reward factor.

## Season 2 reinterpretation

The V2 trajectory is already substantially more plausible after removal of the endogenous patch multiplier. The patch layer adds structural explanations for further movement:

- 2025-07-17: new Ascent/HEXA power shock. V2 `w` rises into the 0.38 range and reaches about 0.46 by 7/31.
- 2025-08-21: new boss First Adversary expands the upper-tail production frontier; `w` subsequently reaches roughly 0.55 by 8/28.
- 2025-10-23: direct crystal reward adjustment. This remains an exogenous reward-schedule break, not a smooth productivity change.

Thus Season 2 should not be expected to follow a featureless monotone progression curve. Several discrete power/frontier/reward changes are real.

## Season 3 reinterpretation

The previous V2 validation called the `2/26 -> 4/16` decline a progression contradiction. The patch event study substantially changes that interpretation.

### February high is structurally plausible

Season 3 opened in late December. Without the later fast Genesis Pass regime, an approximately 10-11 week liberation wave places the first large cohort around late February/early March. Independently, the 2026-02-12 update adds Jupiter, Destiny second transcendence and broad progression support.

Therefore the V2 high around 2026-02-26 should no longer be treated as an automatic falsification.

### March collapse is strongly contaminated by `A_t` composition

From 2026-03-12 to 2026-03-26:

- `A`: 244,263 -> 327,578, about **+34%**
- `B`: 61.561 -> 67.913, about **+10%**
- mixed `B/A`: approximately `2.52e-4 -> 2.07e-4`, about **-18%**

The 3/19 update simultaneously brings a large anniversary/growth population shock and real boss-accessibility improvements. The active-account denominator therefore becomes much less comparable to the pre-3/19 population. A V2 counterfactual that keeps main-account productivity on a smooth bridge interprets much of this compositional dilution as a loss of Challenger residual production.

This is now the leading explanation for the apparent late-S3 `w` collapse.

### April boundary is also not clean

The 2026-04-16 common-core / Helena update is a power/frontier shock one week before the first post-season pure-main anchor used by V2. Therefore the 2026-04-23 endpoint is not a neutral continuation of the pre-March main-world regime. This weakens a simple two-boundary linear bridge further.

## Season 4 reinterpretation

The 7/30 feature is no longer best described as an unexplained statistical spike.

- OVERDRIVE 1 on 6/18 dramatically reduces boss HP / changes boss systems and accelerates Genesis liberation.
- The Challenger cohort begins around the same period, so many fast-progressing accounts reach liberation several weeks later.
- 7/23 adds new HEXA skills, producing a direct combat-power shock.
- The weekly observation on 7/30 is the first full row after that 7/23 power update and coincides with the expected liberation/progression wave.

The observed mixed `B/A` moves from about `3.90e-4` on 7/23 to `5.02e-4` on 7/30, roughly **+29%**, while `A_t` is falling rather than surging. This is the opposite signature from a population-dilution artifact and is consistent with a genuine boss-productivity shock.

Hence the V2 instruction to remove an endogenous OVD2 multiplier remains correct, but the resulting residual jump can still be economically real.

## Implication for the next model

Do **not** respond by smoothing `w_t` harder.

The next identification problem is on the main-world side. The evidence suggests separating at least conceptually

\[
A_t=A_t^{incumbent}+A_t^{entrant}
\]

and allowing entrants to carry a lower short-run boss-production exposure:

\[
A_t^{eff}=A_t^{incumbent}+\lambda_t A_t^{entrant},\qquad 0\le\lambda_t<1.
\]

At the same time, externally identified direct reward/accessibility shocks must remain separate. In particular, an entrant-dilution correction must **not** erase real jumps such as OVERDRIVE 1 or new HEXA/Genesis-liberation waves.

Before fitting a V3, the next useful step is to estimate the entrant-dilution response from pure-main episodes (MILESTONE, NEXT pre-launch, ASSEMBLE pre-launch, CROWN) and test whether a common short-run dilution/recovery profile exists. If it does, that profile can be used as an external correction for the main-world counterfactual during Challenger seasons without fitting to Challenger progression itself.
