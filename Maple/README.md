# Maple

## 2026-09-12 주간 보스 생산성 가중치

신규 보스 보상을 반영한 본섭·챌린저스 조건부 분해의 주간 `w`와 시즌 평균·패치 전후 비교는 [보고서](docs/BOSS_PRODUCTIVITY_WEIGHTS_2026-09-12.md), `data/boss_productivity_weights_20260912/`에 있습니다. 마지막 주 w=0.557이며, 기존 V3 총생산 Q와는 별도의 보스 생산성 지표입니다.

## 2026-09-12 보스 생산 공동분해 연구

`docs/BOSS_DECOMPOSITION_JOINT_V1_RESULTS_2026-09-12.md`에 실제 공동 적합·시나리오·구간가림·가상자료 검사를 기록했습니다. 결과는 `data/boss_decomposition_joint_v1/`, 재현 코드는 `scripts/fit_boss_decomposition.py`입니다. 분석 종점은 2026-08-21이며 마지막 공동 주간 관측은 08-20입니다. 특히 마지막 챌린저스 생산 몫은 약하게 식별되므로 새 중심값을 정본으로 승격하지 않았습니다. 기존 V3는 비교용으로 보존합니다.

메이플스토리 경제 지표 복원/분석용 데이터 폴더입니다.

## 현재 상태 — V3 dual-anchor calibration

현재 per-capita 생산량 calibration의 최신 산출물은 다음입니다.

- `data/per_capita_production_v3_weekly.csv` — V3 전체 주간 시계열.
- `data/per_capita_production_v3_season_summary.csv` — 시즌별 V3 요약.
- `docs/PER_CAPITA_PRODUCTION_V3.md` — pure-main entrant dilution + late/static Challenger anchor 방법론과 결과.
- `scripts/recompute_per_capita_v3.py` — V3 재현 계산 스크립트.

V3의 핵심은 raw 본섭 활동계정 `A_t`를 항상 동질적인 생산 exposure로 보지 않는 것입니다. 대형 유입 직후에는 Challenger-free 구간에서 역산한 entrant exposure를 이용해 `A_t^{eff}`를 만들고,

\[
B_t=A_t^{eff}\mu_t^M+C_t\mu_t^C,
\qquad
E_t=A_t^{eff}+w_tC_t,
\qquad
Q_t=P_t/E_t
\]

를 사용합니다. Challenger 후반부에는 별도의 late/static `muC` anchor로 Challenger 생산량을 역추적합니다. Progression 자료는 fit 입력이 아니라 독립 validation layer로 유지합니다.

Season 4는 2026-09-11 현재 상태를 종료 상태의 provisional estimate로 취급합니다. live Challenger-tier count `189,757`은 validation metadata이며, 활동계정 proxy `C_t`를 대체하지 않습니다. 실제 post-season pure-main 자료가 추가되면 재캘리브레이션합니다.

## 이전 버전

- V2: `data/per_capita_production_v2_weekly.csv`, `docs/PER_CAPITA_PRODUCTION_V2.md`
  - mixed `B/A`에서 추출한 endogenous within-season patch multiplier contamination을 제거한 버전.
- V1: `data/per_capita_production_final_weekly.csv`, `docs/PER_CAPITA_PRODUCTION_METHOD.md`
  - historical first-pass artifact. 일부 Challenger residual 산술 불일치가 있으므로 최신 분석의 기준으로 사용하지 않습니다.

## 연구 목표

현재 목표는 챌린저스 경제모형 자체가 아니라, 총 메소 생산에서 생산능력 보정 population exposure를 제거한 단일 시계열을 만드는 것입니다.

\[
\boxed{Q_t=\frac{P_t}{E_t}}
\]

공개적으로는 “1인당 메소 생산량”이라고 부를 수 있지만, 기술적으로는 **본섭-equivalent productive exposure account당 메소 생산량**입니다.

처음 합류한 연구자는 다음 순서로 읽으세요.

1. `docs/HANDOFF_PER_CAPITA_2026-09-11.md`
2. `docs/PATCH_EVENT_STUDY_PER_CAPITA.md`
3. `docs/DUAL_ANCHOR_V3_PILOT.md`
4. `docs/PER_CAPITA_PRODUCTION_V3.md`

원 입력은 `data/maple_production_calibration_inputs_weekly.csv`입니다. `P_t`, `B_t`, 본섭 계정수 `A_t`, Challenger 활동계정 proxy `C_t`가 공통 목요일 날짜축에 이미 정렬돼 있습니다.

**NOW 그래프를 다시 픽셀 복원하거나 메애기 인구를 다시 수집하지 마세요.** 개인 후기·가이드·개인 인증은 population distribution 자료로 사용하지 않습니다.

## 주요 데이터

- `data/maple_production_calibration_inputs_weekly.csv` — per-capita 연구의 1차 입력패널.
- `data/maple_patch_event_layer_2024_2026.csv` — patch/live event layer.
- `data/dual_anchor_calibration_pilot.csv` — pure-main entrant dilution 및 late/static anchor pilot.
- `data/per_capita_production_v3_weekly.csv` — 최신 V3 시계열.
- `data/per_capita_production_v3_season_summary.csv` — 최신 시즌 요약.
- `data/meaegi_population_weekly.csv` — 본섭 population proxy.
- `data/challengers_population_weekly_seasons1_4.csv` — Challenger activity proxy.
- `data/meaegi_starforce_daily_2025.csv`, `data/meaegi_starforce_daily_2026.csv`, `data/meaegi_starforce_weekly.csv` — 스타포스 별도 병렬 트랙.
- `data/source_manifest.json` — 원자료 범위와 제한사항.

## 핵심 경고

기존 `A+C` 동일가중 per-user 지표는 최종 정본이 아닙니다. V3에서도 `A_t^{eff}`와 `w_tC_t`는 생산능력 exposure이며 literal unique-human count가 아닙니다.

스타포스/소각량/총 메소 잔고 복원은 별도 병렬 트랙으로 유지합니다.
