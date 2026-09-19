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

## Round 6

| Field | Value |
|---|---|
| Round | 6 |
| Date | 2026-09-18 KST |
| Sport | MLB |
| Market timing | Pregame |
| Total effective stake | 111,000 KRW |
| Ticket A stake | 56,000 KRW |
| Ticket A legs | Boston Red Sox ML × New York Mets ML |
| Ticket A combined odds | 3.33 |
| Ticket A potential payout | 186,480 KRW |
| Ticket B stake | 55,000 KRW |
| Ticket B legs | Minnesota Twins ML × Chicago White Sox ML |
| Ticket B combined odds | 3.63 |
| Ticket B potential payout | 199,650 KRW |
| Maximum combined payout | 386,130 KRW |
| Cash deposit | UNKNOWN |
| Promo state | `S1_AFTER_LOSS_5` (carried forward from Round 5; exact funding composition UNKNOWN) |
| Bonus rate | UNKNOWN |
| Bonus amount | UNKNOWN |
| Existing points used | UNKNOWN |
| Result | L (both tickets lost) |
| Result detail | Ticket A: BOS beat TEX 4-3, but NYM lost 0-3 to PHI. Ticket B: CWS beat DET 3-1, but MIN lost 4-5 to LAA. |
| Realized payout | 0 KRW |
| Loss cashback | 2,220 points (= 2% of 111,000 KRW total stake) |
| Next promo state | `S1_AFTER_LOSS_5` |
| Notes | Ticket A @ 3.33 and Ticket B @ 3.63 both lost by one leg. Four-game no-shared-leg structure was preserved. |

## Round 6 arithmetic

```text
Ticket A: 56,000 * 3.33 = 186,480 KRW
Ticket B: 55,000 * 3.63 = 199,650 KRW
Total stake                 = 111,000 KRW
Maximum combined payout     = 386,130 KRW
Maximum combined net profit = 275,130 KRW
realized payout              = 0 KRW
loss cashback                = 111,000 * 0.02 = 2,220 points
```


## Round 7

| Field | Value |
|---|---|
| Round | 7 |
| Date | 2026-09-18 KST |
| Sport | NFL |
| Market timing | Pregame |
| Game | Detroit Lions @ Buffalo Bills |
| Legs | 2 |
| Leg 1 | Buffalo Bills -5.5 @ 1.92 |
| Leg 2 | Over 54.5 @ 1.88 |
| Offered combined odds | 3.61 |
| Cash budget | 120,000 KRW |
| Promo state | `S1_AFTER_LOSS_5` |
| Bonus rate | 5% |
| Bonus amount | 6,000 KRW |
| Existing points used | 2,000 KRW |
| Effective stake | 128,000 KRW |
| Potential payout | 462,080 KRW |
| Result | W |
| Result detail | Buffalo Bills beat Detroit Lions 41-31. Bills -5.5 covered by 4.5 points beyond the spread; game total 72 cleared Over 54.5 by 17.5 points. |
| Realized payout | 462,080 KRW |
| Loss cashback | 0 |
| Next promo state | `S2_NO_BONUS_BALANCE` |
| Notes | User confirmed Round 7 locked in as Bills -5.5 × Over 54.5 at combined odds 3.61. Both legs won. |

## Round 7 arithmetic

```text
cash budget          = 120,000 KRW
5% bonus             =   6,000 KRW
existing points      =   2,000 KRW
effective stake      = 128,000 KRW
combined odds        = 3.61
potential payout     = 128,000 * 3.61 = 462,080 KRW
potential net profit = 462,080 - 120,000 = 342,080 KRW versus fresh cash budget
profit vs effective stake = 462,080 - 128,000 = 334,080 KRW
final score           = BUF 41 - 31 DET
```


## Round 8

| Field | Value |
|---|---|
| Round | 8 |
| Date | 2026-09-20 KST |
| Sport | MLB |
| Market timing | Pregame |
| Available cash budget | 120,000 KRW |
| Bonus rate | 10% |
| Bonus amount | 12,000 KRW |
| Existing points available | 4,000 KRW |
| Total effective bankroll available | 136,000 KRW |
| Ticket A stake | 50,000 KRW |
| Ticket A legs | CLE–ATH Over 7.5 × TOR–TEX Over 7.5 × MIL–BAL Over 7.5 |
| Ticket A structure | 3-leg parlay |
| Ticket A odds promotion | 3% total-odds bonus (user-stated) |
| Ticket A locked combined odds | 6.92 |
| Ticket A potential payout | 346,000 KRW |
| Ticket B stake | 64,080 KRW |
| Ticket B legs | CWS–DET Over 8 × CHC–CIN Over 9 |
| Ticket B structure | 2-leg parlay |
| Ticket B locked combined odds | 3.55 |
| Ticket B potential payout | 227,484 KRW |
| Total staked | 114,080 KRW |
| Effective bankroll left unbet | 21,920 KRW |
| Maximum combined payout | 573,484 KRW |
| Maximum net profit vs amount staked | 459,404 KRW |
| Promo state | 10% bonus active (exact canonical state label UNKNOWN) |
| Result | PENDING |
| Realized payout | PENDING |
| Loss cashback | PENDING |
| Next promo state | PENDING |
| Notes | User confirmed both tickets locked. Ticket A locked at 6.92 and receives a user-stated 3% total-odds bonus for being a 3-leg parlay. Do not reconstruct the pre-boost price from earlier quoted component odds; the locked combined price is canonical. |

## Round 8 arithmetic

```text
cash budget                    = 120,000 KRW
10% bonus                      =  12,000 KRW
existing points                =   4,000 KRW
effective bankroll available   = 136,000 KRW

Ticket A: 50,000 * 6.92        = 346,000 KRW
Ticket B: 64,080 * 3.55        = 227,484 KRW
total staked                   = 114,080 KRW
effective bankroll left unbet  =  21,920 KRW
maximum combined payout        = 573,484 KRW
maximum net profit vs stake    = 459,404 KRW
```
