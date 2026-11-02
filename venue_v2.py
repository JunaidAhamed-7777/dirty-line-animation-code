import bpy
from timeline import FINISH_X,FINISH_Y
def relocate_venue():
 prefixes=('Pit ','Overhanging pit','Lit pit','Garage door','Timing ','Finish gantry','Finish truss','Finish sign','Gantry luminaire','Finish light','Drain ','Pit wall pool')
 for o in bpy.data.objects:
  if o.name.startswith(prefixes):o.location.x+=FINISH_X-112;o.location.y+=FINISH_Y+22
