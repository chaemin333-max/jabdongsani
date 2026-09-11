import csv,hashlib,json,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Maple/data/now_20260910';S=ROOT/'Maple/assets/sources/20260910'
def read(name):
    with (D/name).open(encoding='utf-8') as f:return list(csv.DictReader(f))
class DigitizationTests(unittest.TestCase):
    def test_source_bytes(self):
        m=json.loads((D/'digitization_manifest.json').read_text(encoding='utf-8'))
        for name,meta in m['source_images'].items():self.assertEqual(hashlib.sha256((S/name).read_bytes()).hexdigest(),meta['sha256'])
    def test_calendar_and_components(self):
        r=read('boss_tier_weekly.csv');self.assertEqual(len(r),105);self.assertEqual(r[52]['date'],'2025-08-21');self.assertEqual(r[-1]['date'],'2026-08-20')
        for row in r:
            self.assertAlmostEqual(sum(float(row[f'tier{j}']) for j in range(1,8)),float(row['B_digitized_constrained']),places=8)
            self.assertTrue(all(float(row[f'tier{j}'])>=0 for j in range(1,8)))
    def test_official_production_ratios(self):
        rows={r['date']:r for r in read('boss_tier_weekly.csv')}
        for j,ratio in enumerate([.4,.98,4.03,8.24,10.73,16.83],1):
            self.assertAlmostEqual(float(rows['2026-08-20'][f'tier{j}'])/float(rows['2025-08-21'][f'tier{j}']),ratio,places=9)
    def test_distribution_and_count_ratios(self):
        r=read('solo_clear_distribution.csv')
        for key in ['constrained_share_reference','constrained_share_comparison']:self.assertAlmostEqual(sum(float(x[key]) for x in r),1.,places=9)
        for x in r:
            self.assertAlmostEqual(float(x['constrained_share_comparison'])*float(x['implied_population_growth_multiplier'])/float(x['constrained_share_reference']),float(x['official_multiplier']),places=8)
    def test_source_trace_no_boss_field_alias(self):
        for r in read('production_by_source_weekly.csv'):
            if r['series']=='field' and r['line_y_pixel']:self.assertGreaterEqual(float(r['line_y_pixel']),640)
            if r['series']=='other':self.assertEqual(r['production_index'],'')
    def test_no_leap_cutoff(self):
        for r in read('preleap_tier_excess.csv'):self.assertLess(r['date'],r['first_leap'])
        r=read('season_identification_windows.csv');self.assertEqual([int(x['no_leap_days']) for x in r],[28,28,28,35])
if __name__=='__main__':unittest.main()
