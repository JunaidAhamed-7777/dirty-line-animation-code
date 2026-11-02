"""Temporal QA treatment only: measured rim/tire pivots are already correct.
Call before a controlled consecutive-frame comparison. Never changes wheel speed,
geometry, scale, pivot or physics; do not describe this as an axle repair.
"""
import bpy

def tune_wheel_temporal_sampling():
    changed=[]
    for prefix in ('AUDI','GT40'):
        for pos in ('FL','FR','BL','BR'):
            pivot=bpy.data.objects.get(prefix+'_WHEEL_'+pos)
            if not pivot:continue
            for ob in pivot.children_recursive:
                if ob.type!='MESH':continue
                props=getattr(ob,'cycles',None)
                if props:
                    if hasattr(props,'use_motion_blur'):props.use_motion_blur=True
                    if hasattr(props,'motion_steps'):props.motion_steps=3
                changed.append(ob.name)
    return {'wheel_meshes':changed,'note':'Consecutive render comparison required; default axis/pivots remain untouched.'}
