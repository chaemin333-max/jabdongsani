"""Cross-check new raw-pixel readings; no source-to-canonical fitting for output."""
from pathlib import Path
import json

import numpy as np
import pandas as pd

R=Path(__file__).resolve().parents[1]
O=R/'data/four_now_redigitized_20260913'
bars=pd.read_csv(O/'boss_bars_all.csv',dtype={'snapshot':str})
lines=pd.read_csv(O/'raster_trace_nonweekly.csv',dtype={'snapshot':str})
weekly=pd.read_csv(O/'weekly_line_pixels_all.csv',dtype={'snapshot':str})

# The slide itself prints eight monthly shares.  These are transcribed values,
# not estimates from bar heights; rounding leaves some rows at 99.9%.
months=pd.date_range('2023-04-01',periods=8,freq='MS').strftime('%Y-%m')
boss=[64.8,64.6,60.5,52.3,55.7,58.6,60.9,61.7]
field=[27.2,27.0,29.2,36.8,34.9,33.2,31.2,31.1]
ursus=[8.0,8.3,10.3,10.8,9.4,8.1,7.9,7.2]
printed=pd.DataFrame(dict(month=months,boss_pct=boss,field_pct=field,
                          ursus_pct=ursus))
printed['sum_pct']=printed[['boss_pct','field_pct','ursus_pct']].sum(axis=1)
printed['status']='direct_printed_monthly_percent'
printed['image']='231116_생산처별비율.png'
printed.to_csv(O/'231116_printed_source_shares.csv',index=False)
assert np.max(abs(printed.sum_pct-100))<=.11

# Put a *single* multiplicative factor on each image-pair overlap.  These are
# diagnostics of chart shapes.  Tier definitions differ across broadcasts.
pairs=[('250410','251016','total_height_px','total_height_px','all_boss_stacks'),
       ('251016','260910','total_height_px','total_height_px','all_boss_stacks'),
       ('250410','251016','tier3_height_px','tier3_height_px','hard_suu_to_blackmage_vs_hard_damien_to_jinhilla_proxy'),
       ('251016','260910','tier3_height_px','tier2_height_px','hard_damien_to_jinhilla_vs_hard_suu_to_jinhilla_proxy')]
detail=[];summary=[]
for a,b,ca,cb,label in pairs:
    x=bars[bars.snapshot==a][['date',ca]].rename(columns={ca:'a_px'}).merge(
      bars[bars.snapshot==b][['date',cb]].rename(columns={cb:'b_px'}),on='date')
    x=x[(x.a_px>0)&(x.b_px>0)].copy()
    k=float(np.median(x.b_px/x.a_px))
    x['factor_b_per_a']=k;x['relative_difference']=x.b_px/(k*x.a_px)-1
    x['snapshot_a']=a;x['snapshot_b']=b;x['measure']=label
    detail.append(x)
    summary.append(dict(snapshot_a=a,snapshot_b=b,measure=label,
        overlap_weeks=len(x),median_factor_b_per_a=k,
        median_abs_difference_pct=100*float(x.relative_difference.abs().median()),
        p90_abs_difference_pct=100*float(x.relative_difference.abs().quantile(.9))))
pd.concat(detail,ignore_index=True).to_csv(O/'boss_overlap_detail.csv',index=False)
pd.DataFrame(summary).to_csv(O/'boss_overlap_summary.csv',index=False)

# Earlier total extraction is a QA comparator only.  Both reads originate in
# the same image, so pixel agreement is not an independent external truth.
n=lines[(lines.snapshot=='251016')&(lines.chart=='total_production')&
        (lines.status=='rgb_observed')][['x_pixel','y_pixel']]
old=pd.read_csv(R/'data/total_origin_audit_20260913/original_total_pixels.csv')
j=n.merge(old,left_on='x_pixel',right_on='x')
delta=j.y_pixel-j.y
total_qa=dict(matched_pixels=len(j),mean_abs_y_difference_px=float(abs(delta).mean()),
    p95_abs_y_difference_px=float(abs(delta).quantile(.95)),
    max_abs_y_difference_px=float(abs(delta).max()))

# RGB hit counts include only raw observations.  Ambiguous/axis candidates
# remain explicitly separate and must not be used in a sum of sources.
coverage=lines.groupby(['snapshot','chart','series','status']).size().rename('count').reset_index()
coverage.to_csv(O/'raster_trace_status.csv',index=False)
weekly_counts=weekly.groupby(['snapshot','chart']).date.nunique()
assert weekly_counts.loc[('250410','production_sources')]==118
assert weekly_counts.loc[('251016','production_sources')]==25
assert weekly_counts.loc[('260910','production_sources')]==53
cyan=weekly[(weekly.snapshot=='250410')&(weekly.series=='azmoth')&
            (weekly.status=='direct_weekly_rgb')].sort_values('date')
assert len(cyan)==24 and cyan.iloc[0].date=='2024-10-17' and cyan.iloc[0].x_pixel==1087
straight=pd.read_csv(O/'250410_naive_segment_straightness.csv')
clear_kinks=straight[straight.verdict=='INTERIOR_KINK_GT5PX'].groupby('series').size().to_dict()
assert clear_kinks.get('azmoth',0)==0 and clear_kinks.get('boss',0)>0
joint=json.loads((O/'250410_joint_weekly_manifest.json').read_text(encoding='utf-8'))
joint_axis=pd.read_csv(O/'250410_joint_weekly_axis.csv')
joint_points=pd.read_csv(O/'250410_joint_weekly_points.csv')
point_test=pd.read_csv(O/'250410_point_aware_segment_test.csv')
heldout=pd.read_csv(O/'250410_leave_one_source_out.csv')
assert len(joint_axis)==118 and joint_axis.loc[joint_axis.date=='2024-10-17','x_week'].iloc[0]==1087
assert joint['unmatched_bend_candidates']==0
assert (point_test.verdict=='WITHIN_STROKE_AND_POINT_SIZE').all()
assert (joint_points.groupby('date').x_week.nunique()==1).all()
receipt={'total_image_independent_reread_qa':total_qa,
         'boss_overlap_summary':summary,
         'boss_bar_counts':{s:int(len(g)) for s,g in bars.groupby('snapshot')},
         'weekly_line_chart_counts':{f'{s}/{c}':int(n) for (s,c),n in weekly_counts.items()},
         'azmoth_launch_week':dict(first_date='2024-10-17',first_x=1087,observed_weeks=24),
         'old_single_pixel_rigid_grid_false_flags':{k:int(v) for k,v in clear_kinks.items()},
         'joint_point_size_audit':dict(weeks=int(joint['weeks']),
            bend_candidates=int(joint['raw_corner_candidates']),
            unmatched_bends=int(joint['unmatched_bend_candidates']),
            straight_stroke_review_segments=int((point_test.verdict!='WITHIN_STROKE_AND_POINT_SIZE').sum()),
            heldout_review_segments=int(heldout.review_gt6px.sum())),
         'scope':'raw source-image pixels and direct printed shares only',
         'no_new_total_estimate':True,
         'zero_policy':'unknown for line charts; never infer money from y pixels or fill unresolved components'}
(O/'reread_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
assert receipt['boss_bar_counts']=={'250410':104,'251016':132,'260910':105}
assert total_qa['mean_abs_y_difference_px']<2
print(json.dumps(receipt,ensure_ascii=False,indent=2))
