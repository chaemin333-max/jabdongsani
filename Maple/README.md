# Maple

메이플스토리 경제 지표 복원/분석용 데이터 폴더입니다.

## 현재 상태 — V2 calibration

현재 per-capita 생산량 calibration의 최신 산출물은 다음입니다.

- `data/per_capita_production_v2_weekly.csv` — V2 전체 주간 시계열.
- `docs/PER_CAPITA_PRODUCTION_V2.md` — V2 counterfactual, boundary 처리, progression 재검증, V1↔V2 sensitivity.

V1 산출물 `data/per_capita_production_final_weekly.csv`와 `docs/PER_CAPITA_PRODUCTION_METHOD.md`는 **역사적 first-pass artifact로 보존**합니다. 저장된 V1 CSV에는 일부 Challenger 주의 residual 산술 불일치가 확인되었으므로 새 분석의 기준으로 사용하지 마세요. 상세 erratum은 V2 문서를 따릅니다. 문서에 적힌 V1 모델을 정확히 재계산하면 Season 3의 V1 최대 `w`는 2026-02-26의 약 `0.74444`이며, 역사적 CSV에서 보이는 `0.797`은 올바른 V1 모델 출력이 아닙니다.

V2의 핵심 수정은 챌린저스 운영 중인 mixed `B/A`에서 within-season patch multiplier를 추출해 본섭 counterfactual에 다시 넣던 identification contamination을 제거한 것입니다. 결정석 가격을 직접 바꾼 2025-04-17과 2025-10-23만 외생 reward-table factor를 사용하고, Season 3 아즈모스 삭제 및 Season 4 OVERDRIVE 2·3에는 endogenous multiplier를 사용하지 않습니다.

## 현재 최우선 목표

현재 목표는 챌린저스 경제모형 자체를 연구하는 것이 아니라, 다음 최종 시계열을 만드는 것입니다.

\[
Q_t=\frac{P_t}{E_t},\qquad E_t=A_t+w_tC_t
\]

즉 이미 복원된 총 메소 생산량에서 생산능력으로 보정된 population exposure를 제거하여 **본섭-equivalent 유효 생산계정당 메소 생산량**을 구합니다.

처음 합류한 연구자는 다음 순서로 읽으세요.

1. `docs/HANDOFF_PER_CAPITA_2026-09-11.md` — 목표, 고정 가정, 데이터 정의, 금지사항.
2. `docs/NEXT_TASK_PER_CAPITA_PRODUCTION.md` — 최초 first-pass의 실행 순서.
3. `docs/PER_CAPITA_PRODUCTION_V2.md` — 현재 최신 calibration과 validation 결과.

실제 원 입력은 `data/maple_production_calibration_inputs_weekly.csv`입니다. 이 파일에는 공통 목요일 날짜축으로 정렬된 총생산 `P_t`, 보스생산 `B_t`, 본섭 계정수 `A_t`, 챌린저스 계정수 `C_t`가 이미 들어 있습니다.

**NOW 그래프를 다시 픽셀 복원하거나, 메애기 인구를 다시 수집하지 마세요.** Aggregate progression 자료는 counterfactual을 fit하는 입력이 아니라 residual 결과를 독립적으로 검증하는 validation layer입니다. 개인 후기·가이드·개인 인증을 population distribution 자료로 사용하지 않습니다.

패치 날짜 및 총생산 정본의 6개 기준점은 `docs/meso_patch_dates_and_values.md`를 사용합니다.

## 현재 포함된 데이터

- `data/maple_production_calibration_inputs_weekly.csv`
  - per-capita 생산량 연구의 1차 입력패널.
  - 목요일 공통 날짜축.
  - `P_t`, `B_t`, `A_t`, `C_t`, 챌린저스 시즌, boss direct/backcast source flag 포함.

- `data/per_capita_production_v2_weekly.csv`
  - 현재 최신 V2 시계열.
  - `muM_counterfactual`, unconstrained `muC_raw`/`w_raw`, boundary failure flag, canonical `w`, plotting-only `w_plot`, `E`, `Q`, September-2025=100 index 포함.
  - identification failure 주에는 canonical `w`, `E`, `Q`를 NA로 두고, 연속 그래프용 값은 별도의 `w_plot`/`Q_raw_plot` 컬럼에만 둡니다.

- `data/per_capita_production_final_weekly.csv`
  - V1 historical artifact. 일부 Challenger residual 산술 불일치가 있으므로 최신 분석에 직접 사용하지 않습니다.

- `data/meaegi_population_weekly.csv`
  - 메애기 인구수 통계 RSC payload에서 직접 파싱.
  - 2023-12-28 ~ 2026-09-03, 주간.
  - `group1`을 이 프로젝트의 본섭 인구 지표로 사용합니다.
  - 에오스·헬리오스(구 리부트)는 메소 총생산 공식 지표의 모집단과 맞지 않으므로 분석에서 제외합니다.

- `data/challengers_population_weekly_seasons1_4.csv`
- `data/challengers_population_weekly_seasons1_4.json`
  - 메애기 `all-burning-character` raw array 기반 시즌1~4 챌린저스 활동계정 proxy.
  - 계정당 아이템 버닝 캐릭터 1개라는 시즌 규칙을 사용.

- `data/meaegi_starforce_daily_2025.csv`
- `data/meaegi_starforce_daily_2026.csv`
  - 메애기 스타포스 통계 RSC payload의 `counts`와 `costs`를 날짜로 결합.
  - 전체 기간: 2025-03-20 ~ 2026-09-11, 일간.
  - `attempts`: 메애기 표본에서 관측된 스타포스 강화 횟수.
  - `meso_cost`: 메애기 표본에서 관측된 스타포스 메소 소모량.
  - `meso_per_attempt`: 단순 `meso_cost / attempts` 파생값.
  - 이 값은 **전체 게임 스타포스 소각량이 아니라 메애기 표본 합계**입니다.

- `data/meaegi_starforce_weekly.csv`
  - 일별 스타포스 자료를 목요일~수요일 단위로 합산하여 목요일 날짜로 표시.
  - 메애기 주간 인구수와 시계열을 맞추기 위한 분석용 집계입니다.

- `data/meaegi_starforce_probability.csv`
  - RSC payload에 포함된 스타포스 별수별 성공/실패/파괴 집계.

- `data/source_manifest.json`
  - 원자료 범위, 필드, 제한사항을 기록한 manifest.

자세한 기존 파싱 원칙은 `docs/METHODOLOGY.md`를 참고하세요.

## 핵심 경고

기존 `A+C` 동일가중 per-user 지표는 **최종 정본이 아닙니다.** 본섭 한 계정은 본캐와 복수 보스돌이를 포함할 수 있는 반면 챌린저스는 1계정 1주력 캐릭터 중심이므로, 챌린저스는 본섭 평균 계정 대비 생산능력 가중치 `w_t`로 보정해야 합니다.

스타포스/소각량/총 메소 잔고 복원은 별도 병렬 트랙입니다. 현재 per-capita 생산량 분모 calibration과 먼저 섞지 않습니다.
