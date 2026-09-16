# Round Ledger Schema

Required fields for each round:

```text
round_id
datetime_kst
sport
market_timing
legs
leg_details
displayed_leg_odds
offered_combined_odds
single_leg_evaluation_adjustment
cash_deposit
promo_state
bonus_rate
bonus_amount
points_used
effective_stake
potential_payout
result
realized_payout
loss_cashback_points
next_promo_state
closing_odds
notes
```

Unknown historical values must be stored as `UNKNOWN`, not reconstructed by inference.
