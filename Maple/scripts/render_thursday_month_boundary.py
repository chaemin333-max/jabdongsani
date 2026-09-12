from pathlib import Path
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
R=Path(__file__).resolve().parents[1];D=R/'data/thursday_month_boundary_audit_20260913'
for p in (R/'assets/fonts').glob('NotoSansKR*.ttf'):font_manager.fontManager.addfont(str(p))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False})
b=pd.read_csv(D/'bar_source_change_comparison.csv');f=pd.read_csv(D/'fixed_model_post_subset.csv')
b['source']=b.source.astype(str)
fig,ax=plt.subplots(1,2,figsize=(13,5),layout='constrained')
p=b.pivot(index='source',columns='rule',values='weekly_change_corr').loc[['2504','2510','2609']]
x=np.arange(len(p));ax[0].bar(x-.18,p['all'],.36,label='전 주차');ax[0].bar(x+.18,p['exclude_week_containing_1_or_2'],.36,label='1·2일 포함 주 제외')
ax[0].set_xticks(x,p.index);ax[0].set_ylim(0,1.05);ax[0].set_ylabel('보스 막대–생산처 보스 주간 변화량 상관');ax[0].legend(fontsize=9)
q=f.pivot(index='method',columns='period',values='RMSE_fixed_model_pixels').loc[['source_sum','ratio_free_origin']]
labels=['생산처 합계','보스비율 역산'];x=np.arange(len(q))
ax[1].bar(x-.18,q['all_post'],.36,label='도입 후 전체');ax[1].bar(x+.18,q['post_excluding_month_1_2_weeks'],.36,label='1·2일 포함 주 제외')
ax[1].set_xticks(x,labels);ax[1].set_ylabel('2510 총생산 원본 대비 RMSE, 픽셀');ax[1].legend(fontsize=9)
for a in ax:a.grid(axis='y',alpha=.2);a.set_axisbelow(True)
fig.suptitle('월초 주차 제거: 보스선의 요동은 줄지만 총생산 연결 차이는 남음')
fig.savefig(R/'figures/thursday_month_boundary_audit.png',dpi=170)
