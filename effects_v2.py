"""DIRTY LINE V2 dust recovery: SPEC RECONSTRUCTION, not byte-exact recovery.
Original procedural volumes/grit, no external assets, no scene save/render.
API build_effects(frames=536); consumes timeline.pose(t, hero=True/False).
Requires actual visual comparison with surviving WIPs before final production.
"""
import bpy,math,random
from mathutils import Vector
from timeline import pose

PREFIX='V2 recovered dust | '

def _ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)

def _envelope(t,start,end,fadein=.42,fadeout=.85):
    return _ease((t-start)/fadein)*_ease((end-t)/fadeout)

def _sphere_mesh():
    vs=[];fs=[];rings=12;sides=24
    for j in range(rings+1):
        lat=math.pi*j/rings
        for i in range(sides):
            a=math.tau*i/sides;vs.append((math.sin(lat)*math.cos(a),math.sin(lat)*math.sin(a),math.cos(lat)))
    for j in range(rings):
        for i in range(sides):fs.append((j*sides+i,(j+1)*sides+i,(j+1)*sides+(i+1)%sides,j*sides+(i+1)%sides))
    me=bpy.data.meshes.new(PREFIX+'shared volume boundary');me.from_pydata(vs,[],fs);me.update();return me

def _volume_material(label,density,offset):
    m=bpy.data.materials.new(PREFIX+label);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
    out=n.new('ShaderNodeOutputMaterial');vol=n.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.39,.32,.235,1);vol.inputs['Anisotropy'].default_value=.18;l.new(vol.outputs['Volume'],out.inputs['Volume'])
    tc=n.new('ShaderNodeTexCoord');center=n.new('ShaderNodeVectorMath');center.operation='SUBTRACT';center.inputs[1].default_value=(.5,.5,.5);l.new(tc.outputs['Generated'],center.inputs[0])
    scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=2;l.new(center.outputs['Vector'],scale.inputs[0])
    length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';l.new(scale.outputs['Vector'],length.inputs[0])
    edge=n.new('ShaderNodeMapRange');edge.clamp=True;edge.interpolation_type='SMOOTHERSTEP';edge.inputs['From Min'].default_value=.18;edge.inputs['From Max'].default_value=.98;edge.inputs['To Min'].default_value=1;edge.inputs['To Max'].default_value=0;l.new(length.outputs['Value'],edge.inputs['Value'])
    geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=.68;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.72;noise.inputs['Distortion'].default_value=.45;noise.inputs['W'].default_value=offset;l.new(geo.outputs['Position'],noise.inputs['Vector'])
    erosion=n.new('ShaderNodeMapRange');erosion.clamp=True;erosion.interpolation_type='SMOOTHSTEP';erosion.inputs['From Min'].default_value=.34;erosion.inputs['From Max'].default_value=.72;erosion.inputs['To Min'].default_value=0;erosion.inputs['To Max'].default_value=1;l.new(noise.outputs['Fac'],erosion.inputs['Value'])
    mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(edge.outputs['Result'],mul.inputs[0]);l.new(erosion.outputs['Result'],mul.inputs[1])
    strength=n.new('ShaderNodeValue');strength.name='Dust envelope';strength.outputs[0].default_value=0
    amount=n.new('ShaderNodeMath');amount.operation='MULTIPLY';l.new(mul.outputs[0],amount.inputs[0]);l.new(strength.outputs[0],amount.inputs[1]);l.new(amount.outputs[0],vol.inputs['Density'])
    return m,strength,noise,density

def _volume(col,mesh,label,dims,density,offset):
    # Mesh data copy only for per-object material; tiny volume bounds, not dense mesh.
    me=mesh.copy();ob=bpy.data.objects.new(PREFIX+label,me);col.objects.link(ob);ob.scale=tuple(v/2 for v in dims)
    m,strength,noise,base=_volume_material(label,density,offset);me.materials.append(m)
    return ob,strength,noise,base

def _follow(ob,t,hero,behind,lift,lag=0,lateral=0):
    p=pose(max(0,t-lag),hero);yaw=float(p['yaw']);v=Vector(p['position']);forward=Vector((math.cos(yaw),math.sin(yaw),0));side=Vector((-math.sin(yaw),math.cos(yaw),0))
    # Dust stays tied to road elevation, not the airborne vehicle's jump height.
    v.z=.04;ob.location=v-forward*behind+side*lateral+Vector((0,0,lift));ob.rotation_euler=(0,0,yaw)


def _linear(datablock):
    if datablock.animation_data and datablock.animation_data.action:
        for fc in datablock.animation_data.action.fcurves:
            for kp in fc.keyframe_points:kp.interpolation='LINEAR'


def build_effects(frames=536):
    name=PREFIX+'EFFECTS'
    if bpy.data.collections.get(name):raise RuntimeError('Recovered V2 effects already built; refusing duplicates')
    col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col);mesh=_sphere_mesh();fps=24
    # Continuous, overlapping noisy density fields, never opaque sphere surfaces.
    definitions=[('rear wheel roost',(12,5,3.2),5.2,3.5,.40,0),('lagged wake',(26,8,4.5),4.0,10,.50,.2),('fine lingering cloud',(34,10,5.5),1.8,18,.45,.35)]
    volumes=[]
    for i,(label,dims,density,behind,lift,lag) in enumerate(definitions):
        ob,strength,noise,base=_volume(col,mesh,label,dims,density,2.37+i*5.41);volumes.append(ob)
        for fr in range(1,frames+1):
            t=(fr-1)/fps;_follow(ob,t,True,behind,lift,lag)
            ob.keyframe_insert('location',frame=fr);ob.keyframe_insert('rotation_euler',frame=fr)
            strength.outputs[0].default_value=base*_envelope(t,3.7,12.7);strength.outputs[0].keyframe_insert('default_value',frame=fr)
            noise.inputs['W'].default_value=2.37+i*5.41+t*.18;noise.inputs['W'].keyframe_insert('default_value',frame=fr)
        _linear(ob);_linear(strength.id_data)
    # Four very low thin tire wisps at finish, two per car. Same eroded volume
    # shader, subdued neutral dust: no bright circular smoke sprites.
    for hero in (True,False):
        for side in (-1,1):
            label=('Audi' if hero else 'GT40')+' finish tire '+str(side)
            ob,strength,noise,base=_volume(col,mesh,label,(4,.55,.32),.42,11+side+(0 if hero else 4));volumes.append(ob)
            for fr in range(1,frames+1):
                t=(fr-1)/fps;_follow(ob,t,hero,2.4,.14,.035,side*.79)
                ob.keyframe_insert('location',frame=fr);ob.keyframe_insert('rotation_euler',frame=fr)
                strength.outputs[0].default_value=base*_envelope(t,19,20.6,.16,.35);strength.outputs[0].keyframe_insert('default_value',frame=fr)
                noise.inputs['W'].default_value=t*.3+side;noise.inputs['W'].keyframe_insert('default_value',frame=fr)
            _linear(ob);_linear(strength.id_data)
    rng=random.Random(853019);grain=bpy.data.meshes.new(PREFIX+'shared irregular grit')
    grain.from_pydata([(1,0,0),(-.8,0,0),(0,.7,0),(0,-.9,0),(.1,0,.7),(0,0,-.6)],[],[(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)]);grain.update()
    m=bpy.data.materials.new(PREFIX+'ochre mineral grit');m.diffuse_color=(.20,.135,.07,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=.9;grain.materials.append(m)
    for i in range(850):
        birth=rng.uniform(3.7,12);life=rng.uniform(.25,.7);tire=rng.choice((-1,1));p=pose(birth,True);yaw=float(p['yaw']);forward=Vector((math.cos(yaw),math.sin(yaw),0));side=Vector((-math.sin(yaw),math.cos(yaw),0))
        origin=Vector(p['position'])-forward*1.23+side*(tire*.80);origin.z=.08
        # Rearward ballistic grain with modest residual vehicle velocity, gravity
        # and ground-clamped tail. These are geometry flecks, not luminous sparks.
        velocity=forward*rng.uniform(-7,-2)+side*rng.uniform(-2.4,2.4)+Vector((0,0,rng.uniform(1.1,3.4)))
        ob=bpy.data.objects.new(PREFIX+'grit %04d'%i,grain);col.objects.link(ob);size=rng.uniform(.008,.025);spin=Vector([rng.uniform(-8,8) for _ in range(3)])
        start=max(2,math.ceil(birth*fps)+1);end=min(frames,math.ceil((birth+life)*fps)+1)
        ob.scale=(0,0,0);ob.keyframe_insert('scale',frame=1);ob.keyframe_insert('scale',frame=start-1)
        for fr in range(start,end+1):
            age=max(0,(fr-1)/fps-birth);q=origin+velocity*age+Vector((0,0,-.5*9.81*age*age));q.z=max(.035,q.z);ob.location=q;ob.rotation_euler=spin*age
            ob.keyframe_insert('location',frame=fr);ob.keyframe_insert('rotation_euler',frame=fr)
            fade=1-_ease((age/life-.72)/.28);ob.scale=(size*fade,)*3;ob.keyframe_insert('scale',frame=fr)
        ob.scale=(0,0,0);ob.keyframe_insert('scale',frame=min(frames,end+1));_linear(ob)
    if mesh.users==0:bpy.data.meshes.remove(mesh)
    col['reconstruction']='Specification-based recovery, not byte-exact; visual QA required';col['grit_count']=850;col['dust_window']='3.7–12.7s';col['finish_wisps']='19–20.6s'
    return {'collection':col.name,'volumes':len(volumes),'ballistic_grains':850,'source_status':'specification reconstruction; not exact recovered source'}
