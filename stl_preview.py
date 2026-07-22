import sys, struct, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LightSource

def load_stl(path):
    with open(path,'rb') as f:
        data=f.read()
    # binary STL: 80 byte header + uint32 count + 50 bytes/tri
    n=struct.unpack('<I', data[80:84])[0]
    tris=np.zeros((n,3,3),dtype=np.float32)
    off=84
    for i in range(n):
        # 12 floats: normal(3)+v1(3)+v2(3)+v3(3); skip normal
        vals=struct.unpack('<12f', data[off:off+48])
        tris[i,0]=vals[3:6]; tris[i,1]=vals[6:9]; tris[i,2]=vals[9:12]
        off+=50
    return tris

def render(path, out, title):
    tris=load_stl(path)
    verts=tris.reshape(-1,3)
    ctr=verts.mean(0);
    mn=verts.min(0); mx=verts.max(0); dim=mx-mn
    # compute face normals for shading
    v0=tris[:,0]; v1=tris[:,1]; v2=tris[:,2]
    fn=np.cross(v1-v0, v2-v0)
    ln=np.linalg.norm(fn,axis=1); ln[ln==0]=1; fn=fn/ln[:,None]
    light=np.array([0.4,-0.7,0.6]); light=light/np.linalg.norm(light)
    shade=np.clip(fn@light,0.15,1.0)
    base=np.array([0.83,0.72,0.45])
    colors=base[None,:]*shade[:,None]
    colors=np.clip(colors,0,1)
    fig=plt.figure(figsize=(12,5))
    angles=[(12,-88),(20,-45),(12,0)]  # elev,azim ; front, 3q, side (Z up)
    names=['front','3quarter','side']
    for k,((el,az),nm) in enumerate(zip(angles,names)):
        ax=fig.add_subplot(1,3,k+1,projection='3d')
        pc=Poly3DCollection(tris, facecolors=colors, edgecolors='none')
        ax.add_collection3d(pc)
        # equal aspect
        c=(mn+mx)/2; r=dim.max()/2*1.05
        ax.set_xlim(c[0]-r,c[0]+r); ax.set_ylim(c[1]-r,c[1]+r); ax.set_zlim(c[2]-r,c[2]+r)
        ax.set_box_aspect((1,1,1))
        ax.view_init(elev=el, azim=az)
        ax.set_axis_off()
        ax.set_title(nm,fontsize=9)
    fig.suptitle(f"{title}   tris={len(tris)}  dims={dim[0]:.1f}x{dim[1]:.1f}x{dim[2]:.1f}", fontsize=11)
    plt.tight_layout()
    plt.savefig(out, dpi=90, facecolor='#15120c')
    print(f"{title}: tris={len(tris)} dims={dim[0]:.2f}x{dim[1]:.2f}x{dim[2]:.2f} -> {out}")

if __name__=='__main__':
    for path,out,title in [
        ('reference_bapga.stl','prev_bapga.png','반가사유상 (A)'),
        ('file_b.stl','prev_b.png','file_b'),
        ('file_c.stl','prev_c.png','file_c'),
    ]:
        render(path,out,title)
