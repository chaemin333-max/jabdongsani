# 총 메소 생산량 원시 복원 정본

2026-09-12 복구 확인: part00에서 누락된 base64 문자 1개를 복구했고, 아래 기존 SHA-256과 정확히 일치하는 JSON을 `Maple/data/meso_total_production_raw_canonical.json`에 저장했다. 기존 복원 스크립트도 정상 실행된다. 복구 기록은 `Maple/data/boss_decomposition_research_20260912/raw_recovery_receipt.json`에 있다. 이 JSON에는 총생산 좌표 1,664개만 있으며 고해상도 보스 배열은 포함돼 있지 않다.

총생산 원시 곡선 정본은 이미지 복원 단계에서 확정된 `total.month_coordinate` / `total.index` 배열이다.

원본 JSON은 61,198 bytes이며 SHA-256은:

`63e41f7c7d5c384971524a56df0dcc01a25fd888f808e9174b3195feb9dd6b41`

GitHub Contents API 전송 제약 때문에 exact gzip+base64 payload를 다음 4개 파일로 분할 보존한다.

- `Maple/data/raw/meso_total_production_raw_canonical.part00.b64`
- `Maple/data/raw/meso_total_production_raw_canonical.part01.b64`
- `Maple/data/raw/meso_total_production_raw_canonical.part02.b64`
- `Maple/data/raw/meso_total_production_raw_canonical.part03.b64`

복원:

```bash
python Maple/scripts/restore_meso_total_raw.py
```

복원 결과:

`Maple/data/meso_total_production_raw_canonical.json`

JSON 구조:

```text
unit
  = 2025년 9월 S25 평균 총생산 = 100

total.month_coordinate
  = 이미지에서 복원된 고해상도 x 좌표

total.index
  = 해당 좌표의 총 메소 생산 상대지수

source_data
normalization_S25_height
event_notes
```

## 분석용 주간 패널과의 관계

`Maple/data/maple_production_calibration_inputs_weekly.csv`의 `P_total_newage100`은 이 원시 총생산 곡선을 목요일 공통 날짜축에 정렬하고 NEW AGE 기준으로 환산한 downstream 분석 입력이다.

따라서:

```text
원시 이미지 복원 곡선
meso_total_production_raw_canonical.json
        ↓ 날짜 정렬 / 배율 환산
maple_production_calibration_inputs_weekly.csv :: P_total_newage100
        ↓ V1/V2/V3 calibration
per_capita_production_v3_weekly.csv
```

향후 총생산 곡선을 다시 픽셀 복원하지 않는다. 원시곡선 검증·재현은 이 payload를 기준으로 한다.
