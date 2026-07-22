"""반가사유상 메시의 AO(크레바스) 맵을 Cycles CPU로 베이크 → tex_in/ao.png
   깊은 홈(크레바스)일수록 어둡다. 게임에서 '솔이 못 닦는 구석' 판정에 사용."""
import bpy, os
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath='khs_buddha.glb')
obj=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
bpy.context.view_layer.objects.active=obj; obj.select_set(True)

img=bpy.data.images.new('AObake',2048,2048)
if not obj.data.materials:
    m=bpy.data.materials.new('bakeM'); m.use_nodes=True; obj.data.materials.append(m)
mat=obj.data.materials[0]; mat.use_nodes=True
node=mat.node_tree.nodes.new('ShaderNodeTexImage'); node.image=img
mat.node_tree.nodes.active=node

sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.device='CPU'
sc.cycles.samples=64
try: sc.cycles.use_denoising=False
except: pass
bpy.context.view_layer.objects.active=obj
bpy.ops.object.bake(type='AO', margin=8, use_clear=True)

os.makedirs('tex_in',exist_ok=True)
img.filepath_raw=os.path.abspath('tex_in/ao.png'); img.file_format='PNG'; img.save()
print('AO baked ->', img.filepath_raw, os.path.getsize(img.filepath_raw),'bytes')
