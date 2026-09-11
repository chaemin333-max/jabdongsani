"""Focused checks of alignment, the joint observation model, and reported results."""
import hashlib
import unittest
import numpy as np
from fit_boss_decomposition import Model, Spec, SOURCE, OUT, ROOT, read_csv


class JointDecompositionTests(unittest.TestCase):
    def test_original_coordinate_integrity(self):
        raw=ROOT/'Maple/data/meso_total_production_raw_canonical.json'
        self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),
                         '63e41f7c7d5c384971524a56df0dcc01a25fd888f808e9174b3195feb9dd6b41')

    def test_cutoff_and_absent_boundary_counts(self):
        m=Model(Spec())
        self.assertEqual(str(m.d['dates'][-1]),'2026-08-20')
        for ds in ['2025-06-19','2025-12-18','2026-06-18']:
            i=[str(x) for x in m.d['dates']].index(ds)
            self.assertFalse(m.d['train'][i]);self.assertFalse(m.d['valid'][i])

    def test_future_population_not_used_at_endpoint(self):
        m=Model(Spec(lag=1))
        self.assertFalse(m.d['train'][-1]);self.assertFalse(m.d['valid'][-1])

    def test_canonical_progression_values_preserved(self):
        model=Model(Spec(progression=True)); known={r['date']:float(r['challenger_count']) for r in
            read_csv(SOURCE/'challenger_progression_canonical_s2_s3.csv') if r['challenger_count']}
        for i,d in enumerate(model.d['dates']):
            if str(d) in known:self.assertEqual(model.d['observed_H'][i],known[str(d)])

    def test_log_observation_gradient(self):
        m=Model(Spec(inflow=True,progression=True));theta=m.initial.copy()
        _,_,b,share=m.predict(theta);jac=(1-share[:,None])*m.M+share[:,None]*m.C
        for j in [0,m.cstart,m.cstart+16,len(theta)-1]:
            plus=theta.copy();minus=theta.copy();plus[j]+=1e-5;minus[j]-=1e-5
            numeric=(np.log(m.predict(plus)[2])-np.log(m.predict(minus)[2]))/2e-5
            np.testing.assert_allclose(numeric,jac[:,j],rtol=1e-6,atol=1e-9)

    def test_observationally_equivalent_split(self):
        m=Model(Spec());_,_,b,s=m.predict(m.initial)
        other=np.where(m.d['C']>0,.5*s+.2,0.)
        np.testing.assert_allclose(b*(1-other)+b*other,b)
        self.assertTrue(np.max(abs(other-s))>.05)

    def test_output_reconciliation_is_explicit(self):
        for row in read_csv(OUT/'weekly_decomposition.csv'):
            if row['B_main_reconciled']:
                self.assertAlmostEqual(float(row['B_main_reconciled'])+float(row['B_challenger_reconciled']),
                                       float(row['B_observed']),places=9)
                self.assertTrue(0<=float(row['challenger_share'])<=1)
            self.assertLessEqual(row['date'],'2026-08-21')

    def test_profile_targets_and_multistart_convergence(self):
        for row in read_csv(OUT/'share_profile.csv'):
            self.assertEqual(row['success'],'True')
            self.assertLess(abs(float(row['target_share'])-float(row['achieved_share'])),1e-4)
        for row in read_csv(OUT/'model_comparison.csv'):
            self.assertEqual(row['success'],'True')
            self.assertLess(float(row['multistart_objective_range']),1e-4)


if __name__=='__main__':unittest.main()
