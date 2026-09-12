# 판독 파일 사용 순서

- **250410 공통 주간 x:** `250410_joint_weekly_axis.csv`. 아즈모스 첫 x=1087을 출시일에 고정하고 여러 생산처의 굴절을 합쳐 주마다 하나의 x를 복원했다. `dx_from_previous_week`는 6~10픽셀이다.
- **250410 주간 생산처 점:** `250410_joint_weekly_points.csv`. 모든 생산처가 같은 날짜에 같은 x를 쓴다. 굵은 점 때문에 y는 중심 추정값과 가능한 픽셀 범위를 함께 제공한다.
- **다른 방송의 주간 선:** `weekly_line_pixels_all.csv`. 그 파일의 **250410 부분은 과거의 등간격 초안**이며 분석 입력으로는 위 공통 점 파일을 사용한다.
- **주간 점 위치 확인:** `250410_joint_weekly_vertices_qa.png`. 연한 하늘색 아즈모스는 자홍색으로 매주 한 점만 표시했다.
- **아즈모스 원본 추적:** `azmoth_light_cyan_raster.csv`, `azmoth_light_cyan_trace_crop.png`. 첫 색 픽셀 x=1087을 2024-10-17에 고정했다.
- **굴절과 간격:** `250410_all_detected_bends.csv`에 원시 굴절 후보·각도·`dx`, `250410_merged_weekly_bends.csv`에 굵은 점의 양 가장자리를 합친 주간 굴절·`dx`가 있다. `250410_shared_week_bends_qa.png`는 굴절과 공통 x 수직선을 표시한다.
- **점 크기를 고려한 직선성:** `250410_point_aware_segment_test.csv`. 두꺼운 접합부를 선분 검증에서 분리한 결과, 관측 가능한 구간 모두 영상 선폭 범위 안에서 직선 연결에 부합한다. `250410_naive_segment_straightness.csv`는 접합부를 고려하지 않아 거짓 양성을 낸 **이전 검사**다.
- **독립 대조:** `250410_leave_one_source_out_segments.csv`는 생산처 한 선을 x맞춤에서 빼고 검증한다. 여섯 구간은 6픽셀 허용범위 밖이라 재검토 상태다.
- **중간 진단:** `250410_nonuniform_segment_diagnostic.csv` 역시 y방향 점 크기를 적용하기 전의 수치다. 최종 직선성 판정은 위 점 크기 검사만 따른다.
- **급변 주 오차:** `weekly_250410_phase_sensitive.csv`. x를 ±3픽셀 옮겼을 때 y가 10픽셀 넘게 변하는 주를 표시한다.
- **보스 막대:** `boss_bars_all.csv`. 선 판독과 별개로 막대 하나당 한 행이다.
- **영상 탐색용:** `raster_trace_nonweekly.csv`와 `*_qa.png`는 선 색을 따라간 **픽셀 탐색 자료**다. 행 수를 주간 관측 수로 읽거나 경제 분석에 직접 쓰지 않는다.

선 그래프의 y는 원본 이미지의 화면 좌표다. `0` 기준·화폐 단위가 확인되지 않은 선을 합산하지 않는다.
