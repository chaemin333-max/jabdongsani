# 판독 파일 사용 순서

- **주간 선 값:** `weekly_line_pixels_all.csv`. 한 `date`·`series`에 한 행. `status=direct_weekly_rgb`만 원본에서 색을 분리한 값이다. `date`는 목요일이며 250410의 주간 라벨은 패치 기반 추정이다.
- **주간 점 위치 확인:** `*_WEEKLY_qa.png`. 250410에서는 초록 점이 다른 생산처의 주간 점, 자홍 점이 **직접 판독한 연한 하늘색 아즈모스** 주간 점이다.
- **아즈모스 원본 추적:** `azmoth_light_cyan_raster.csv`, `azmoth_light_cyan_trace_crop.png`. 첫 색 픽셀 x=1087을 2024-10-17에 고정했다.
- **250410 x축:** `weekly_grid_manifest.json`. 세 패치 꺾임으로 주당 픽셀 간격을 찾고, 아즈모스 첫 점으로 나머지 생산처의 격자 위상을 고정했다.
- **주간 직선성 검증:** `250410_weekly_segment_straightness.csv`. 두 목요일 점 사이 원본 선의 모든 x를 직선과 비교한다. 일부 보스·필드 구간은 검사를 **통과하지 못한다**. `250410_original_interior_kink_example.png`가 원본 반례다.
- **급변 주 오차:** `weekly_250410_phase_sensitive.csv`. x를 ±3픽셀 옮겼을 때 y가 10픽셀 넘게 변하는 주를 표시한다.
- **보스 막대:** `boss_bars_all.csv`. 선 판독과 별개로 막대 하나당 한 행이다.
- **영상 탐색용:** `raster_trace_nonweekly.csv`와 `*_qa.png`는 선 색을 따라간 **픽셀 탐색 자료**다. 행 수를 주간 관측 수로 읽거나 경제 분석에 직접 쓰지 않는다.

선 그래프의 y는 원본 이미지의 화면 좌표다. `0` 기준·화폐 단위가 확인되지 않은 선을 합산하지 않는다.
