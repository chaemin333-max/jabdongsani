from pathlib import Path
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
R=Path(__file__).resolve().parents[1];D=R/'data/total_ratio_exact_thursday_20260913'
for f in (R/'assets/fonts').glob('NotoSansKR*.ttf'):font_manager.fontManager.addfont(str(f))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False})
d=pd.read_csv(D/'named_thursday_pixel_deltas.csv').iloc[:4]
x=np.arange(len(d));fig,ax=plt.subplots(figsize=(12,5),layout='constrained')
scale=.30952
ax.bar(x-.3,d.apr_source_sum_change_px*scale,.2,label='2504 생산처 전체 × 보정 배율')
ax.bar(x-.1,d.apr_source_sum_without_az_change_px*scale,.2,label='2504 아즈모스 제외 × 보정 배율')
ax.bar(x+.1,d.oct_total_up_px,.2,label='2510 총생산 원본')
ax.axhline(0,color='#333',lw=1)
ax.set_xticks(x,[f'{r.start[5:]}→{r.end[5:]}' for r in d.itertuples()]);ax.set_ylabel('2510 총생산 그림에 맞춘 상승 픽셀')
ax.set_title('목요일 날짜 정정: 첫 차이는 10월 17일 아즈모스 신규 성분과 동시 발생')
ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.legend(fontsize=9)
fig.savefig(R/'figures/corrected_thursday_pixel_deltas.png',dpi=170)
