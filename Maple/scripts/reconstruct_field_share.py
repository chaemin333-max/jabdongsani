"""Recover field share, multiply canonical total, and compare pre-leap episodes."""
from pathlib import Path
import calendar,json,hashlib
import numpy as np
import pandas as pd
from PIL import Image
R=Path(__file__).resolve().parents[1]; O=R/'data/field_share_reconstruction_20260912'
NAMES=['boss','field','coin_dark','coin_light','other']

def run():
    O.mkdir(parents=True,exist_ok=True)
    im=np.asarray(Image.open(R.parent/'251016 생산처별메소.png').convert('RGB'),float)
    records=[]
    palette=[np.median(im[y-1:y+2,1348:1385],axis=(0,1)) for y in [309,341,373,403,435]]
    for i,day in enumerate(pd.date_range('2025-04-17',periods=25,freq='7D')):
        x=136+49*i
        for name,c,(lo,hi) in zip(NAMES,palette,[(300,570),(600,700),(698,739),(630,740),(752,757)]):
            col=np.median(im[lo:hi+1,x-2:x+3],axis=1)
            dist=np.linalg.norm(col-c,axis=1);j=np.argmin(dist)
            if name=='boss':
                score=col[:,0]-(col[:,1]+col[:,2])/2;j=np.argmax(score);dist[j]=0 if score[j]>25 else 999
            if name=='coin_dark':
                score=col[:,2]-col[:,0];j=np.argmax(score);dist[j]=0 if score[j]>15 else 999
            y=lo+j;h=757-y
            records.append(dict(source='251016',date=day.strftime('%Y-%m-%d'),series=name,x_pixel=x,y_pixel=y,height=h if dist[j]<90 else np.nan,status='detected' if dist[j]<90 else 'unresolved',color_distance=dist[j]))
    new=pd.read_csv(R/'data/now_20260910/production_by_source_weekly.csv')
    rename=dict(zip(['boss_rewards','field','serazar_coin','coin_exchange','other'],NAMES))
    for row in new.itertuples():
        records.append(dict(source='260910',date=row.date,series=rename[row.series],x_pixel=row.x_pixel,y_pixel=row.line_y_pixel,height=row.height_from_zero_pixels,status=row.status,color_distance=np.nan))
    p=pd.DataFrame(records);p.to_csv(O/'source_pixels.csv',index=False)
    shares=[]
    for source,g in p.groupby('source'):
        h=g.pivot(index='date',columns='series',values='height').reindex(columns=NAMES)
        # One isolated missing field point between observed weeks, no endpoint extension.
        field=h.field.copy()
        for i in range(1,len(h)-1):
            if pd.isna(field.iloc[i]) and pd.notna(field.iloc[i-1]) and pd.notna(field.iloc[i+1]):
                h.iloc[i,h.columns.get_loc('field')]=(field.iloc[i-1]+field.iloc[i+1])/2
        for day,v in h.iterrows():
            lower={};upper={};notes=[]
            for n in NAMES:
                a=v[n]
                if pd.notna(a):lower[n]=max(0,a-2);upper[n]=a+2
                elif n=='other':lower[n]=0;upper[n]=3;notes.append('other_axis_band')
                elif n=='coin_dark' and source=='260910':lower[n]=0;upper[n]=20;notes.append('unresolved_dark_coin_0_to_20px_visual_band')
                elif n=='coin_light' and day>='2026-01-15':lower[n]=0;upper[n]=15;notes.append('unresolved_light_coin_0_to_15px_visual_band')
                else:lower[n]=upper[n]=np.nan;notes.append('missing_'+n)
            midpoint={n:(lower[n]+upper[n])/2 for n in NAMES}
            den=sum(midpoint.values()); f=midpoint['field']
            shares.append(dict(source=source,date=day,field_share=f/den,field_share_low=lower['field']/(lower['field']+sum(upper[n] for n in NAMES if n!='field')),field_share_high=upper['field']/(upper['field']+sum(lower[n] for n in NAMES if n!='field')),field_interpolated=bool(pd.isna(field.loc[day]) and pd.notna(v.field)),notes=';'.join(notes),**{n+'_height':midpoint[n] for n in NAMES}))
    s=pd.DataFrame(shares)
    raw=json.loads((R/'data/meso_total_production_raw_canonical.json').read_text(encoding='utf-8'))['total']
    def total(ds):
        z=pd.Timestamp(ds);x=(z.year-2023)*12+z.month-1+(z.day-1)/calendar.monthrange(z.year,z.month)[1]
        assert min(raw['month_coordinate'])<=x<=max(raw['month_coordinate'])
        return np.interp(x,raw['month_coordinate'],raw['index'])*6.495250069
    s['P_total']=s.date.map(total)
    for suffix in ['', '_low','_high']:s['F_field'+suffix]=s.P_total*s['field_share'+suffix]
    s.to_csv(O/'source_shares.csv',index=False)
    overlap=s.pivot(index='date',columns='source',values='F_field').dropna()
    overlap['new_over_old_minus_one']=overlap['260910']/overlap['251016']-1
    overlap.to_csv(O/'overlap_audit.csv')
    # Prefer latest image; fall back to older observed share if the new endpoint is unresolved.
    selected=s.sort_values(['date','source']).groupby('date',sort=True).apply(lambda g:g[g.F_field.notna()].iloc[-1] if g.F_field.notna().any() else g.iloc[-1],include_groups=False).reset_index()
    weights=pd.read_csv(R/'data/boss_productivity_weights_20260912/weekly_weights.csv')
    d=selected.merge(weights[['date','A_accounts','C_accounts','weight_status']],on='date',how='left')
    d.to_csv(O/'weekly_field.csv',index=False)
    windows=pd.read_csv(R/'data/now_20260910/season_identification_windows.csv');results=[];episodes=[]
    for e in windows.itertuples():
        start=pd.Timestamp(e.start);end=pd.Timestamp(e.first_leap)
        pre=d[(pd.to_datetime(d.date)>=start-pd.Timedelta(weeks=6))&(pd.to_datetime(d.date)<start)].dropna(subset=['F_field'])
        post=d[(pd.to_datetime(d.date)>=start)&(pd.to_datetime(d.date)<end)].copy()
        if len(pre)<4 or len(post)==0:continue
        prex=(pd.to_datetime(pre.date)-start).dt.days.to_numpy()/7
        slope,intercept=np.polyfit(prex,pre.F_field,1)
        flat=pre.tail(3).F_field.mean()
        for method in ['flat_total','linear_total','flat_per_account']:
            for drift in [-.10,0,.10]:
                z=post.copy();x=(pd.to_datetime(z.date)-start).dt.days/7
                base=np.full(len(z),flat) if method=='flat_total' else intercept+slope*x if method=='linear_total' else (pre.tail(3).F_field/pre.tail(3).A_accounts).mean()*z.A_accounts
                z['main_counterfactual']=np.asarray(base)*(1+drift)
                z['C_field_signed_excess']=z.F_field-z.main_counterfactual
                z['C_field_low']=z.F_field_low-z.main_counterfactual
                z['C_field_high']=z.F_field_high-z.main_counterfactual
                z['feasible']=(z.C_field_signed_excess>=0)&(z.C_field_signed_excess<=z.F_field)
                z['C_field_per_account']=np.where(z.feasible&(z.C_accounts>0),z.C_field_signed_excess/z.C_accounts,np.nan)
                z['season']=e.season;z['method']=method;z['main_drift_assumed']=drift
                episodes.append(z)
                results.append(dict(season=e.season,method=method,main_drift_assumed=drift,pre_weeks=len(pre),post_weeks=len(z),post_field_mean=z.F_field.mean(),main_counterfactual_mean=z.main_counterfactual.mean(),signed_excess_mean=z.C_field_signed_excess.mean(),signed_share=z.C_field_signed_excess.sum()/z.F_field.sum(min_count=1),valid_field_weeks=int(z.F_field.notna().sum()),feasible_weeks=int(z.feasible.sum()),count_observed_weeks=int((z.C_accounts>0).sum())))
    ep=pd.concat(episodes,ignore_index=True);su=pd.DataFrame(results)
    ep.to_csv(O/'preleap_scenarios.csv',index=False);su.to_csv(O/'episode_summary.csv',index=False)
    assert (d.dropna(subset=['field_share']).field_share.between(0,1)).all()
    np.testing.assert_allclose(d.F_field,d.P_total*d.field_share,equal_nan=True)
    assert d.date.max()=='2026-08-20'
    assert set(su.season)=={2,3,4}
    assert (ep.loc[~ep.feasible,'C_field_per_account'].isna()).all()
    receipt={'status':'CONDITIONAL_FIELD_SHARE_AND_PRELEAP_EXCESS','share_method':'field height divided by sum of source heights; multiply canonical total','latest_priority':'260910; 251016 fallback when latest unresolved','pixel_sensitivity':'+/-2px; unresolved other 0..3; dark coin 0..20; postJan15 light coin 0..15px; midpoint is an assumption, not confidence intervals','interpolation':'isolated interior field gap only','S1':'opening outside image coverage','no_postleap_extrapolation':True,'overlap_weeks':len(overlap),'overlap_median_abs_pct':float(overlap.new_over_old_minus_one.abs().median()*100),'checks_passed':5}
    (O/'manifest.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt));print(su[(su.main_drift_assumed==0)].to_string(index=False))
if __name__=='__main__':run()
