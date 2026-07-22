"""정교한 세척 도구 3종 (Blender bpy) → tools.glb
   서 있는 상태(+Z 위, 팁=원점 z0)로 만든 뒤 -90°X 회전+yup export
   → three.js에서 로컬 +Z가 '작업 방향', 원점이 팁이 되도록 정렬.
   objects: blow / brush / swab
"""
import bpy, bmesh, math, random
random.seed(3)

def clear():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
    for c in (bpy.data.meshes,bpy.data.curves):
        for x in list(c): c.remove(x)

def mat(name,color,metallic,rough):
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(color[0],color[1],color[2],1)
    b.inputs['Metallic'].default_value=metallic
    b.inputs['Roughness'].default_value=rough
    return m

def smooth(o):
    for p in o.data.polygons: p.use_smooth=True

def cone(r1,r2,z0,z1,seg=40,m=None):
    d=abs(z1-z0)
    bpy.ops.mesh.primitive_cone_add(vertices=seg,radius1=r1,radius2=r2,depth=d,location=(0,0,(z0+z1)/2))
    o=bpy.context.active_object; smooth(o)
    if m: o.data.materials.append(m)
    return o

def uvsphere(r,z,m=None,scale=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,radius=r,location=(0,0,z))
    o=bpy.context.active_object; o.scale=scale; smooth(o)
    if m: o.data.materials.append(m)
    return o

def join(objs,name):
    for o in bpy.context.scene.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.object.join()
    r=bpy.context.view_layer.objects.active; r.name=name
    return r

def subsurf(o,lv=2):
    m=o.modifiers.new('s','SUBSURF'); m.levels=lv; m.render_levels=lv
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.modifier_apply(modifier=m.name)

# ---------- 재질 ----------
walnut = mat('walnut',(0.20,0.09,0.035),0.0,0.55)
brass  = mat('brass',(0.83,0.63,0.28),1.0,0.28)
bristle= mat('bristle',(0.86,0.76,0.52),0.0,0.85)
rubber = mat('rubber',(0.62,0.12,0.10),0.0,0.55)
blacky = mat('blacky',(0.05,0.05,0.06),0.0,0.5)
paper  = mat('paper',(0.93,0.90,0.82),0.0,0.7)
cotton = mat('cotton',(0.97,0.97,0.95),0.0,0.9)
steel  = mat('steel',(0.7,0.72,0.75),1.0,0.3)

def build_bristle():
    """별도 노드 'brush_bristle' — 촘촘하고 가는 강모 다발(게임에서 애니메이션)."""
    parts=[]
    core=cone(0.05,0.028,0.03,0.17,seg=44,m=bristle); parts.append(core)       # 속 채움(빈틈 방지)
    cap=uvsphere(0.05,0.03,m=bristle,scale=(1,1,0.5)); parts.append(cap)        # 둥근 끝
    for rr,cnt in [(0.020,9),(0.034,15),(0.048,22),(0.060,28),(0.070,32)]:
        for i in range(cnt):
            a=(i/cnt)*2*math.pi + rr*11
            z0=0.018+random.uniform(0,0.016)                                    # 팁 살짝 프레이
            b=cone(0.0036,0.0014,z0,0.176,seg=5,m=bristle)
            b.location=(math.cos(a)*rr, math.sin(a)*rr, 0)
            parts.append(b)
    return join(parts,'brush_bristle')

def build_brush():
    """'brush' = 놋쇠 페룰 + 나무 손잡이(정적 부분)."""
    parts=[]
    fer=cone(0.085,0.075,0.15,0.30,seg=40,m=brass); subsurf(fer,1); parts.append(fer)
    ring=cone(0.088,0.088,0.19,0.205,seg=40,m=brass); parts.append(ring)
    ring2=cone(0.088,0.088,0.25,0.265,seg=40,m=brass); parts.append(ring2)
    prof=[(0.0,0.30),(0.05,0.31),(0.058,0.40),(0.046,0.58),(0.04,0.78),(0.052,0.95),(0.036,1.05),(0.0,1.08)]
    verts=[(x,0,z) for x,z in prof]
    me=bpy.data.meshes.new('handleP')
    bm=bmesh.new()
    vs=[bm.verts.new(v) for v in verts]
    for i in range(len(vs)-1): bm.edges.new((vs[i],vs[i+1]))
    bm.to_mesh(me); bm.free()
    ho=bpy.data.objects.new('handle',me); bpy.context.scene.collection.objects.link(ho)
    bpy.context.view_layer.objects.active=ho; ho.select_set(True)
    m=ho.modifiers.new('scr','SCREW'); m.axis='Z'; m.steps=48; m.render_steps=48; m.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=m.name)
    ho.data.materials.append(walnut); smooth(ho); parts.append(ho)
    return join(parts,'brush')

def build_blow():
    parts=[]
    # 노즐(끝이 팁) — 가늘게 → 넓게
    noz=cone(0.014,0.055,0.0,0.20,seg=32,m=blacky); subsurf(noz,1); parts.append(noz)
    tipring=cone(0.02,0.02,0.0,0.012,seg=24,m=steel); parts.append(tipring)
    # 고무 벌브(물방울형): 구를 뒤로 눌러 뾰족하게
    bulb=uvsphere(0.16,0.40,m=rubber,scale=(1,1,1.35)); subsurf(bulb,1); parts.append(bulb)
    # 뒤쪽 밸브 꼭지
    val=cone(0.02,0.028,0.60,0.66,seg=20,m=blacky); parts.append(val)
    return join(parts,'blow')

def build_swab():
    parts=[]
    tip=uvsphere(0.032,0.03,m=cotton,scale=(1,1,1.5)); parts.append(tip)
    rod=cone(0.0125,0.0125,0.045,0.55,seg=20,m=paper); parts.append(rod)
    back=uvsphere(0.032,0.575,m=cotton,scale=(1,1,1.5)); parts.append(back)
    return join(parts,'swab')

def orient_export():
    # 원점을 팁(0,0,0)으로 → -90°X 회전 → 트랜스폼 완전 적용(노드 identity)
    import os
    sc=bpy.context.scene
    sc.cursor.location=(0,0,0)
    for o in sc.objects:
        if o.type!='MESH': continue
        for x in sc.objects: x.select_set(False)
        o.select_set(True); bpy.context.view_layer.objects.active=o
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')      # 원점 → 팁
        o.rotation_euler=(math.radians(-90),0,0)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=os.path.abspath('tools.glb'),export_format='GLB',
                              use_selection=True, export_yup=True)

def main():
    clear()
    b=build_brush()
    br=build_bristle()
    w=build_blow()
    s=build_swab()
    for o in (b,br,w,s):
        print(f"  {o.name}: verts={len(o.data.vertices)} polys={len(o.data.polygons)} mats={len(o.data.materials)}")
    orient_export()
    print("DONE tools.glb")

main()
