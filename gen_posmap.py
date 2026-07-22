import trimesh, numpy as np
from PIL import Image
N=512
def rasterize(glb, out):
    s=trimesh.load(glb,force='scene')
    g=list(s.geometry.values())[0]
    uv=g.visual.uv.copy()
    V=g.vertices.astype(np.float64)
    F=g.faces
    mn=V.min(0); sz=V.max(0)-mn; sz[sz<1e-9]=1
    Vn=(V-mn)/sz               # 0..1 over local bbox
    rgb=np.zeros((N,N,3),np.float64)
    val=np.zeros((N,N),np.uint8)
    # UV -> pixel (flipY=false in game: v maps directly; game uses vUv without flip on amt)
    P=uv.copy(); P[:,0]*=N; P[:,1]*=N
    for tri in F:
        p0,p1,p2=P[tri]; c0,c1,c2=Vn[tri]
        minx=int(max(0,np.floor(min(p0[0],p1[0],p2[0])))); maxx=int(min(N-1,np.ceil(max(p0[0],p1[0],p2[0]))))
        miny=int(max(0,np.floor(min(p0[1],p1[1],p2[1])))); maxy=int(min(N-1,np.ceil(max(p0[1],p1[1],p2[1]))))
        if maxx<minx or maxy<miny: continue
        den=((p1[1]-p2[1])*(p0[0]-p2[0])+(p2[0]-p1[0])*(p0[1]-p2[1]))
        if abs(den)<1e-12: continue
        ys,xs=np.mgrid[miny:maxy+1,minx:maxx+1]
        px=xs+0.5; py=ys+0.5
        a=((p1[1]-p2[1])*(px-p2[0])+(p2[0]-p1[0])*(py-p2[1]))/den
        b=((p2[1]-p0[1])*(px-p2[0])+(p0[0]-p2[0])*(py-p2[1]))/den
        c=1-a-b
        m=(a>=-1e-4)&(b>=-1e-4)&(c>=-1e-4)
        if not m.any(): continue
        pos=a[...,None]*c0+b[...,None]*c1+c[...,None]*c2
        yy=ys[m]; xx=xs[m]
        rgb[yy,xx]=pos[m]; val[yy,xx]=255
    out_img=np.dstack([(np.clip(rgb,0,1)*255).astype(np.uint8), val])
    Image.fromarray(out_img,'RGBA').save(out)
    return val.mean()/255*100
import sys
for glb,out in [('khs_buddha.glb','tex_in/pos.png'),('art2.glb','tex2/pos.png'),
                ('art3.glb','tex3/pos.png'),('art4.glb','tex4/pos.png'),('art5.glb','tex5/pos.png')]:
    cov=rasterize(glb,out)
    print('%-16s -> %-18s coverage %.1f%%'%(glb,out,cov))
