from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
R=Path(__file__).resolve().parents[1];D=R/'data/four_boss_window_alignment'
for p in (R/'assets/fonts').glob('NotoSansKR*.ttf'):font_manager.fontManager.addfont(str(p))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False})
fig,ax=plt.subplots(figsize=(14,6),layout='constrained')
for label,path,color in [('2504','2504_pixels.csv','#d55e00'),('2510','2510_low_high.csv','#0072b2'),('2609','2609_low_high.csv','#009e73')]:
    d=pd.read_csv(D/path,parse_dates=['date'])
    ax.plot(d.date,100*d.low_share,label=label,color=color,linewidth=2,alpha=.9)
ax.set_ylim(0,100);ax.set_xlim(pd.Timestamp('2023-03-01'),pd.Timestamp('2026-08-20'))
ax.set_ylabel('하드 스우 미만 / 해당 그림 주간 보스 구간 합계, %');ax.grid(alpha=.2);ax.legend()
ax.set_title('보스 구간별 생산비율 직접 대조 — 2311은 정확한 경계 미식별')
fig.savefig(R/'figures/four_boss_window_alignment.png',dpi=170)
