import numpy as np, sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cycloid import *
R,rp,e,N=32.,3.,1.5,12
t,x,y=profile(R,rp,e,N,20000); dt=t[1]-t[0]
r=np.hypot(x,y); print("K1=eN/R=",e*N/R," e_max(cusp)=R/N=",R/N)
print("disc tip r=%.3f root r=%.3f  OD=%.2f"%(r.max(),r.min(),2*r.max()))
# independent check: every profile point must be at distance rp from the epitrochoid (pin-centre path)
te,xe,ye=epitrochoid(R,e,N,20000)
d=np.sqrt((x[:,None][::40]-xe[None,:])**2+(y[:,None][::40]-ye[None,:])**2).min(1)
print("offset-distance to epitrochoid: min %.4f max %.4f (should be %.1f)"%(d.min(),d.max(),rp))
# curvature of epitrochoid (pin-centre path) : offset inward needs rho_min > rp where concave side
k=curvature(xe,ye,dt); print("epitrochoid curvature radius: min |rho| %.3f ; max curvature sign flip? neg=%s"%(1/np.abs(k).max(), (k<0).any()))
kp=curvature(x,y,dt); print("disc profile: min |rho| %.3f ; sign changes: pos=%d neg=%d"%(1/np.abs(kp).max(),(kp>0).sum(),(kp<0).sum()))
# self-intersection check via sorted polar (profile should be star-shaped)
from math import atan2
# rp limit scan
for rp_ in [2,3,4,5,6]:
    _,xx,yy=profile(R,rp_,e,N,20000); kk=curvature(xx,yy,dt)
    print("rp=%d: min curvature radius of disc (signed concave min) = %.3f ; concave regions=%s"%(rp_,1/np.abs(kk).max(),(kk<0).any()))
