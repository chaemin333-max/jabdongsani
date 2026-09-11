"""Visual QA of digitization; independent from the canonical total/per-capita chart."""
import csv,json
from pathlib import Path
from datetime import date
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'Maple/data/now_20260910'
def read(name):
    with (DATA/name).open(encoding='utf-8') as f:return list(csv.DictReader(f))
font=ROOT/'Maple/assets/fonts/NotoSansKR-Regular.ttf';font_manager.fontManager.addfont(str(font))
plt.rcParams['font.family']=font_manager.FontProperties(fname=str(font)).get_name()
plt.rcParams['axes.unicode_minus']=False
palette=['#6073fe','#ff5f35','#02b592','#af71fd','#ffa54f','#05c3f8','#ff7694']
labels=['하드 스우 미만','하드 스우~하드 진 힐라','노멀 세렌~하드 세렌','이지 카링~익스트림 스우','노멀 흉성~노멀 림보','익스트림 세렌~하드 림보','하드 벨로나 이상']
r=read('boss_tier_weekly.csv');ds=[date.fromisoformat(x['date']) for x in r]
fig,axes=plt.subplots(3,1,figsize=(15,15),dpi=160)
fig.subplots_adjust(left=.075,right=.76,top=.92,bottom=.07,hspace=.48)
fig.suptitle('2026.09.10 MAPLE NOW · 첨부 자료 수치 복원',fontsize=23,y=.97)
ax=axes[0];bottom=np.zeros(len(r))
for j in range(7):
    v=np.array([float(x[f'tier{j+1}']) for x in r]);ax.bar(ds,v,bottom=bottom,width=5.2,color=palette[j],label=labels[j]);bottom+=v
ax.set_title('주간 보스 구간별 생산량 · 105주 / 공식 증감률 반영');ax.set_ylabel('기존 정본에 맞춘 상대 스케일')
ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),fontsize=9)
for dt,text in [('2025-08-21','ASSEMBLE 3'),('2026-06-18','OVERDRIVE 1'),('2026-07-23','2'),('2026-08-20','3')]:
    ax.axvline(date.fromisoformat(dt),color='#aaa',ls='--',lw=.7)
ax=axes[1];r=read('production_by_source_weekly.csv')
for code,label,color in [('boss_rewards','보스 리워드','#d26253'),('field','필드','#efaaa8'),('serazar_coin','세라자르 주화','#163e60'),('coin_exchange','주화 거래소 판매','#abd8e9')]:
    rr=[x for x in r if x['series']==code];ax.plot([date.fromisoformat(x['date']) for x in rr],[float(x['production_index']) if x['production_index'] else np.nan for x in rr],color=color,label=label,lw=1.8)
ax.set_title('생산처별 메소 생산량 · 53주');ax.set_ylabel('기존 정본에 맞춘 상대 스케일');ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),fontsize=10)
ax.text(1.015,.43,'겹쳐 읽히지 않는 점은 빈칸 유지\n기타: 0축 부근에서 분리 불가',transform=ax.transAxes,fontsize=9,color='#666')
ax=axes[2];r=read('solo_clear_distribution.csv');bottom=np.zeros(2)
for j,x in enumerate(r):
    v=np.array([float(x['constrained_share_reference']),float(x['constrained_share_comparison'])])*100
    ax.bar([0,1],v,bottom=bottom,color=palette[j],width=.5,label=labels[j] if j<5 else '익스트림 세렌 이상');bottom+=v
ax.set_ylim(0,100);ax.set_xlim(-.7,1.7);ax.set_xticks([0,1],['CROWN 3차\n2026-02-12','OVERDRIVE 3차\n2026-08-20']);ax.set_ylabel('비중 (%)')
ax.set_title('보스 솔로 클리어 난이도 분포 · 원본 막대와 공식 증감률 결합');ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),fontsize=9)
for ax in axes:
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
for ax in axes[:2]:ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3));ax.xaxis.set_major_formatter(mdates.DateFormatter('%y.%m'))
fig.text(.075,.025,'원본 이미지 3개는 별도 보존. 막대 픽셀 측정값과 공식 수치로 보정한 값은 CSV에서 구분합니다.',fontsize=11,color='#536574')
path=ROOT/'Maple/figures/now_20260910_reconstruction.png';fig.savefig(path);print(path)

# Direct pixel-coordinate overlay is an audit diagram, not an edited replacement image.
from PIL import Image
raw=read('boss_tier_pixels.csv');fig,ax=plt.subplots(figsize=(14,7),dpi=160)
im=Image.open(ROOT/'Maple/assets/sources/20260910/boss_production_by_tier.png');ax.imshow(im)
for ds in sorted(set(x['date'] for x in raw))[::4]:
    rr=[x for x in raw if x['date']==ds];x=float(rr[0]['x_pixel']);yy=float(rr[0]['stack_bottom_y'])+.5
    for row in rr:
        yy-=float(row['height_pixels']);ax.plot([x-2,x+2],[yy,yy],color='black',lw=.55)
ax.set_xlim(125,825);ax.set_ylim(680,335);ax.set_title('픽셀 복원 검증: 검은 선 = 측정한 구간 경계');ax.set_xlabel('원본 x pixel');ax.set_ylabel('원본 y pixel')
fig.tight_layout();fig.savefig(ROOT/'Maple/figures/now_20260910_pixel_audit.png')
