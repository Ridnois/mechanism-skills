"""Pure-python cycloid disc profile (no numpy: runs inside FreeCAD). Equation: see research/specs.md #5."""
import math
def profile_points(R,rp,e,N,n):
    pts=[]
    for i in range(n):
        t=2*math.pi*i/n
        psi=math.atan2(math.sin((1-N)*t), R/(e*N)-math.cos((1-N)*t))
        pts.append((R*math.cos(t)-rp*math.cos(t+psi)-e*math.cos(N*t),
                    -R*math.sin(t)+rp*math.sin(t+psi)+e*math.sin(N*t)))
    return pts
