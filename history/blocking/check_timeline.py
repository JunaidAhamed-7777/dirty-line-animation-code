# Historical authored revision; duplicate shared helpers and all assets are omitted.
import sys,os,json,math
ROOT=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,ROOT)
from timeline import pose,camera_pose,H,R
records=[]
for i in range(481):
 t=i/24;h=pose(t);r=pose(t,False)
 assert h['speed']>0 and r['speed']>0
 assert all(math.isfinite(x) for x in h['position']+r['position'])
 records.append({'t':t,'hero':h,'rival':r})
with open(ROOT+'/timeline_validation.json','w') as f:json.dump(records,f)
for t in (0,3,5,9,9.7,10.85,12,16,17.5,20):print(t,pose(t),pose(t,False))
