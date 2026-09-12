"""Independent raw RGB reread of NOW line charts; output pixels, never fitted totals.

Every missing sample remains missing.  Pixel y is image position, not a money
amount; the original vertical zero and cross-slide scale are not inferred here.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/sources/four_now_originals"
OUT = ROOT / "data/four_now_redigitized_20260913"
OUT.mkdir(parents=True, exist_ok=True)


def read(name):
    return np.asarray(Image.open(SRC / name).convert("RGB"), dtype=np.float32)


def trace(im, xs, color, lo, hi, *, limit=40, step=16, initial=None,
          omit_before=None, omit_x=(), gray_mode=False):
    """Track only original color pixels, with a local continuity filter.

    The previous *observed* position guides ambiguous thin lines; it is never
    emitted at an x lacking a matching pixel.  A long unresolved interval may
    still require manual inspection because the guide can follow another line.
    """
    color = np.asarray(color, dtype=float)
    prior = initial
    misses = 0
    output = []
    for x in xs:
        if (omit_before is not None and x < omit_before) or any(abs(x-b) <= 2 for b in omit_x):
            output.append((np.nan, np.nan, "not_observable")); continue
        patch = im[lo:hi+1, max(0,x-1):x+2]
        distance = np.linalg.norm(patch-color, axis=2)
        # Require a colored line pixel; near-white anti-aliasing and background
        # must not become a sample merely because there is no better match.
        sat = np.ptp(patch, axis=2)
        if gray_mode:
            distance[(sat > 25) | (patch.mean(axis=2) < 80)] = np.inf
        else:
            distance[sat < 12] = np.inf
        best = distance.min(axis=1)
        candidates = np.flatnonzero(best < limit)
        if prior is not None and misses < 5:
            nearby = candidates[np.abs(candidates + lo-prior) <= step]
            if len(nearby): candidates = nearby
            else: candidates = np.array([], dtype=int)
        if len(candidates):
            # Color first; proximity breaks ties when the line overlaps a legend
            # or dashed event marker.
            score = best[candidates] + (np.abs(candidates+lo-prior)*0.15 if prior is not None else 0)
            yy = int(candidates[np.argmin(score)] + lo)
            prior = yy
            misses = 0
            output.append((yy, float(best[yy-lo]), "rgb_observed"))
        else:
            misses += 1
            output.append((np.nan, np.nan, "unresolved"))
    return output


panels = [
    # source, chart, x span/spacing, legend colors, original-image y windows.
    ("231116", "boss_tier_lines", "231116_보스구간별생산.png", range(75,1661,4), [
        ("hard_damien_to_hard_jinhilla", [42,50,131], 570,1070, 58, 32, None),
        ("normal_suu_to_normal_dunkel", [119,130,197], 740,1070, 55, 32, None),
        ("easy_cygnus_to_chaos_bellum", [155,155,156], 680,1085, 30, 32, None),
        ("daily_boss", [107,131,202], 1200,1340, 46, 22, None),
        ("normal_seren_to_extreme_kalos", [122,124,123], 1260,1360, 28, 20, None)]),
    ("250410", "production_sources", "250410_생산처별장기추이.jpg", range(368,1263,3), [
        ("boss", [191,75,84], 300,745, 60, 45, None),
        ("field", [253,158,166], 645,800, 36, 28, None),
        ("azmoth", [183,219,238], 690,823, 28, 25, 1083),
        ("other_coin", [42,86,130], 692,823, 34, 24, 790),
        ("other", [188,190,189], 812,828, 25, 8, None)]),
    ("251016", "production_sources", "251016_생산처별.png", range(136,1313,3), [
        ("boss", [198,91,72], 300,570, 43, 22, None),
        ("field", [235,158,160], 585,710, 38, 18, None),
        ("azmoth_coin", [34,77,111], 685,753, 35, 14, None),
        ("other_coin", [169,217,231], 620,755, 29, 22, None),
        ("other", [165,166,166], 750,761, 22, 8, None)]),
    ("260910", "production_sources", "260910_생산처별.png", range(192,1131,3), [
        ("boss", [205,91,73], 330,655, 44, 20, None),
        ("field", [234,151,154], 625,710, 38, 14, None),
        ("serazar_coin", [40,77,109], 684,717, 35, 10, None),
        ("coin_exchange", [166,215,231], 650,717, 30, 18, None),
        ("other", [168,170,170], 705,719, 22, 7, None)]),
    ("251016", "total_production", "251016_총생산.png", range(150,1381,2), [
        ("total", [187,50,64], 290,760, 50, 55, None)]),
]

records = []; manifest = {}
for snapshot, chart, filename, xs, series in panels:
    im = read(filename)
    manifest[f"{snapshot}/{chart}"] = dict(image=filename,
        image_sha256=hashlib.sha256((SRC/filename).read_bytes()).hexdigest(),
        image_size=[int(im.shape[1]),int(im.shape[0])], x_count=len(xs))
    for name, color, lo, hi, limit, step, omit_before in series:
        if snapshot == '250410':
            initial = {'boss':700,'field':770,'other':821}.get(name)
        elif snapshot == '231116':
            initial = {'hard_damien_to_hard_jinhilla':1045,
                       'normal_suu_to_normal_dunkel':1055,
                       'easy_cygnus_to_chaos_bellum':1061,
                       'daily_boss':1306,
                       'normal_seren_to_extreme_kalos':1340}.get(name)
        else: initial = None
        samples = trace(im, xs, color, lo, hi, limit=limit, step=step,
                        omit_before=omit_before, initial=initial,
                        gray_mode=(snapshot=='231116' and name in
                            ('easy_cygnus_to_chaos_bellum','normal_seren_to_extreme_kalos')))
        for x,(y,dist,status) in zip(xs,samples):
            records.append(dict(snapshot=snapshot,chart=chart,series=name,
                x_pixel=x,y_pixel=y,rgb_distance=dist,status=status,
                image=filename))

data = pd.DataFrame.from_records(records)
# On the April slide the pale Azmoth coin stroke and the dark coin stroke
# overlap in the post-launch weeks.  A palette hit alone does not identify
# which physical line is present; retain the candidate coordinate for QA but
# prevent its use as a confirmed production-source value.
ambiguous = ((data.snapshot == '250410') & (data.series == 'azmoth') &
             (data.status == 'rgb_observed'))
data.loc[ambiguous, 'status'] = 'candidate_overlap_unverified'
# These tiny near-axis "other" strokes are visually indistinguishable from
# the axis and compression artifacts.
ambiguous = ((data.snapshot.isin(['251016','260910'])) &
             (data.series == 'other') & (data.status == 'rgb_observed'))
data.loc[ambiguous, 'status'] = 'candidate_axis_unverified'
data.to_csv(OUT/'line_pixels_all.csv',index=False)
counts = data.groupby(['snapshot','chart','series','status']).size().rename('n').reset_index()
counts.to_csv(OUT/'line_read_status.csv',index=False)
(OUT/'line_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
qa_colors = {
    'boss':'#00ef22', 'field':'#1818ff', 'azmoth':'#ed00ed',
    'azmoth_coin':'#ed00ed', 'other_coin':'#00dada',
    'coin_exchange':'#00dada', 'serazar_coin':'#eacc00',
    'total':'#00ef22', 'hard_damien_to_hard_jinhilla':'#00ef22',
    'normal_suu_to_normal_dunkel':'#ed00ed',
    'easy_cygnus_to_chaos_bellum':'#00dada',
    'daily_boss':'#eacc00', 'normal_seren_to_extreme_kalos':'#ed2222'
}
for (snapshot,chart),group in data.groupby(['snapshot','chart']):
    canvas = Image.open(SRC/group.image.iloc[0]).convert('RGB')
    draw = ImageDraw.Draw(canvas)
    for row in group.itertuples():
        if row.status not in ('rgb_observed','candidate_overlap_unverified'):
            continue
        col = qa_colors.get(row.series,'#000000')
        x,y = int(row.x_pixel),int(row.y_pixel)
        draw.ellipse((x-2,y-2,x+2,y+2),fill=col)
    canvas.save(OUT/f'{snapshot}_{chart}_qa.png')
print(counts.to_string(index=False))
