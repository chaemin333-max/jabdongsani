import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Maple/data/tier_boss_decomposition_v1'
def read(path):
    with path.open(encoding='utf-8') as f:return list(csv.DictReader(f))
class TierDecompositionTests(unittest.TestCase):
    def test_all_fits_converge(self):
        rr=read(D/'fit_diagnostics.csv');self.assertEqual(len(rr),44)
        for r in rr:
            self.assertEqual(r['success'],'True');self.assertLess(float(r['equality_max_error']),1e-6);self.assertLess(float(r['inequality_max_error']),1e-6)
    def test_boss_mapping_no_extra_mass(self):
        m=json.loads((D/'run_manifest.json').read_text());self.assertEqual(m['season_boss_assignment'],{'Kai':3,'Meirin':3});self.assertTrue(m['no_added_season_boss_mass'])
    def test_tier_conservation_support_and_bounds(self):
        for r in read(D/'scenario_weekly.csv'):
            total=0
            for j in range(1,8):
                c=float(r[f'C_tier{j}']);m=float(r[f'M_tier{j}']);self.assertGreaterEqual(c,-1e-7);self.assertGreaterEqual(m,-1e-7);total+=c+m
                if j>int(r['cap_tier']):self.assertAlmostEqual(c,0.,places=9)
            self.assertAlmostEqual(total,float(r['B_total']),places=7)
            self.assertGreaterEqual(float(r['C_share'])+1e-7,float(r['assumption_only_share_lower']))
            self.assertLessEqual(float(r['C_share'])-1e-7,float(r['assumption_only_share_upper']))
            if r['stage']=='pre_leap':self.assertAlmostEqual(float(r['transferred_production_in_main']),0.,places=8)
    def test_exact_preleap_anchor(self):
        anchors={r['date']:float(r['challenger_low2_increment']) for r in read(ROOT/'Maple/data/now_20260910/preleap_tier_excess.csv')}
        rows=[r for r in read(D/'weekly_decomposition.csv') if r['stage']=='pre_leap'];self.assertEqual(len(rows),17)
        for r in rows:self.assertAlmostEqual(float(r['C_tier1'])+float(r['C_tier2']),anchors[r['date']],places=6)
    def test_cutoff_and_missing_means(self):
        rr=read(D/'weekly_decomposition.csv');self.assertEqual(len(rr),105);self.assertEqual(rr[-1]['date'],'2026-08-20')
        for r in rr:
            if not r['C_accounts']:self.assertEqual(r['C_mean_per_100k'],'')
    def test_source_tiers_remain_unchanged(self):
        raw={r['date']:r for r in read(ROOT/'Maple/data/now_20260910/boss_tier_weekly.csv')}
        for r in read(D/'scenario_weekly.csv'):
            for j in range(1,8):self.assertAlmostEqual(float(r[f'M_tier{j}'])+float(r[f'C_tier{j}']),float(raw[r['date']][f'tier{j}']),places=7)
if __name__=='__main__':unittest.main()
