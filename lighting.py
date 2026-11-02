"""Night-film lighting, wet reflections, atmospheric depth and restrained bloom."""
import bpy,math
from mathutils import Vector

def configure_scene(width=1280,height=720,samples=32):
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';
 for attr,value in [('taa_render_samples',samples),('use_gtao',True),('gtao_distance',3),('use_raytracing',True),('use_fast_gi',True)]:
  if hasattr(s.eevee,attr):setattr(s.eevee,attr,value)
 s.render.resolution_x=width;s.render.resolution_y=height;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=536;s.render.threads_mode='FIXED';s.render.threads=8
 s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.film_transparent=False
 if s.world is None:s.world=bpy.data.worlds.new('Night atmosphere world')
 s.world.use_nodes=True;bg=s.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.018,.028,.055,1);bg.inputs[1].default_value=.4
 s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
 # Broad moonlight keeps car silhouettes readable outside artificial light pools.
 d=bpy.data.lights.new('Soft moon','SUN');d.energy=.65;d.color=(.45,.62,1);d.angle=.25;o=bpy.data.objects.new('Soft moon',d);bpy.context.collection.objects.link(o);o.rotation_euler=(.45,-.35,-.5)
 # Camera-facing key is NOT used: highlights remain anchored in the world.
 d=bpy.data.lights.new('Cloud bounce','AREA');d.energy=35000;d.color=(.38,.52,.8);d.shape='DISK';d.size=100;o=bpy.data.objects.new('Cloud bounce',d);bpy.context.collection.objects.link(o);o.location=(10,-10,65)
 # Low atmospheric density, not opaque fog or billowing smoke.
 m=bpy.data.materials.new('Night humidity');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();v=nt.nodes.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.0018;v.inputs['Color'].default_value=(.37,.48,.62,1);v.inputs['Anisotropy'].default_value=.35;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(v.outputs['Volume'],out.inputs['Volume'])
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,10,10));fog=bpy.context.object;fog.name='Subtle atmosphere';fog.scale=(440,240,28);fog.data.materials.append(m);fog.display_type='WIRE'
 
 for attr,value in [('volumetric_samples',24),('volumetric_tile_size','8'),('use_volumetric_shadows',False)]:
  if hasattr(s.eevee,attr):setattr(s.eevee,attr,value)
 s.use_nodes=True;nt=s.node_tree;nt.nodes.clear();rl=nt.nodes.new('CompositorNodeRLayers');gl=nt.nodes.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='HIGH';gl.threshold=2;gl.size=6;gl.mix=-.94;out=nt.nodes.new('CompositorNodeComposite');nt.links.new(rl.outputs['Image'],gl.inputs['Image']);nt.links.new(gl.outputs['Image'],out.inputs['Image'])
 return s
