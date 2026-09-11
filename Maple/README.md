# Maple

메이플스토리 경제 지표 복원/분석용 데이터 폴더입니다.

## 현재 포함된 데이터

- `data/meaegi_population_weekly.csv`
  - 메애기 인구수 통계 RSC payload에서 직접 파싱.
  - 2023-12-28 ~ 2026-09-03, 주간.
  - `group1`을 이 프로젝트의 본섭 인구 지표로 사용합니다.
  - 에오스·헬리오스(구 리부트)는 메소 총생산 공식 지표의 모집단과 맞지 않으므로 분석에서 제외합니다.

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

자세한 파싱·사용 원칙은 `docs/METHODOLOGY.md`를 참고하세요.

## 핵심 경고

메애기 스타포스 자료는 등록/연동된 표본에서 수집된 자료입니다. 따라서

`sample starforce cost × (전체 인구 / 표본 인구)`

를 곧바로 전체 소각량으로 간주하지 않습니다. 날짜별 표본 규모와 표본의 스펙 분포가 추가로 확보되면 coverage 보정 및 층화 추정을 검토합니다.

2025 NDC에서 공개된 스타포스의 메소 소비 비중(약 25%+)도 전 기간 고정계수로 쓰지 않고, 전체 소각량 상대 시계열의 scale anchor 후보로만 취급합니다.
