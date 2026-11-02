"""Make actual GT40 lamp faces visibly lit and aim body-attached road beams.
No scene load/save/render. Call after refine_lamp_glass(), on fresh or saved scene.
Only lamp/spot objects changed; model geometry and indicator materials retained.
"""
import bpy,math
from mathutils import Vector

def _emitter(name,color,strength,thin_glass=False):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*color,1);e.inputs['Strength'].default_value=strength
    if thin_glass:
        tr=n.new('ShaderNodeBsdfTransparent');add=n.new('ShaderNodeAddShader');l.new(tr.outputs[0],add.inputs[0]);l.new(e.outputs[0],add.inputs[1]);l.new(add.outputs[0],out.inputs['Surface'])
    else:l.new(e.outputs[0],out.inputs['Surface'])
    return m

def fix_gt40_headlights():
    body=bpy.data.objects['GT40_BODY'];report=[]
    # These are actual circular primary lens surfaces, NOT the large aerodynamic
    # covers or amber turn indicators. No substitute lamp discs are introduced.
    for name,strength,thin in [('GT40_HeadLightGlass',12,True),('GT40_HeadLights',35,False),('GT40_SecondaryHeadlights',16,False)]:
        ob=bpy.data.objects.get(name)
        if not ob or ob.type!='MESH':raise RuntimeError('Expected supplied GT40 lamp missing: '+name)
        m=_emitter('V2 lit '+name,(1,.84,.63),strength,thin)
        ob.data.materials.clear();ob.data.materials.append(m)
        for p in ob.data.polygons:p.material_index=0
        report.append({'lamp':name,'emission':strength})
    lights=sorted([o for o in bpy.data.objects if o.type=='LIGHT' and o.name.startswith('GT40 working headlight')],key=lambda o:o.name)
    if len(lights)!=2:raise RuntimeError('Expected exactly two GT40 road spots')
    for ob,side in zip(lights,(-1,1)):
        ob.parent=body;ob.matrix_parent_inverse.identity();ob.location=(2.005,side*.62,.535)
        ob.rotation_mode='XYZ';ob.rotation_euler=Vector((1,side*.015,-.055)).to_track_quat('-Z','Y').to_euler()
        d=ob.data;d.type='SPOT';d.energy=1800;d.color=(1,.84,.63);d.spot_size=math.radians(35);d.spot_blend=.65;d.shadow_soft_size=.035
        report.append({'beam':ob.name,'body_local_position':list(ob.location),'power_w':d.energy})
    return report
