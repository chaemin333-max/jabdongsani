"""Trace the visibly light-cyan Azmoth line from its first original pixel.

The path finder prefers the light-cyan RGB palette and a continuous stroke.
Dark-blue coin crossings may hide the cyan color; those pixels are flagged as
occluded rather than silently certified as visible cyan observations.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[1]
SRC=R/'assets/sources/four_now_originals/250410_생산처별장기추이.jpg'
O=R/'data/four_now_redigitized_20260913'
im=np.asarray(Image.open(SRC).convert('RGB'),dtype=float)
palette=np.array([192.,217.,228.])

# Search only the launch vicinity.  Before the first light-cyan stroke this
# interior patch is white; the dark-blue coin curve lies lower.  A three-pixel
# continuation check excludes isolated JPEG artifacts.
launch=[]
for x in range(1050,1110):
    distances=np.linalg.norm(im[740:770,x]-palette,axis=1)
    y=int(np.argmin(distances)+740)
    if distances.min()<35:
        launch.append((x,y,float(distances.min())))
assert launch and all(launch[i][0]==launch[0][0]+i for i in range(3))
first_x,first_y,_=launch[0]
assert first_x==1087 and 745<=first_y<=760
last_x=1262
end_roi=np.linalg.norm(im[700:750,last_x]-palette,axis=1)
last_y=int(np.argmin(end_roi)+700)

xs=np.arange(first_x,last_x+1)
ys=np.arange(705,810)
rgb=im[705:810,first_x:last_x+1].transpose(1,0,2)
distance=np.linalg.norm(rgb-palette,axis=2)
color_cost=np.minimum(distance/8,8)
color_cost[(rgb[:,:,0]<145)|((rgb[:,:,2]-rgb[:,:,0])<4)]=8
n,m=color_cost.shape
dp=np.full((n,m),1e9);back=np.zeros((n,m),dtype=np.int16)
dp[0,first_y-705]=color_cost[0,first_y-705]
for i in range(1,n):
    for j in range(m):
        k0=max(0,j-5);k1=min(m,j+6)
        prev=np.arange(k0,k1)
        cost=dp[i-1,prev]+.12*(prev-j)**2
        pick=int(np.argmin(cost))
        dp[i,j]=color_cost[i,j]+cost[pick]
        back[i,j]=int(prev[pick])
path=np.zeros(n,dtype=int);path[-1]=last_y-705
for i in range(n-1,0,-1):path[i-1]=back[i,path[i]]
assert path[0]+705==first_y and path[-1]+705==last_y

rows=[]
for i,x in enumerate(xs):
    y=int(ys[path[i]]);d=float(distance[i,path[i]])
    rows.append(dict(x_pixel=int(x),y_pixel=y,rgb_distance=d,
        status='light_cyan_observed' if d<=35 else 'crossing_or_occluded_path'))
out=pd.DataFrame(rows)
out.to_csv(O/'azmoth_light_cyan_raster.csv',index=False)
canvas=Image.open(SRC).convert('RGB');draw=ImageDraw.Draw(canvas)
for r in out.itertuples():
    draw.ellipse((r.x_pixel-1,r.y_pixel-1,r.x_pixel+1,r.y_pixel+1),
        fill='#ed00ed' if r.status=='light_cyan_observed' else '#ff9b00')
canvas.save(O/'azmoth_light_cyan_trace_qa.png')
canvas.crop((1050,690,1265,820)).resize((1290,780)).save(O/'azmoth_light_cyan_trace_crop.png')
receipt=dict(source=str(SRC.relative_to(R)),sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
    color_palette=palette.tolist(),first_pixel_x=first_x,first_pixel_y=first_y,
    launch_date='2024-10-17',last_pixel_x=last_x,last_pixel_y=last_y,
    observed_pixels=int((out.status=='light_cyan_observed').sum()),
    occluded_pixels=int((out.status!='light_cyan_observed').sum()),
    meaning='first visible cyan x fixes nominal launch-week x; crossing paths carry separate status')
(O/'azmoth_light_cyan_manifest.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
