import unittest
from pathlib import Path
import pandas as pd
import numpy as np
D=Path(__file__).resolve().parents[1]/'data/main_total_components_20260912'
class ComponentsTests(unittest.TestCase):
    def test_conservation_and_nonnegative(self):
        s=pd.read_csv(D/'residual_allocation_scenarios.csv').dropna(subset=['main_total'])
        np.testing.assert_allclose(s.main_total+s.challenger_total,s.P_total)
        self.assertTrue((s.challenger_total>=-1e-10).all())
        self.assertTrue((s.main_total>=s.M_boss-1e-10).all())
    def test_monotonic_raw_levels(self):
        s=pd.read_csv(D/'residual_allocation_scenarios.csv')
        p=s.pivot(index='date',columns='residual_C_to_M_productivity_assumed',values='q_main').dropna()
        self.assertTrue((np.diff(p.to_numpy(),axis=1)<=1e-12).all())
    def test_baseline_and_cutoff(self):
        s=pd.read_csv(D/'residual_allocation_scenarios.csv')
        self.assertEqual(s.date.max(),'2026-08-20')
        for _,g in s.groupby('residual_C_to_M_productivity_assumed'):
            self.assertAlmostEqual(g[g.date.str.startswith('2025-09')].q_main_sep2025_100.mean(),100)
    def test_missing_and_scope_rejections(self):
        s=pd.read_csv(D/'residual_allocation_scenarios.csv')
        self.assertTrue(s.loc[~s.weight_status.isin(['valid','outside_season']),'q_main'].isna().all())
        a=pd.read_csv(D/'source_scope_audit.csv')
        self.assertEqual((~a.three_component_feasible).sum(),16)
        t=pd.read_csv(D/'three_component_scenarios.csv')
        self.assertTrue(t.loc[~t.three_component_feasible,'q_main_three_component'].isna().all())
    def test_bounds(self):
        d=pd.read_csv(D/'weekly_components.csv')
        s=pd.read_csv(D/'residual_allocation_scenarios.csv').merge(d[['date','q_main_lower_fixed_boss','q_main_upper_fixed_boss']],on='date').dropna(subset=['q_main'])
        self.assertTrue((s.q_main>=s.q_main_lower_fixed_boss-1e-12).all())
        self.assertTrue((s.q_main<=s.q_main_upper_fixed_boss+1e-12).all())
if __name__=='__main__':unittest.main()
