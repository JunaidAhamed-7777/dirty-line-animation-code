import bpy,os,sys
ROOT=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,ROOT)
curbs=sorted([o for o in bpy.data.objects if o.name.startswith('Corner curb')],key=lambda o:int(o.name.rsplit('.',1)[-1]) if '.' in o.name else 0)
for i,o in enumerate(curbs):
 o.data.materials.clear();o.data.materials.append(bpy.data.materials['Curb red' if i%2==0 else 'Road paint'])
source=bpy.data.materials['Compacted ochre gravel'];mat=source.copy();mat.name='Recovered textured opaque ramp earth'
nt=mat.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
for link in list(p.inputs['Alpha'].links):nt.links.remove(link)
p.inputs['Alpha'].default_value=1
nt.links.new(p.outputs['BSDF'],out.inputs['Surface'])
for o in bpy.data.objects:
 if o.name.startswith('Graded ramp shoulder'):o.data.materials.clear();o.data.materials.append(mat)
s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_persistent_data=False;s.cycles.samples=32
s['Recovery visual QA']='Pending; do not claim identical source recovery.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/DIRTY_LINE.blend',compress=True)
print('RECOVERY_PATCHED',len(curbs))
