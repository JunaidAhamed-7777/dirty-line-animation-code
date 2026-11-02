"""Depth-based atmospheric perspective avoids an expensive full-world volume."""
import bpy

def configure_atmosphere_grade():
 s=bpy.context.scene
 fog=bpy.data.objects.get('Subtle atmosphere')
 if fog:fog.hide_render=True
 s.view_layers[0].use_pass_mist=True;s.world.mist_settings.start=0;s.world.mist_settings.depth=250;s.world.mist_settings.falloff='LINEAR'
 nt=s.node_tree;rl=next(n for n in nt.nodes if n.type=='R_LAYERS');gl=next(n for n in nt.nodes if n.type=='GLARE');factor=nt.nodes.new('CompositorNodeMath');factor.name='Distance haze weight';factor.operation='MULTIPLY';factor.inputs[1].default_value=.42;nt.links.new(rl.outputs['Mist'],factor.inputs[0]);mix=nt.nodes.new('CompositorNodeMixRGB');mix.name='Cool atmospheric perspective';mix.blend_type='MIX';mix.inputs[2].default_value=(.025,.045,.075,1);nt.links.new(factor.outputs[0],mix.inputs[0]);nt.links.new(rl.outputs['Image'],mix.inputs[1]);nt.links.new(mix.outputs[0],gl.inputs['Image'])
 s.cycles.transparent_max_bounces=64;s.cycles.samples=32;s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.10
