"""Check published weight identities, missingness, and aggregation contracts."""
import unittest
import numpy as np
import pandas as pd
from pathlib import Path

D=Path(__file__).resolve().parents[1]/'data/boss_productivity_weights_20260912'

class WeightsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all=pd.read_csv(D/'weekly_weights.csv')
        cls.valid=cls.all[cls.all.weight_status=='valid']

    def test_definition_and_allocation(self):
        x=self.valid
        np.testing.assert_allclose(x.w,(x.C_boss/x.C_accounts)/(x.M_boss/x.A_accounts))
        np.testing.assert_allclose(x.w*x.C_accounts/x.E_main_equivalent_accounts,x.C_boss/x.B_total)
        np.testing.assert_allclose(x.B_total/x.E_main_equivalent_accounts,x.bM_per_account)

    def test_index_baseline(self):
        x=self.all[self.all.date.str.startswith('2025-09')]
        self.assertAlmostEqual(x.main_productivity_index.mean(),100)

    def test_missing_is_not_zero(self):
        x=self.all
        outside=x[x.weight_status=='outside_season']
        self.assertTrue((outside.w==0).all())
        self.assertTrue(outside.bC_per_account.isna().all())
        missing=x[~x.weight_status.isin(['valid','outside_season'])]
        self.assertGreater(len(missing),0)
        self.assertTrue(missing.w.isna().all())
        self.assertTrue(missing.E_main_equivalent_accounts.isna().all())

    def test_scenarios(self):
        x=self.valid
        self.assertTrue((x.w>=x.w_scenario_min-1e-9).all())
        self.assertTrue((x.w<=x.w_scenario_max+1e-9).all())

    def test_season_aggregation(self):
        for r in pd.read_csv(D/'season_summary.csv').itertuples():
            x=self.valid[self.valid.season==r.season]
            self.assertAlmostEqual(r.C_weighted_w,(x.w*x.C_accounts).sum()/x.C_accounts.sum())

    def test_cutoff_and_windows(self):
        self.assertEqual(self.all.date.max(),'2026-08-20')
        p=pd.read_csv(D/'patch_window_comparison.csv')
        self.assertEqual(p.iloc[-1].post_calendar,1)
        self.assertEqual(p.iloc[-1].coverage,'partial_or_boundary')
        self.assertTrue(p.loc[p.C_pre_n==0,'C_change_pct'].isna().all())

if __name__=='__main__':unittest.main()
