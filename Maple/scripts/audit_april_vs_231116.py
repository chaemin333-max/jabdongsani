"""Compare April image with printed November 2023 shares, without scale fitting."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
R=Path(__file__).resolve().parents[1];O=R/'data/april_vs_231116';O.mkdir(exist_ok=True)
d=pd.read_csv(R/'data/now_20250410_overlay_v2/digitized_overlay.csv');t=pd.to_datetime(d.date).astype('datetime64[ns]').astype('int64')
boss=[64.8,64.6,60.5,52.3,55.7,58.6,60.9,61.7]
field=[27.2,27.,29.2,36.8,34.9,33.2,31.2,31.1]
ursus=[8.,8.3,10.3,10.8,9.4,8.1,7.9,7.2]
official=pd.DataFrame({'month':[f'2023-{m:02}' for m in range(4,12)],'boss_pct':boss,'field_pct':field,'ursus_pct':ursus})
official['printed_sum']=official[['boss_pct','field_pct','ursus_pct']].sum(axis=1)
official.to_csv(O/'official_printed_shares.csv',index=False)
out=[]
for row in official.itertuples():
    start=pd.Timestamp(row.month+'-01');end=start+pd.offsets.MonthEnd(0)
    # November is necessarily incomplete; report both end conventions, not a full-month claim.
    ends=[('full_month',end)] if start.month!=11 else [('through_Nov15',pd.Timestamp('2023-11-15')),('through_Nov16',pd.Timestamp('2023-11-16'))]
    for convention,last in ends:
        for shift in [-7,0,7]:
            ds=pd.date_range(start,last)+pd.Timedelta(hours=12,days=shift)
            h={}
            for name in ['boss','field','etc']:
                good=d[name+'_px'].notna();h[name]=np.interp(ds.as_unit('ns').astype('int64'),t[good],d.loc[good,name+'_px']).sum()
            total=sum(h.values());bf=h['boss']+h['field'];official_bf=row.boss_pct+row.field_pct
            out.append(dict(month=row.month,window=convention,date_shift=shift,days=len(ds),boss_image_pct=100*h['boss']/total,field_image_pct=100*h['field']/total,etc_image_pct=100*h['etc']/total,
                field_within_BF_official=100*row.field_pct/official_bf,field_within_BF_image=100*h['field']/bf,
                BF_difference_pp=100*h['field']/bf-100*row.field_pct/official_bf,
                field_image_vs_printed_pp=100*h['field']/total-row.field_pct,
                field_if_add_ursus_pct=(100-row.ursus_pct)*h['field']/total,
                corrected_field_difference_pp=(100-row.ursus_pct)*h['field']/total-row.field_pct,
                ursus_official_pct=row.ursus_pct))
a=pd.DataFrame(out);a.to_csv(O/'monthly_comparison.csv',index=False)
base=a[(a.date_shift==0)&(a.month!='2023-11')]
summary={'full_months':7,'mean_abs_BF_difference_pp':float(base.BF_difference_pp.abs().mean()),'mean_abs_field_direct_difference_pp':float(base.field_image_vs_printed_pp.abs().mean()),'mean_abs_field_ursus_adjusted_difference_pp':float(base.corrected_field_difference_pp.abs().mean()),'max_abs_BF_difference_pp':float(base.BF_difference_pp.abs().max()),'method':'daily integration of interpolated image heights; ratio of sums; no scale fitting; no adjustment to original curves','November':'partial window unknown; 1-15 and 1-16 alternatives; excluded from main summary','Ursus_adjustment':'conditional denominator diagnostic; not proof of exclusion','source_sha256':hashlib.sha256((R.parent/'231116 2.png').read_bytes()).hexdigest()}
(O/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
assert max(abs(official.printed_sum-100))<.11
assert len(base)==7
assert a.field_within_BF_image.between(0,100).all()
for f in (R/'assets/fonts').glob('NotoSansKR*.ttf'):font_manager.fontManager.addfont(str(f))
plt.rcParams.update({'font.family':'Noto Sans KR','axes.unicode_minus':False})
p=a[(a.date_shift==0)&(a.window!='through_Nov16')]
fig,ax=plt.subplots(figsize=(12,5),layout='constrained')
ax.plot(p.month,p.field_within_BF_official,'o-',label='231116 공식: 사냥/(보스+사냥)')
ax.plot(p.month,p.field_within_BF_image,'s--',label='250410 판독: 사냥/(보스+사냥)')
ax.set_ylabel('%');ax.set_title('우르스·기타를 양쪽 분모에서 제외한 구성비 대조');ax.grid(alpha=.2);ax.legend()
fig.supxlabel('11월은 1~15일 판독 가정 · 수치에 맞춘 배율 조정 없음')
fig.savefig(R/'figures/april_vs_231116.png',dpi=170)
print(json.dumps(summary));print(p[['month','field_within_BF_official','field_within_BF_image','BF_difference_pp','corrected_field_difference_pp']].to_string(index=False))
