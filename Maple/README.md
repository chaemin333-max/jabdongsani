# Maple

메이플스토리 경제 지표 복원/분석용 데이터 폴더입니다.

## 현재 최우선 작업 — 여기서 시작

현재 목표는 챌린저스 경제모형 자체를 연구하는 것이 아니라, 다음 최종 시계열을 만드는 것입니다.

\[
Q_t=\frac{P_t}{E_t},\qquad E_t=A_t+w_tC_t
\]

즉 이미 복원된 총 메소 생산량에서 생산능력으로 보정된 population exposure를 제거하여 **본섭-equivalent 유효 생산계정당 메소 생산량**을 구합니다.

다음 연구자는 먼저 아래 두 파일을 읽으세요.

1. `docs/HANDOFF_PER_CAPITA_2026-09-11.md` — 목표, 고정 가정, 데이터 정의, 금지사항.
2. `docs/NEXT_TASK_PER_CAPITA_PRODUCTION.md` — 정확한 실행 순서와 필수 산출물.

실제 계산은 `data/maple_production_calibration_inputs_weekly.csv`에서 바로 시작합니다. 이 파일에는 공통 목요일 날짜축으로 정렬된 총생산 `P_t`, 보스생산 `B_t`, 본섭 계정수 `A_t`, 챌린저스 계정수 `C_t`가 이미 들어 있습니다.

**NOW 그래프를 다시 픽셀 복원하거나, 메애기 인구를 다시 수집하거나, 먼저 인벤을 뒤지는 작업은 하지 마세요.** Aggregate progression 검색은 첫 번째 `Q_t` 시계열을 만든 뒤 residual 결과를 검증하는 2차 단계입니다.

패치 날짜 및 총생산 정본의 6개 기준점은 `docs/meso_patch_dates_and_values.md`를 사용합니다.

## 현재 포함된 데이터

- `data/maple_production_calibration_inputs_weekly.csv`
  - 현재 per-capita 생산량 연구의 1차 입력패널.
  - 목요일 공통 날짜축.
  - `P_t`, `B_t`, `A_t`, `C_t`, 챌린저스 시즌, boss direct/backcast source flag 포함.

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
