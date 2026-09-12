from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];D=R/'data/four_total_bridges_20260913'
b=pd.read_csv(D/'bar_source_bridge.csv');s=pd.read_csv(D/'source_zero_sensitivity.csv');f=pd.read_csv(D/'total_ratio_formula_test.csv')
assert set(b.source.astype(str))=={'2504','2510','2609'}
assert set(b.smooth_weeks)=={1,3,5}
assert (s.groupby('method').post_Azmoth_RMSE_px.min()>s.groupby('method').pre_train_RMSE_px.max()).all()
assert f[(f.method=='ratio_with_bar_free_origin')&(f.window=='post_Azmoth')].n.iloc[0]==22
print('four total bridge checks passed')
