# Meaegi data parsing and methodology

## 1. Source payloads

2026-09-11 메애기 통계 페이지에서 Chrome DevTools를 통해 Next.js RSC 응답을 확보했습니다.

### Population

RSC 내부의 다음 fallback 데이터를 파싱했습니다.

`/api/maplestory/statistics/all-population?type=all-population`

각 관측치는

```json
{"date":"YYYY-MM-DD","group1":...,"group2":...}
```

형태입니다.

- 관측 수: 141주
- 기간: 2023-12-28 ~ 2026-09-03
- 이 프로젝트의 경제 분석 모집단: `group1`
- `group2`는 에오스·헬리오스(구 리부트) 계열로 분리하여 분석에서 제외합니다.
- `total = group1 + group2`는 원자료 확인용 파생열입니다.

메소 총생산 공식 그래프 역시 구 리부트가 포함되지 않는다는 전제하에 population 분모도 동일 모집단으로 맞춥니다.

## 2. Starforce

스타포스 statistics RSC의 `pageProps`에서 두 배열을 직접 파싱했습니다.

- `counts`: 일별 강화 횟수
- `costs`: 일별 소모 메소

두 배열 모두 541개 날짜가 존재하며 날짜가 1:1 대응합니다.

- 기간: 2025-03-20 ~ 2026-09-11
- `meso_per_attempt = meso_cost / attempts`

강화 이벤트가 있는 일요일 등에는 실제로 매우 큰 spike가 존재합니다. 따라서 추세 분석에서는 일별 원자료와 함께 주간 합계를 별도로 사용합니다.

주간 자료는 목요일~수요일을 한 주로 보고 합산한 뒤 목요일 날짜로 라벨링했습니다. 이는 population 통계의 주간 날짜축과 쉽게 결합하기 위한 분석 편의상의 변환입니다.

## 3. Probability table

RSC payload의

- `destroyDecrease0`
- `destroyDecrease30`

배열에서 `star`, `total`, `success`, `fail`, `destroy`를 추출했습니다.

이 자료는 메소 소각 시계열 복원 자체의 핵심 입력은 아니며, 메애기 스타포스 데이터의 내부 일관성 및 강화 행동 분석에 사용할 수 있습니다.

## 4. What is NOT identified yet

현재 전달받은 RSC payload에는 다음 시계열이 확인되지 않았습니다.

1. 날짜별 메애기 API 등록/연동 캐릭터 수
2. 날짜별 메애기 표본의 전투력 분포
3. 월드별 일별 스타포스 `counts/costs`

따라서 `meaegi_starforce_daily.csv`의 `meso_cost`는 **표본 총소모량**입니다.

전체 게임의 스타포스 소각량을 추정하려면 최소한 시간에 따른 표본 coverage 변화에 대한 보정이 필요합니다.

가장 단순한 후보는

\[
\widehat{SF}_t =
SF^{sample}_t
\times
\frac{N^{group1}_t}{n^{sample}_t},
\]

이지만 메애기 등록 유저가 랜덤 표본이 아니므로 이 식을 그대로 정본으로 쓰지 않습니다.

전투력 bucket별 표본 정보가 확보되면

\[
\widehat{SF}_t =
\sum_k N_{k,t}\bar s_{k,t}
\]

형태의 post-stratification을 우선 검토합니다.

## 5. Relation to total meso destruction

2025 NDC의 “스타포스가 전체 메소 소비의 약 25% 이상”이라는 공개 자료는 전 기간에 고정 적용하지 않습니다.

이 프로젝트의 현재 계획은:

1. 스타포스 표본 시계열의 coverage를 보정한다.
2. NDC 시점에서 스타포스/전체소각 비율을 scale anchor로 활용 가능한지 검증한다.
3. 전체 소각량의 **상대 시계열**을 추정한다.
4. 기존에 복원한 총생산 상대 시계열과 결합한다.
5. `Δ잔고 = 생산 - 소각`을 누적한다.
6. 2023년에 공개된 공식 총 메소 잔고 **상대 그래프**와 모양을 맞춰 검증한다.

공식 잔고 그래프에 절대 메소량이 공개되지 않았으므로 최종 결과 역시 절대 stock이 아니라 상대지수입니다.

## 6. Important caveat

`data/meaegi_population_starforce_weekly.csv`의

- `meso_cost_per_group1_user`
- `attempts_per_group1_user`

는 메애기 표본 총량을 전체 `group1` 인구로 단순 나눈 **diagnostic ratio**입니다.

이는 표본 coverage가 100%라는 가정 아래에서만 실제 1인당 소비량이 되므로, 현재는 경제학적 추정치가 아니라 시계열 비교용 보조열로만 사용합니다.
