"""
백제금동대향로 (Baekje Gilt-bronze Incense Burner) — 1차 절차적 모델링 (Blender bpy)
4파트: 봉황(phoenix) / 박산뚜껑(mountain lid) / 연꽃몸통(lotus body) / 용받침(dragon base)
목표: 표면 굴곡(relief)을 실제 지오메트리로 만들어 '구석구석 세척' 감을 살린다.
출력: censer.glb (파트별 named mesh) + censer_preview.stl (미리보기용)
"""
import bpy, bmesh, math, random
from mathutils import Vector, Euler

random.seed(7)

def clear():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
    for c in list(bpy.data.curves): bpy.data.curves.remove(c)

def smooth(o):
    for p in o.data.polygons: p.use_smooth=True

def subsurf(o, lv=2):
    m=o.modifiers.new('s','SUBSURF'); m.levels=lv; m.render_levels=lv

def bevel(o, w=0.01, seg=2):
    m=o.modifiers.new('b','BEVEL'); m.width=w; m.segments=seg; m.limit_method='ANGLE'; m.angle_limit=math.radians(35)

def apply_all(o):
    bpy.context.view_layer.objects.active=o
    for m in list(o.modifiers):
        try: bpy.ops.object.modifier_apply(modifier=m.name)
        except Exception as e: print('apply fail',m.name,e)

def join(objs, name):
    for o in bpy.context.scene.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.object.join()
    r=bpy.context.view_layer.objects.active; r.name=name
    return r

# ---------- 한 장의 연꽃잎(petal) ----------
def make_petal(length=0.9, width=0.42, curl=0.5):
    """뾰족하고 살짝 오목한 잎. 밑동에서 위로 뻗음(로컬 +Z가 길이방향)."""
    bm=bmesh.new()
    rows=6; cols=5
    verts=[[None]*cols for _ in range(rows)]
    for i in range(rows):
        t=i/(rows-1)                      # 0(밑동)~1(끝)
        w=width*math.sin(math.pi*(0.15+0.85*t))*(1-t*0.55)  # 중간이 넓고 끝이 뾰족
        for j in range(cols):
            s=(j/(cols-1))-0.5
            x=s*2*w
            z=t*length
            # 잎맥 따라 오목하게(가운데가 안쪽으로), 끝으로 갈수록 뒤로 젖힘
            depth=(0.5-abs(s))*width*0.5*curl
            y=-depth - t*t*curl*0.5
            verts[i][j]=bm.verts.new((x,y,z))
    bm.verts.index_update()
    for i in range(rows-1):
        for j in range(cols-1):
            bm.faces.new((verts[i][j],verts[i][j+1],verts[i+1][j+1],verts[i+1][j]))
    me=bpy.data.meshes.new('petal'); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new('petal',me); bpy.context.scene.collection.objects.link(o)
    sol=o.modifiers.new('sol','SOLIDIFY'); sol.thickness=0.03
    return o

def ring_of_petals(cx,cy,cz, radius, count, tilt, scale, zlen, name, phase=0.0):
    petals=[]
    for k in range(count):
        ang=phase+2*math.pi*k/count
        p=make_petal(length=zlen, width=0.42*scale)
        p.scale=(scale,scale,scale)
        # 위로 세우되 바깥으로 tilt
        p.rotation_euler=Euler((tilt,0,0),'XYZ')
        # 링 위치로 배치 후 중심축 기준 회전
        p.location=(0,-radius,0)
        # 회전행렬로 링 배치
        import mathutils
        R=mathutils.Matrix.Rotation(ang,4,'Z')
        p.location=R@Vector((0,-radius,0))+Vector((cx,cy,cz))
        p.rotation_euler=(mathutils.Matrix.Rotation(ang,4,'Z')@p.rotation_euler.to_matrix().to_4x4()).to_euler()
        petals.append(p)
    return petals

# =========================================================
# 1) 연꽃 몸통 (lotus body)
# =========================================================
def build_body():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,radius=1.05,location=(0,0,2.55))
    core=bpy.context.active_object; core.name='body_core'
    # 살짝 계란형(위로 갈수록 좁게)
    core.scale=(1,1,1.15)
    smooth(core)
    parts=[core]
    # 위를 향한 연꽃잎을 3~4겹 겹쳐 몸통을 덮음
    layers=[
        dict(z=1.95,r=0.98,count=12,tilt=math.radians(38),scale=1.15,zlen=1.15,phase=0.0),
        dict(z=2.35,r=1.02,count=14,tilt=math.radians(30),scale=1.05,zlen=1.15,phase=math.pi/14),
        dict(z=2.75,r=0.95,count=14,tilt=math.radians(22),scale=0.95,zlen=1.05,phase=0.0),
        dict(z=3.10,r=0.72,count=10,tilt=math.radians(14),scale=0.8,zlen=0.95,phase=math.pi/10),
    ]
    for L in layers:
        parts+=ring_of_petals(0,0,L['z'],L['r'],L['count'],L['tilt'],L['scale'],L['zlen'],'p',L['phase'])
    for p in parts: smooth(p)
    body=join(parts,'몸통_lotus')
    return body

# =========================================================
# 2) 박산 뚜껑 (mountain lid) — 산봉우리 층층 + 봉우리 사이 굴곡
# =========================================================
def make_peak(h,r,sides=6):
    bpy.ops.mesh.primitive_cone_add(vertices=sides, radius1=r, radius2=0.0, depth=h)
    o=bpy.context.active_object
    return o

def build_lid():
    # 돔
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,radius=1.0,location=(0,0,3.55))
    dome=bpy.context.active_object; dome.name='lid_dome'
    # 아래 반 잘라 돔으로
    bm=bmesh.new(); bm.from_mesh(dome.data)
    for v in list(bm.verts):
        if v.co.z<0: v.co.z*=0.12
    bm.to_mesh(dome.data); bm.free()
    dome.scale=(1,1,1.15)
    smooth(dome)
    parts=[dome]
    # 산봉우리: 동심 링으로, 아래(큰것)→위(작은것)
    rings=[
        dict(z=3.62,r=0.92,n=15,ph=3.62,ph2=0.0,h=0.5,pr=0.13,tilt=0.5),
        dict(z=3.9,r=0.72,n=13,h=0.5,pr=0.12,tilt=0.42,ph2=0.3),
        dict(z=4.15,r=0.5,n=10,h=0.46,pr=0.11,tilt=0.32,ph2=0.0),
        dict(z=4.38,r=0.28,n=7,h=0.4,pr=0.10,tilt=0.2,ph2=0.4),
        dict(z=4.55,r=0.0,n=1,h=0.34,pr=0.10,tilt=0.0,ph2=0.0),
    ]
    import mathutils
    for R in rings:
        for k in range(R['n']):
            ang=R.get('ph2',0)+2*math.pi*k/max(R['n'],1)
            hh=R['h']*random.uniform(0.82,1.15)
            pk=make_peak(hh,R['pr']*random.uniform(0.85,1.1),sides=6)
            base=Vector((0,-R['r'],R['z']))
            rot=mathutils.Matrix.Rotation(ang,4,'Z')
            pos=rot@base
            pk.location=pos+Vector((0,0,hh*0.4))
            # 바깥으로 젖힘
            pk.rotation_euler=(rot@mathutils.Matrix.Rotation(-R['tilt'],4,'X')).to_euler()
            smooth(pk); parts.append(pk)
    # 작은 인물/동물 융기(범프)
    for _ in range(18):
        z=random.uniform(3.65,4.2); rr=random.uniform(0.3,0.85)*(4.4-z)/0.8
        ang=random.uniform(0,2*math.pi)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(0.05,0.09),
            location=(rr*math.cos(ang),rr*math.sin(ang),z))
        b=bpy.context.active_object; b.scale=(1,1,1.6); smooth(b); parts.append(b)
    lid=join(parts,'뚜껑_mountain')
    return lid

# =========================================================
# 3) 봉황 finial (phoenix)
# =========================================================
def build_phoenix():
    parts=[]
    # 구슬(orb)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13,location=(0,0,4.66)); orb=bpy.context.active_object; smooth(orb); parts.append(orb)
    # 몸통(계란형, 앞으로 살짝)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15,location=(0,0.02,4.9)); bod=bpy.context.active_object
    bod.scale=(0.7,1.0,1.5); smooth(bod); parts.append(bod)
    # 목/머리
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08,location=(0,0.14,5.16)); head=bpy.context.active_object
    head.scale=(0.8,1.1,1.0); smooth(head); parts.append(head)
    # 부리
    bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=0.035,radius2=0,depth=0.13,location=(0,0.24,5.17))
    beak=bpy.context.active_object; beak.rotation_euler=(math.radians(90),0,0); smooth(beak); parts.append(beak)
    # 날개 2장(펼침)
    for s in (-1,1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14,location=(s*0.16,-0.02,4.98))
        w=bpy.context.active_object; w.scale=(0.9,0.28,0.5)
        w.rotation_euler=(0,s*math.radians(28),math.radians(s*18)); smooth(w); parts.append(w)
    # 꼬리(길게 뒤로/위로)
    bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=0.1,radius2=0.02,depth=0.5,location=(0,-0.16,5.02))
    tail=bpy.context.active_object; tail.rotation_euler=(math.radians(-35),0,0); tail.scale=(1,1,1); smooth(tail); parts.append(tail)
    ph=join(parts,'봉황_phoenix')
    return ph

# =========================================================
# 4) 용 받침 (dragon base) — 물결 받침 + 솟구치는 용 다리
# =========================================================
def swept_tube(points, radius0, radius1, name):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for i,p in enumerate(points):
        bp=sp.bezier_points[i]; bp.co=p; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    cu.bevel_depth=radius0; cu.bevel_resolution=4
    cu.taper_object=None
    o=bpy.data.objects.new(name,cu); bpy.context.scene.collection.objects.link(o)
    return o

def build_base():
    parts=[]
    # 물결 받침(납작한 원반 + 물결 테)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=1.0,depth=0.16,location=(0,0,0.12))
    disc=bpy.context.active_object
    bm=bmesh.new(); bm.from_mesh(disc.data)
    for v in bm.verts:
        rr=math.hypot(v.co.x,v.co.y)
        if rr>0.7:
            ang=math.atan2(v.co.y,v.co.x)
            v.co.z+=0.06*math.sin(ang*7)
    bm.to_mesh(disc.data); bm.free(); smooth(disc); parts.append(disc)
    # 중심 기둥(몸통 바닥까지)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=0.12,depth=1.3,location=(0,0,0.85))
    stem=bpy.context.active_object; smooth(stem); parts.append(stem)
    # 용 다리 3가닥: 물결에서 솟아 기둥을 감쌈
    import mathutils
    for k in range(3):
        ang=2*math.pi*k/3
        R=mathutils.Matrix.Rotation(ang,3,'Z')
        pts=[R@Vector(p) for p in [
            (0.0,-0.85,0.16),(0.15,-0.62,0.5),(0.05,-0.32,0.85),(0.0,-0.16,1.2),(0.0,-0.05,1.45)]]
        tube=swept_tube(pts,0.075,0.03,f'dragon{k}')
        # 곡선 → 메쉬
        bpy.context.view_layer.objects.active=tube; tube.select_set(True)
        bpy.ops.object.convert(target='MESH'); tube=bpy.context.active_object
        smooth(tube); parts.append(tube)
        # 용머리(다리 끝 근처)
        hp=R@Vector((0.15,-0.62,0.5))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11,location=hp)
        hd=bpy.context.active_object; hd.scale=(0.8,1.2,0.8); smooth(hd); parts.append(hd)
    base=join(parts,'용받침_dragon')
    return base

# =========================================================
def uv_and_finish(o, angle=66):
    bpy.context.view_layer.objects.active=o
    for x in bpy.context.scene.objects: x.select_set(False)
    o.select_set(True)
    # subsurf 약하게 + bevel로 매끈하게
    apply_all(o)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    smooth(o)

def main():
    clear()
    body=build_body()
    lid=build_lid()
    ph=build_phoenix()
    base=build_base()
    for o in (body,lid,ph,base):
        uv_and_finish(o)
    # 내보내기
    import os
    # 전체 미리보기용 STL
    for x in bpy.context.scene.objects: x.select_set(x.type=='MESH')
    bpy.ops.wm.stl_export(filepath=os.path.abspath('censer_preview.stl'), export_selected_objects=True)
    # 파트별 glb (하나의 glb에 4개 named mesh)
    bpy.ops.export_scene.gltf(filepath=os.path.abspath('censer.glb'), export_format='GLB',
                              use_selection=False, export_yup=True)
    # 통계
    for o in (body,lid,ph,base):
        print(f"  {o.name}: verts={len(o.data.vertices)} tris≈{len(o.data.polygons)}")
    print("DONE")

main()
