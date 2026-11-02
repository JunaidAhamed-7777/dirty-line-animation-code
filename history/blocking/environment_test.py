# Historical authored revision; duplicate shared helpers and all assets are omitted.
import bpy,sys,os
ROOT=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,ROOT)
from course import build_course
from lighting import configure_scene
from effects import build_effects
from timeline import camera_pose
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);build_course();s=configure_scene(640,360,8);build_effects()
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
pos,target,lens=camera_pose(7);cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
s.frame_set(169);s.render.filepath=ROOT+'/previews/environment-fx-test.png';bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/ENVIRONMENT_WIP.blend');bpy.ops.render.render(write_still=True)
