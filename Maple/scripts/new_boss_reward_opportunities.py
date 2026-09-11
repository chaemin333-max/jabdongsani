"""Fixed-price, fixed-access boss baskets: isolate menu expansion from power.

Reference prices are the 2026-08-20 schedule, not September proposed prices.
Profiles are explicit counterfactual access sets, not estimated populations.
"""
import csv,json,re,hashlib
from datetime import date,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Maple/data/new_boss_reward_opportunities'

def read(p):
    with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(name,rows):
    with (D/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
def norm(s):return ''.join(s.split())

RELEASES={
 '발드릭스':('2025-02-20','https://maplestory.nexon.com/news/update/766'),
 '최초의대적자':('2025-08-21','https://maplestory.nexon.com/news/update/779'),
 '찬란한흉성':('2026-01-15','https://maplestory.nexon.com/news/update/795'),
 '유피테르':('2026-02-12','https://maplestory.nexon.com/news/update/797'),
 '벨로나':('2026-08-20','https://maplestory.nexon.com/news/update/811')}

LOW=['자쿰(카오스)','매그너스(하드)','벨룸(카오스)','피에르(카오스)','반반(카오스)','블러디퀸(카오스)',
     '파풀라투스(카오스)','스우(하드)','데미안(하드)','가디언엔젤슬라임(카오스)','루시드(하드)',
     '윌(하드)','더스크(카오스)','진힐라(하드)','듄켈(하드)']
MID=LOW+['선택받은세렌(하드)','감시자칼로스(이지)']
EXT=MID+['카링(이지)','감시자칼로스(노멀)','스우(익스트림)']
PROFILES={
 'challenger_seren':MID+['최초의대적자(이지)'],
 'challenger_extreme_suu':EXT+['최초의대적자(이지)'],
 'main_extreme_suu':EXT+['최초의대적자(노멀)','벨로나(이지)'],
 'main_normal_limbo':EXT+['카링(노멀)','림보(노멀)','최초의대적자(노멀)','찬란한흉성(노멀)','벨로나(노멀)'],
 'main_upper':EXT+['카링(익스트림)','감시자칼로스(익스트림)','림보(하드)','선택받은세렌(익스트림)',
                   '발드릭스(하드)','최초의대적자(익스트림)','찬란한흉성(하드)','유피테르(하드)','벨로나(노멀)']}

def basket(catalog,profile,day,exclude=(),limit=12):
    # One weekly difficulty per boss family. Then select top payouts.
    best={}
    for name in PROFILES[profile]:
        r=catalog[name];family=r['family']
        if family in exclude or r['release_week']>day:continue
        if family not in best or r['meso']>best[family]['meso']:best[family]=r
    return sorted(best.values(),key=lambda r:r['meso'],reverse=True)[:limit]

def run():
    D.mkdir(exist_ok=True,parents=True)
    prices={};evidence=[]
    # Parsed official before/after tables are archived next to this script's outputs.
    for code in [768,786,806]:
        for r in read(D/f'official_prices_{code}.csv'):
            try:before,after=int(r['1']),int(r['2'])
            except ValueError:continue
            name=norm(r['0']);prices[name]=(after,f'https://maplestory.nexon.com/news/update/{code}')
            evidence.append(dict(boss=r['0'],before_meso=before,after_meso=after,source_url=f'https://maplestory.nexon.com/news/update/{code}'))
    for r in read(D/'official_prices_test199.csv'):
        if '벨로나' in r['0']:
            # ONLY the 'before' column confirms the August price. Do not use the future nerf.
            prices[norm(r['0'])]=(int(r['1']),'https://maplestory.nexon.com/testworld/news/all/199')
    catalog={}
    for name in sorted(set(sum(PROFILES.values(),[]))):
        if name not in prices:raise ValueError(f'Missing verified price {name}')
        family=name.split('(')[0];release,url=RELEASES.get(family,('2000-01-01','existing_catalog'))
        price,source=prices[name]
        catalog[name]=dict(boss=name,family=family,meso=price,release_week=release,release_source=url,price_source=source,
                           eligible_challenger=name=='최초의대적자(이지)' if family in RELEASES else True)
    write('verified_boss_catalog.csv',list(catalog.values()));write('official_price_evidence.csv',evidence)
    weeks=[r['date'] for r in read(ROOT/'Maple/data/now_20260910/boss_tier_weekly.csv')]
    weekly=[];selections=[];events=[]
    for profile in PROFILES:
        baseline=basket(catalog,profile,'2026-08-20',exclude=RELEASES)
        base=sum(r['meso'] for r in baseline)
        for ds in weeks:
            selected=basket(catalog,profile,ds);total=sum(r['meso'] for r in selected)
            weekly.append(dict(date=ds,profile=profile,reference_price_date='2026-08-20',weekly_cap=12,
                               without_new_bosses_meso=base,with_available_new_bosses_meso=total,
                               opportunity_factor=total/base,increase_pct=100*(total/base-1),
                               interpretation='fixed-access solo basket; not mean realized production'))
            for rank,r in enumerate(selected,1):selections.append(dict(date=ds,profile=profile,rank=rank,boss=r['boss'],meso=r['meso']))
        for family,(ds,url) in RELEASES.items():
            before=basket(catalog,profile,(date.fromisoformat(ds)-timedelta(days=1)).isoformat());after=basket(catalog,profile,ds)
            added=[r for r in after if r['boss'] not in {x['boss'] for x in before}]
            removed=[r for r in before if r['boss'] not in {x['boss'] for x in after}]
            gain=sum(x['meso'] for x in after)-sum(x['meso'] for x in before)
            if gain:
                events.append(dict(profile=profile,new_family=family,release_week=ds,added_bosses=';'.join(r['boss'] for r in added),
                                   displaced_bosses=';'.join(r['boss'] for r in removed),gross_added=sum(r['meso'] for r in added),
                                   displaced_income=sum(r['meso'] for r in removed),net_weekly_gain=gain,
                                   before_weekly_income=sum(r['meso'] for r in before),after_weekly_income=sum(r['meso'] for r in after),
                                   gain_pct=100*gain/sum(r['meso'] for r in before)))
    write('weekly_opportunity_factors.csv',weekly);write('weekly_basket_selections.csv',selections);write('new_boss_net_gains.csv',events)
    accounts=[]
    for profile in PROFILES:
        old=basket(catalog,profile,'2026-08-20',exclude=RELEASES);new=basket(catalog,profile,'2026-08-20')
        for count in [1,3,6,8]:
            a=sum(sorted([x['meso'] for x in old]*count,reverse=True)[:90]);b=sum(sorted([x['meso'] for x in new]*count,reverse=True)[:90])
            accounts.append(dict(profile=profile,characters=count,per_character_cap=12,world_account_cap=90,
                                 baseline_weekly_meso=a,expanded_weekly_meso=b,net_gain=b-a,gain_pct=100*(b/a-1)))
    write('account_cap_examples.csv',accounts)
    manifest=dict(price_reference='2026-08-20',future_test_prices_applied=False,weekly_limit=12,monthly_black_mage_excluded=True,
                  challenger_new_boss_exception='Easy First Adversary only',other_new_bosses='main-only assumption',
                  season_bosses='Kai/Meirin remain tier3; not double-added in this ordinary-crystal basket',
                  limitations=['fixed access sets are scenarios, not combat-stat thresholds inferred from players',
                               'solo rewards; actual party sizes and take-up are unknown',
                               'Hard Bellona price not verified in the selected official tables, so excluded from this basket calculation'],
                  release_catalog=RELEASES)
    (D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    for r in weekly:
        if r['date']=='2026-08-20':print(r)

if __name__=='__main__':run()
