from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
R=Path(__file__).resolve().parents[1];D=R/'data/four_total_bridges_20260913'
for p in (R/'assets/fonts').glob('NotoSansKR*.ttf'):font_manager.fontManager.addfont(str(p))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False})
d=pd.read_csv(D/'total_ratio_formula_weekly.csv',parse_dates=['date'])
fig,ax=plt.subplots(2,1,figsize=(13,8),sharex=True,layout='constrained')
ax[0].plot(d.date,-d.october_total_y,label='2510 총생산 원본 높이',color='#222222',lw=2.5)
ax[0].plot(d.date,d.source_sum_only_predicted_negative_y,label='2504 생산처 합계',lw=2)
ax[0].plot(d.date,d.ratio_with_bar_free_origin_predicted_negative_y,label='2504 보스막대÷보스비중',lw=2)
ax[0].axvline(pd.Timestamp('2024-10-17'),color='#ad3636',ls='--',label='아즈모스 도입')
ax[0].set_ylabel('2510 총생산 그림의 임의 픽셀좌표');ax[0].legend(fontsize=9)
for col,label in [('source_sum_only_predicted_negative_y','생산처 합계'),('ratio_with_bar_free_origin_predicted_negative_y','보스 비율 역산')]:
    ax[1].plot(d.date,d[col]+d.october_total_y,label=label)
ax[1].axhline(0,color='#333333',lw=1);ax[1].axvline(pd.Timestamp('2024-10-17'),color='#ad3636',ls='--')
ax[1].set_ylabel('2510 원본 대비 픽셀 차이');ax[1].legend(fontsize=9)
for a in ax:a.grid(alpha=.2)
fig.suptitle('네 원본의 총생산 연결부 진단 · 원본 0선은 고정하지 않음')
fig.savefig(R/'figures/four_total_bridge_audit.png',dpi=170)
