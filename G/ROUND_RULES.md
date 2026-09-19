# Round Execution Rules

These rules supplement `G/README.md` and `G/ROUND_LEDGER.md`.

## Pricing / selection

1. For a 1-leg bet, evaluate value using:

```text
evaluation_odds = displayed_decimal_odds - 0.10
```

2. Multi-leg tickets use the bookmaker's actual offered combined decimal odds unless an explicit adjustment rule is documented for that round.

3. Fixed project rule — 3-leg parlay odds bonus:

```text
3-leg parlay final odds = bookmaker combined odds with +3% total-odds bonus applied
```

For recordkeeping, the actually locked final combined odds are canonical. Do not reverse-engineer or overwrite a locked price from component odds unless explicitly requested.

4. Keep `displayed odds`, `evaluation odds`, `offered parlay odds`, and `effective fresh-cash odds` conceptually separate.

## Round recording

For every placed round, immediately append the ticket to `ROUND_LEDGER.md` with all known funding and pricing fields. When the event settles, update the same round with:

- W/L result
- realized payout
- point cashback
- next promo state
- closing-line data when available

Do not reconstruct missing historical values by guesswork. Use `UNKNOWN` until an explicit source is recovered.

## Promo transition

The existing canonical promo state machine applies:

- `S0_FIRST_DEPOSIT_10`: first deposit of the day, +10%
- `S1_AFTER_LOSS_5`: after a loss and depleted balance, next deposit +5%
- `S2_NO_BONUS_BALANCE`: balance remains after a win, no deposit bonus

Loss cashback remains 2% of stake as points under the existing framework.

## Round 5 note

Round 5 MLB analysis explicitly included the 07:40 KST games; they are not to be skipped merely because start time is close.
