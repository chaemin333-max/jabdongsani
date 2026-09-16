# G — Betting Data, Edge, and Kelly Framework

이 폴더는 스포츠/이스포츠 멀티레그 베팅의 데이터 수집, 엣지 측정, 프로모션 반영, Kelly sizing을 일관되게 기록하기 위한 정본 노트다.

> Round별 실제 체결·결과 기록은 `G/ROUND_LEDGER.md`를 정본으로 사용한다. 실행 규칙은 `G/ROUND_RULES.md`를 따른다.

## 1. 기본 원칙

이 시스템의 목표는 단순 적중률이 아니라 다음 네 요소를 분리해서 측정하는 것이다.

1. **Selection edge**: 시장 대비 개별 선택 자체가 좋은가.
2. **Correlation edge**: 서로 상관된 leg를 bookmaker가 단순 곱으로 가격화할 때 생기는 오가격이 있는가.
3. **Promo edge**: 입금 보너스, cashback, 고정 포인트가 기대값을 얼마나 개선하는가.
4. **Sizing edge**: 추정된 edge를 Kelly 또는 portfolio Kelly로 얼마나 효율적으로 배분하는가.

특히 현재 사용하는 bookmaker는 멀티레그에서 별도의 correlation haircut 없이 leg별 decimal odds를 곱하는 구조를 사용한다. 따라서 positive-correlation parlay가 핵심 탐색 대상이 될 수 있다.

---

## 2. Bet schema

각 베팅은 최소한 아래 필드를 기록한다.

| Field | Description |
|---|---|
| ID | 순차 번호, 예: `#001` |
| Date/time | 베팅 시각 |
| Sport | NFL, LoL 등 |
| Match | 경기명 |
| Market timing | `pregame`, `live-before-map-start` 등 |
| Legs | 2-leg / 3-leg |
| Leg details | 각 leg의 market, line, odds |
| Naive product odds | 각 leg odds의 단순 곱 |
| Offered parlay odds | bookmaker가 실제 제시한 parlay odds |
| Promo state | 아래 state machine 참조 |
| Cash deposit | 새로 넣은 현금 |
| Bonus | 입금 보너스 |
| Existing points used | 기존 포인트 사용액 |
| Fixed points | 출석/첫 입금 등 고정 포인트 |
| Stake | 실제 총 베팅액 |
| Potential payout | 적중 시 지급액 |
| Nominal odds | bookmaker 표시 배당 |
| Effective odds | fresh-cash 기준 실질 배당 |
| Economic-capital odds | 기존 포인트 등 기존 자산까지 비용으로 본 배당 |
| Correlation tag | 예: `NFL_DOG_UNDER`, `LOL_DOMINANCE_STACK` |
| Result | W/L |
| Closing odds | 가능하면 기록 |
| Notes | 부상, 밴픽, 라인무브 등 |

---

## 3. Correlation tagging

### 3.1 NFL

대표적인 positive-correlation family:

- `NFL_DOG_UNDER`: underdog spread + game under
- `NFL_FAV_OVER`: favorite side + over
- `NFL_SIDE_TEAMTOTAL`: side + 해당 팀 team total
- `NFL_PLAYER_SCRIPT`: side + 특정 선수 usage/yardage/TD가 같은 game script를 공유

예: `SF +3.5 + U48.5`는 underdog가 경기 내내 접전을 유지하고 전체 scoring pace가 낮은 시나리오에서 두 leg가 동시에 적중하기 쉬우므로 `NFL_DOG_UNDER`로 태깅한다.

### 3.2 LoL

LoL live는 **map 시작 전, 밴픽 종료 후** 구간만 대상으로 한다.

대표적인 family:

- `LOL_DOMINANCE_STACK`: kills handicap + first dragon/tower/first blood 등 우세 상태를 공유
- `LOL_CONTROLLED_STOMP`: kills handicap + kills under + first objective
- `LOL_PACE_OVER`: kill over + first blood + aggressive-objective 계열

핵심 아이디어는 여러 leg가 하나의 latent game state를 공유하는지 기록하는 것이다.

---

## 4. Nominal odds, effective odds, break-even

Decimal odds를 `O`, 실제 승률을 `p`라고 하면 명목 EV는

```text
EV = p * O - 1
```

명목 break-even probability는

```text
p_BE = 1 / O
```

### 4.1 Fresh-cash effective odds

새로 투입한 현금을 `C`, 실제 총 stake를 `S`, 적중 시 payout을 `P`라고 하면

```text
O_eff_fresh = P / C
```

이 값은 입금 보너스와 기존 포인트까지 한 번에 베팅한 경우 fresh cash가 얼마나 증폭되는지 보여준다.

### 4.2 Economic-capital odds

기존 포인트도 이미 보유하던 경제적 자산이라면 그것을 공짜로 보면 안 된다.

기존 포인트의 경제적 가치를 `rho * points`로 두면

```text
Economic capital = fresh cash + rho * existing points
O_eff_econ = payout / Economic capital
```

`rho`는 포인트 1원의 실제 현금화 가치를 뜻한다. 100% rolling이 필요하므로 기본값을 1보다 작게 두고 실제 회수율 데이터로 추정한다.

---

## 5. Promo state machine

현재 bookmaker의 핵심 구조:

- **하루 첫 deposit:** +10%
- **낙첨 후 같은 날 추가 deposit:** +5%씩, 다음 적중 전까지
- **잔고가 있으면 deposit bonus 없음**
- **낙첨 시:** stake의 2% point cashback
- **매일 출석 복권/첫 deposit:** 약 1,000 KRW+의 고정 포인트가 추가될 수 있음
- 포인트는 **100% rolling**이 필요하므로 즉시 cash와 동일 취급하지 않음

이를 상태로 기록한다.

### `S0_FIRST_DEPOSIT_10`

잔고가 없고, 그날 첫 deposit을 하는 상태.

```text
bonus rate = 10%
```

### `S1_AFTER_LOSS_5`

직전 bet이 낙첨되어 잔고가 소진되었고, 다음 deposit에 5% bonus가 붙는 상태.

```text
bonus rate = 5%
```

### `S2_NO_BONUS_BALANCE`

직전 bet이 적중하여 잔고가 남아 있고 추가 입금 bonus가 없는 상태.

```text
bonus rate = 0%
```

이 구조에서는 같은 nominal bet이라도 state별 EV가 크게 달라진다. 따라서 ROI를 반드시 아래처럼 분리한다.

```text
ROI_10%
ROI_5%
ROI_0%
```

실전 전략은 종종 `S0`와 `S1`에서만 bet하고 `S2`에서는 pass하는 형태가 합리적일 수 있다.

---

## 6. Cashback와 point valuation

낙첨 시 2% point cashback이 있다면, stake를 `S`, cashback rate를 `c=0.02`, point valuation을 `rho`라 할 때 낙첨 시 경제적 회수액은

```text
Loss recovery = rho * c * S
```

따라서 단순한 win/loss payoff가 아니라

```text
Win:  + (payout - economic capital)
Loss: - economic capital + point recovery
```

형태로 평가하는 것이 더 정확하다.

고정 출석 포인트와 첫 deposit 보너스 포인트는 bet별 EV가 아니라 **daily subsidy**로 별도 기록하고, 필요하면 그날의 총 투입 fresh cash에 배분한다.

---

## 7. Cash NAV vs Economic NAV

두 개의 bankroll 값을 동시에 추적한다.

```text
Cash NAV = 즉시 출금 가능한 현금
Economic NAV = Cash NAV + rho * Points
```

Kelly denominator는 원칙적으로 경제적 bankroll을 사용하되, promo 자산의 제약이 크면 cash NAV와 economic NAV를 모두 보고 보수적으로 sizing한다.

---

## 8. Kelly sizing

Decimal odds `O`, 실제 승률 추정 `p`일 때 full Kelly 비중은

```text
f* = (O*p - 1) / (O - 1)
```

Half Kelly:

```text
f_half = 0.5 * f*
```

Quarter Kelly:

```text
f_quarter = 0.25 * f*
```

### 예: effective EV +5%

`O = 3.8418`이고 `EV = +5%`라면

```text
O*p - 1 = 0.05
p = 1.05 / 3.8418 ≈ 27.33%
```

따라서

```text
full Kelly ≈ 1.759%
half Kelly ≈ 0.880%
```

100,000 KRW가 half-Kelly stake라면 역산 bankroll은 약

```text
100,000 / 0.008797 ≈ 11.37 million KRW
```

이다.

### Practical rule

승률 추정 오차가 크므로 raw historical hit rate를 그대로 Kelly에 넣지 않는다.

```text
raw p
→ shrinkage / conservative p
→ Kelly
→ optional 0.5x multiplier or hard cap
```

한 티켓 exposure에는 별도 hard cap을 둘 수 있다.

---

## 9. Portfolio / vectorized Kelly

같은 시간대에 여러 독립 경기의 parlay를 동시에 보유한다면 개별 Kelly를 단순 합산하지 않고 portfolio Kelly를 사용한다.

각 bet `i`의 bankroll 비중을 `f_i`, payoff random variable을 `X_i`라 하면

```text
maximize E[ log(1 + sum_i f_i X_i) ]
```

subject to

```text
f_i >= 0
sum_i f_i <= 1
```

서로 독립 경기라도 bankroll을 공유하므로 정확한 해는 individual Kelly의 단순 합과 다르다.

같은 경기/같은 LoL map을 공유하는 여러 bet은 특히 독립으로 보면 안 된다. 이 경우 joint distribution 또는 covariance/correlation 구조를 반영해야 한다.

Sunday NFL처럼 10~15개의 독립 후보가 있을 때는 전체 slate를 한 번에 최적화한 뒤

```text
f_actual = lambda * f_portfolio
```

형태로 half-portfolio-Kelly 등을 적용하는 방식이 적절하다.

---

## 10. Sample-size milestones

전체 n보다 **동일 전략 family 내 n**이 더 중요하다.

대략적인 기준:

- `0–100`: 기록 체계 검증. 결과에 따라 전략을 자주 바꾸지 않음.
- `100–300`: 초기 신호 확인. 명백히 죽은 구조만 제거.
- `300–500`: promo 포함 EV가 양수인지 평가 시작.
- `500–1,000`: empirical-Bayes / shrinkage 기반 p와 fractional Kelly를 사용하기 시작.
- `1,000+`: 특정 전략 family의 실제 edge와 sizing을 진지하게 추정 가능.

승률이 약 30%인 경우 binomial 표준오차가 크므로 수백 건만으로 raw hit rate를 true probability처럼 취급하면 안 된다.

또한 같은 경기에서 여러 parlay를 친 경우 표본을 독립 n개로 세지 않고 **match/map cluster**로 취급한다.

---

## 11. Validation

장기적으로 다음을 분리해서 검증한다.

### 11.1 Promo-adjusted profitability

```text
H1: true p > promo-adjusted break-even p
```

실제 돈을 벌 수 있는 시스템인지 평가한다.

### 11.2 Pure betting edge

```text
H2: true p > nominal break-even p
```

프로모션 없이도 selection/correlation edge가 존재하는지 평가한다.

### 11.3 Closing-line value

가능하면 bet 시점 odds와 closing odds를 비교한다. 장기적으로 closing market을 지속적으로 beat하는지는 중요한 sanity check다.

### 11.4 Out-of-sample persistence

초기 데이터로 발견한 rule을 뒤 데이터에서 재검증한다. 전체 데이터를 보고 전략을 만든 뒤 같은 전체 데이터에서 검증하는 data snooping을 피한다.

---

## 12. Example #001 — SF vs LAR

### Bet

```text
Sport: NFL
Match: San Francisco 49ers vs Los Angeles Rams
Structure: 2-leg correlated parlay
Tag: NFL_DOG_UNDER

Leg 1: SF +3.5 @1.87
Leg 2: U48.5 @1.80
```

Naive product:

```text
1.87 * 1.80 = 3.3666
```

Bookmaker offered:

```text
@3.37
```

즉 별도의 correlation haircut은 사실상 없었다.

### Funding

```text
Fresh cash deposit: 100,000 KRW
First-deposit bonus: 10,000 KRW
Existing points used: 4,000 KRW
Total stake: 114,000 KRW
```

Potential payout:

```text
114,000 * 3.37 = 384,180 KRW
```

### Effective odds

Fresh-cash basis:

```text
384,180 / 100,000 = 3.8418
```

Fresh-cash break-even:

```text
1 / 3.8418 ≈ 26.03%
```

기존 4,000 point를 1:1 경제가치로 본 economic-capital basis:

```text
384,180 / 104,000 ≈ 3.6940
```

Economic-capital break-even:

```text
1 / 3.6940 ≈ 27.07%
```

### Result

```text
Final: SF 26 – 21 LAR
Ticket result: WIN
Potential payout realized: 384,180 KRW
```

---

## 13. Round-recording rule

- 실제 체결된 모든 Round는 `G/ROUND_LEDGER.md`에 즉시 기록한다.
- 결과 확정 후 같은 Round에 `Result`, `Realized payout`, `Cashback`, `Next promo state`를 업데이트한다.
- 과거 Round의 누락값은 추측하지 않고 `UNKNOWN`으로 둔다.
- **1-leg value 비교 시 표시 decimal odds에서 0.10을 차감한 값을 평가배당으로 사용한다.**
