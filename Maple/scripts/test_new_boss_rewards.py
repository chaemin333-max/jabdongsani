import csv,json,unittest
from pathlib import Path
from new_boss_reward_opportunities import basket,PROFILES,RELEASES
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Maple/data/new_boss_reward_opportunities'
def read(p):
    with p.open(encoding='utf-8') as f:return list(csv.DictReader(f))
class MenuTests(unittest.TestCase):
    def setUp(self):
        self.catalog={r['boss']:{**r,'meso':int(r['meso'])} for r in read(D/'verified_boss_catalog.csv')}
    def test_early_date_and_family_exclusivity(self):
        for p in PROFILES:
            rows=basket(self.catalog,p,'2025-01-01');self.assertTrue(all(r['family'] not in RELEASES for r in rows))
            rows=basket(self.catalog,p,'2026-08-20');self.assertLessEqual(len(rows),12);self.assertEqual(len(rows),len({r['family'] for r in rows}))
    def test_challenger_exception(self):
        for p in ['challenger_seren','challenger_extreme_suu']:
            new=[r for r in basket(self.catalog,p,'2026-08-20') if r['family'] in RELEASES]
            self.assertEqual([r['boss'] for r in new],['최초의대적자(이지)'])
    def test_exact_replacement_arithmetic(self):
        for r in read(D/'new_boss_net_gains.csv'):
            self.assertEqual(int(r['gross_added'])-int(r['displaced_income']),int(r['net_weekly_gain']))
            self.assertEqual(int(r['after_weekly_income'])-int(r['before_weekly_income']),int(r['net_weekly_gain']))
    def test_no_future_price_nerf(self):
        self.assertEqual(self.catalog['최초의대적자(이지)']['meso'],308000000)
        self.assertEqual(self.catalog['벨로나(이지)']['meso'],440000000)
    def test_account_limit(self):
        for r in read(D/'account_cap_examples.csv'):
            if r['characters']=='8':
                p=r['profile'];full=sum(x['meso'] for x in basket(self.catalog,p,'2026-08-20'))*8
                self.assertLess(int(r['expanded_weekly_meso']),full)
    def test_applied_model_conserves_observations(self):
        p=ROOT/'Maple/data/tier_boss_decomposition_reward_adjusted'
        for r in read(p/'scenario_weekly.csv'):
            self.assertAlmostEqual(float(r['C_boss'])+float(r['M_boss']),float(r['B_total']),places=7)
            for j in range(int(r['cap_tier'])+1,8):self.assertEqual(float(r[f'C_tier{j}']),0)
        diagnostics=read(p/'fit_diagnostics.csv');self.assertEqual(len(diagnostics),52);self.assertTrue(all(r['success']=='True' for r in diagnostics))
if __name__=='__main__':unittest.main()
