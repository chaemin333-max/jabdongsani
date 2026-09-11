"""Apply verified new-boss menu factors and preserve the prior decomposition."""
import csv
from pathlib import Path
import fit_tier_boss_decomposition as model

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Maple/data/tier_boss_decomposition_reward_adjusted'
if __name__=='__main__':
    model.run(reward_adjusted=True,output=OUT)
    old={r['date']:r for r in model.read(ROOT/'Maple/data/tier_boss_decomposition_v1/weekly_decomposition.csv')}
    new=model.read(OUT/'weekly_decomposition.csv');rows=[]
    for r in new:
        prev=old[r['date']]
        rows.append(dict(date=r['date'],season=r['season'],share_before=prev['C_share'],share_after=r['C_share'],
                         change_percentage_points=100*(float(r['C_share'])-float(prev['C_share'])) if r['C_share']!='' and prev['C_share']!='' else '',
                         M_mean_before=prev['M_mean_per_100k'],M_mean_after=r['M_mean_per_100k'],
                         C_mean_before=prev['C_mean_per_100k'],C_mean_after=r['C_mean_per_100k']))
    model.write(OUT/'before_after.csv',rows)
