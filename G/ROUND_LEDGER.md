# Round Ledger

This ledger is the canonical round-by-round betting record. Do not infer missing historical fields; use `UNKNOWN` unless supported by an explicit prior record.

## Recording rules

- Record each round immediately after placement.
- Update the same round when result, payout, cashback, and next promo state become known.
- Single-leg evaluation rule: use `displayed decimal odds - 0.10` when comparing value.
- Preserve bookmaker promo state explicitly: `S0_FIRST_DEPOSIT_10`, `S1_AFTER_LOSS_5`, `S2_NO_BONUS_BALANCE`.
- Loss cashback rule from the canonical betting framework: 2% of stake is credited as points, subject to point valuation/rolling constraints.
- Never infer unsupported historical data. Mark it `UNKNOWN`.

## Round 1–4

Historical round details are not yet recoverable from the current canonical repository. They remain `UNKNOWN` pending explicit source recovery from prior chat/local records.

## Round 5

| Field | Value |
|---|---|
| Round | 5 |
| Date | 2026-09-16 KST |
| Sport | MLB |
| Market timing | Pregame |
| Legs | 2 |
| Leg 1 | Chicago White Sox ML |
| Leg 2 | Detroit Tigers ML |
| Offered combined odds | 4.43 |
| Cash deposit | 90,000 KRW |
| Promo state | `S0_FIRST_DEPOSIT_10` |
| Bonus rate | 10% |
| Bonus amount | 9,000 KRW |
| Existing points used | 3,000 KRW |
| Effective stake | 102,000 KRW |
| Potential payout | 451,860 KRW |
| Result | L |
| Result detail | Detroit won; Chicago White Sox lost 6–7 to Cleveland |
| Realized payout | 0 KRW |
| Loss cashback | 2,040 points (= 2% of 102,000 KRW stake) |
| Next promo state | `S1_AFTER_LOSS_5` |
| Notes | Round 5 analysis included the 07:40 KST games. |

## Round 5 arithmetic

```text
cash                = 90,000
10% bonus           =  9,000
existing points     =  3,000
stake               = 102,000
combined odds       = 4.43
potential payout    = 102,000 * 4.43 = 451,860
loss cashback       = 102,000 * 0.02 = 2,040 points
```
