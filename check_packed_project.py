import bpy,json,os
R=os.path.dirname(os.path.abspath(__file__))
missing=[];images=[]
for i in bpy.data.images:
 if i.source in {'GENERATED','VIEWER'}:continue
 packed=bool(i.packed_file) or bool(getattr(i,'packed_files',[]))
 exists=os.path.exists(bpy.path.abspath(i.filepath)) if i.filepath else False
 images.append({'name':i.name,'packed':packed,'external_exists':exists})
 if not packed and not exists:missing.append(i.name)
r={'images':images,'missing_images':missing,'linked_libraries':[l.filepath for l in bpy.data.libraries],'frame_range':[bpy.context.scene.frame_start,bpy.context.scene.frame_end],'fps':bpy.context.scene.render.fps,'objects':len(bpy.data.objects),'audi_rim_parent':bpy.data.objects['AUDI_RIM_DETAIL_FR_15'].parent.name}
json.dump(r,open(R+'/packed_project_QA.json','w'),indent=2)
assert not missing,missing
assert not r['linked_libraries'],r['linked_libraries']
print('PACKED_PROJECT_QA_PASS',len(images),'images')
