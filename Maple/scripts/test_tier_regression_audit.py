import csv,json,unittest
from pathlib import Path
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_hac
from audit_tier_regression import hac_cov,random_meta
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Maple/data/tier_regression_audit'
def read(name):
    with (D/name).open(encoding='utf-8') as f:return list(csv.DictReader(f))
class AuditTests(unittest.TestCase):
    def test_hac_matches_reference_on_contiguous_data(self):
        rng=np.random.default_rng(43);X=np.column_stack([np.ones(80),rng.normal(size=(80,2))]);y=X@np.array([1,2,3])+rng.normal(size=80)
        fit=sm.OLS(y,X).fit();np.testing.assert_allclose(hac_cov(X,fit.resid,np.arange(80),4),cov_hac(fit,nlags=4,use_correction=True),rtol=1e-9,atol=1e-10)
    def test_gap_aware_covariance(self):
        X=np.column_stack([np.ones(6),np.arange(6)]);e=np.array([1,-1,.5,-.5,2,-2])
        cov=hac_cov(X,e,np.arange(6)*10,4)
        bread=np.linalg.inv(X.T@X);scores=X*e[:,None]
        np.testing.assert_allclose(cov,bread@(scores.T@scores)@bread*6/4)
    def test_meta_null(self):
        m=random_meta(np.zeros(4),np.ones(4)*.01);self.assertAlmostEqual(m['pooled_pct'],0);self.assertLess(m['ci_lower_pct'],0);self.assertGreater(m['ci_upper_pct'],0)
    def test_meta_is_four_events_not_scenarios(self):
        m=json.loads((D/'episode_meta_summary.json').read_text());self.assertEqual(m['k'],4);self.assertEqual(len(read('opening_episode_effects.csv')),4)
    def test_four_cluster_sign_enumeration(self):
        for r in read('opening_wild_cluster_sensitivity.csv'):
            self.assertEqual(int(r['sign_patterns']),16);self.assertEqual(int(r['clusters']),4)
            self.assertGreaterEqual(float(r['restricted_wild_sign_p']),2/16-1e-8)
    def test_official_holdout_disjoint(self):
        rr=read('cross_broadcast_holdout.csv');cal=[x['date'] for x in rr if x['role']=='scale_calibration'];test=[x['date'] for x in rr if x['role']=='held_out_cross_broadcast'];self.assertEqual(len(cal),16);self.assertEqual(len(test),43);self.assertLess(max(cal),min(test))
    def test_old_assembly_annotation_not_misread_as_bar(self):
        row=next(x for x in read('official_20251016_pixels.csv') if x['date']=='2025-06-19');self.assertGreater(float(row['height_pixels']),250)
    def test_printed_distribution_and_constraint_classification(self):
        rr=read('official_20251016_solo_distribution.csv')
        for d in ['2025-06-12','2025-10-02']:self.assertAlmostEqual(sum(float(x['share_pct']) for x in rr if x['date']==d),100)
        self.assertTrue(all(x['evidence_class']=='constraint_reproduction_not_independent_validation' for x in read('official_constraint_audit.csv')))
if __name__=='__main__':unittest.main()
