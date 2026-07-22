import trimesh
import numpy as np

def lathe_solid(profile, segments=128):
    """닫힌 회전체(위/아래 캡 포함) → watertight solid"""
    profile = np.array(profile, dtype=float)
    n = len(profile)
    verts = []
    for i in range(segments):
        a = i/segments * 2*np.pi
        c, s = np.cos(a), np.sin(a)
        for (r, y) in profile:
            verts.append([r*c, y, r*s])
    verts = list(verts)
    # 중심 축 상/하 점 추가(캡용)
    bottom_c = len(verts); verts.append([0, profile[0][1], 0])
    top_c = len(verts); verts.append([0, profile[-1][1], 0])
    verts = np.array(verts)
    faces = []
    for i in range(segments):
        i2 = (i+1) % segments
        for j in range(n-1):
            a = i*n + j; b = i*n + j+1
            c = i2*n + j; d = i2*n + j+1
            faces.append([a, b, d]); faces.append([a, d, c])
        # 하단 캡
        faces.append([bottom_c, i2*n+0, i*n+0])
        # 상단 캡
        faces.append([top_c, i*n+(n-1), i2*n+(n-1)])
    m = trimesh.Trimesh(vertices=verts, faces=faces)
    m.merge_vertices(); m.fix_normals()
    return m

profile = [
    (0.02,0.0),(0.35,0.02),(0.6,0.12),(0.78,0.32),(0.85,0.6),
    (0.78,0.9),(0.6,1.12),(0.5,1.2),(0.52,1.28)
]
body = lathe_solid(profile, 128)
print("몸통 watertight:", body.is_watertight, "verts:", len(body.vertices))

# 투각 구멍
holes = []
for ring_y, count, rad in [(0.5,10,0.09),(0.78,12,0.07)]:
    ring_r = np.interp(ring_y,[p[1] for p in profile],[p[0] for p in profile])
    for k in range(count):
        a = k/count*2*np.pi
        cyl = trimesh.creation.cylinder(radius=rad, height=1.2, sections=16)
        cyl.apply_transform(trimesh.geometry.align_vectors([0,0,1],[np.cos(a),0,np.sin(a)]))
        cyl.apply_translation([np.cos(a)*ring_r, ring_y, np.sin(a)*ring_r])
        holes.append(cyl)
holes_all = trimesh.util.concatenate(holes)

pierced = body.difference(holes_all)
print("투각 후 verts:", len(pierced.vertices), "watertight:", pierced.is_watertight)
pierced.export('/home/claude/censer_pierced.glb')
import os; print("glb:", os.path.getsize('/home/claude/censer_pierced.glb'),"bytes")

# 렌더 미리보기(오프스크린) 시도
try:
    scene = trimesh.Scene(pierced)
    png = scene.save_image(resolution=(400,500))
    open('/home/claude/preview.png','wb').write(png)
    print("preview.png 저장됨")
except Exception as e:
    print("렌더 미리보기 불가(정상, 헤드리스):", str(e)[:80])
