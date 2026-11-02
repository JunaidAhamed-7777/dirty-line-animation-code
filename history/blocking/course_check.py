# Historical authored revision; duplicate shared helpers and all assets are omitted.
import bpy,sys,os
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,ROOT)
from course import build_course
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
build_course();s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.06,.06,.06)
bpy.ops.object.camera_add(location=(10,-125,170));c=bpy.context.object;c.rotation_euler=(Vector((0,4,0))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=230;s.camera=c
s.render.filepath=ROOT+'/previews/course-geography.png';bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/COURSE_BLOCKOUT.blend');bpy.ops.render.render(write_still=True)
