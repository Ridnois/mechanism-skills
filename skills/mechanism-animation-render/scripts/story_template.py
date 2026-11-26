"""TEMPLATE (from the cycloidal-drive project). Copy next to the .blend together with render_base.py renamed to render.py, then edit ONLY the project-specific blocks:
  PROJECT-SPECIFIC: ferndale/HDRI file name, light names, CASING object list + park direction (adopt()), EXPLODE/CASING_K keys, speed(), CAM waypoints, GROUPS (glow stages), PREVIEW_T, SCENES.
Modes:  -- preview   stills at key times -> renders/v3_preview (RGBA, composite on a dark backdrop to look at them)
        -- check     per-frame test that no removed-casing part is inside the camera frustum
        -- clip      key every frame (linear) and render RGBA PNG; env FRAMES=a-b, FRAMEDIR=dir (resumable, use render_chunks.sh)
Original docstring follows.
"""
"""v3 30 s / 30 fps storyboard + renderer. Casing parts fly away (never hidden while visible), glow encodes the torque path, transparent background, ferndale HDRI.
blender -b cycloidal_drive.blend --python story30.py -- preview     (stills of key times -> renders/v3_preview/)
blender -b cycloidal_drive.blend --python story30.py -- clip        (env FRAMES=a-b, FRAMEDIR=dir)"""
import bpy, sys, os, math
MODE=sys.argv[sys.argv.index("--")+1]
HERE=os.path.dirname(os.path.abspath(bpy.data.filepath))
sys.argv=[sys.argv[0],"--","__none__"]
exec(open(os.path.join(HERE,"render.py")).read().split("for s in shots:")[0])
FPS=30; T=30.0; NF=int(FPS*T)
# ---------------- look: ferndale HDRI, transparent film
env.image=bpy.data.images.load(os.path.join(HERE,"ferndale_studio_04_2k.exr"))
bgh.inputs["Strength"].default_value=float(os.environ.get("HDRI_STR","1.0"))
hsv=nt.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value=float(os.environ.get("HDRI_SAT","0.3"))
nt.links.new(env.outputs[0],hsv.inputs["Color"]); nt.links.new(hsv.outputs[0],bgh.inputs[0])
for n,k in (("key",0.45),("rim",0.45),("back",0.35)): bpy.data.lights[n].energy*=k
sc.render.film_transparent=True; sc.render.image_settings.color_mode='RGBA'; sc.view_settings.exposure=float(os.environ.get("EXPO","-0.2"))
cam.clip_start=0.002; cam.clip_end=20
# ---------------- glow hook: every Principled BSDF gets emission = ObjectColor.rgb * ObjectColor.alpha * GLOW
GLOW=float(os.environ.get("GLOW","1.5"))
for m in bpy.data.materials:
    if not m.use_nodes: continue
    nt=m.node_tree; pb=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not pb: continue
    oi=nt.nodes.new("ShaderNodeObjectInfo"); mu=nt.nodes.new("ShaderNodeMath"); mu.operation='MULTIPLY'; mu.inputs[1].default_value=GLOW
    nt.links.new(oi.outputs["Color"],pb.inputs["Emission Color"]); nt.links.new(oi.outputs["Alpha"] if "Alpha" in oi.outputs else oi.outputs[1],mu.inputs[0]); nt.links.new(mu.outputs[0],pb.inputs["Emission Strength"])
for o in bpy.data.objects: o.color=(1,1,1,0)
# ---------------- casing rigs (parents at origin; objects keep their own drivers)
def empty(n): e=bpy.data.objects.new(n,None); sc.collection.objects.link(e); return e
EB,EH,EF=empty("CasingBack"),empty("CasingHousing"),empty("CasingFront")
def adopt(e,names):
    for n in names: bpy.data.objects[n].parent=e
adopt(EB,["back_cover","shaft_bearing_outer","shaft_bearing_cage"]+[f"cover_bolt_{i}" for i in range(6)])
adopt(EH,["housing"]); adopt(EF,["front_cover","hub_bearing_outer","hub_bearing_cage"])
CASING=[bpy.data.objects[n] for n in ["back_cover","shaft_bearing_outer","shaft_bearing_cage","housing","front_cover","hub_bearing_outer","hub_bearing_cage"]+[f"cover_bolt_{i}" for i in range(6)]]
FD=(-0.866,0.5)    # front cover leaves sideways (only ever from the fully exploded state, where it is clear of the hub)
def set_casing(c):
    EB.location=(0,0,-1.3*c); EH.location=(0,0,-0.9*c); EF.location=(FD[0]*1.3*c,FD[1]*1.3*c,0.05*c)
# ---------------- time functions
def ss(u): u=min(1,max(0,u)); return u*u*(3-2*u)
def keys(pts,t):
    if t<=pts[0][0]: return pts[0][1]
    for (t0,v0),(t1,v1) in zip(pts,pts[1:]):
        if t<=t1: return v0+(v1-v0)*ss((t-t0)/(t1-t0))
    return pts[-1][1]
EXPLODE=[(0,0),(3.0,0),(4.6,1),(7.6,1),(9.4,0.55),(14.4,0.55),(16.4,0),(25.0,0),(26.2,1),(27.4,1),(29.2,0),(30,0)]
CASING_K=[(0,0),(7.4,0),(9.0,1),(26.2,1),(27.6,0),(30,0)]
V_LOW=0.2   # output rev/s (12 rpm) during the slow part of the accel/decel scene
def speed(t):   # output revolutions per second; 1.0 = 60 rpm
    if t<21: return 1.0
    if t<22.4: return 1+(V_LOW-1)*ss((t-21)/1.4)
    if t<23.4: return V_LOW
    if t<25.0: return V_LOW+(1-V_LOW)*ss((t-23.4)/1.6)
    return 1.0
_dt=1/600; _cum=[0.0]
for i in range(int(T/_dt)+2): _cum.append(_cum[-1]+speed(i*_dt)*_dt)
def out_revs(t): i=t/_dt; k=int(i); return _cum[k]+(_cum[k+1]-_cum[k])*(i-k)
def alpha(t): return out_revs(t)*11*360.0       # input angle, deg
CAM=[ # t, r, yaw, z, target z, lens, f-stop
 (0.0,.34,-45,.20,.0035,80,11),(1.5,.34,-41,.19,.0035,80,11),(3.0,.38,-36,.14,.0035,76,14),(5.0,.83,-30,.03,-.008,70,16),(7.4,.83,-6,.03,-.008,70,16),
 (8.6,.32,28,-.075,-.045,50,9),(9.8,.30,50,-.040,-.045,48,9),(11.0,.30,72,-.020,-.030,46,9),(12.4,.30,94,0.0,-.008,46,9),(13.6,.30,116,.030,.016,46,9),(14.6,.32,134,.060,.034,46,9),(15.6,.30,146,.10,.012,64,11),
 (17.0,.28,160,-.14,-.004,65,11),(19.0,.30,186,.0,.0,70,11),(20.8,.30,214,.13,.006,70,11),
 (22.0,.30,236,-.16,0,70,14),(25.0,.25,250,-.17,0,70,14),
 (26.4,.83,272,.03,-.008,70,16),(27.6,.83,288,.03,-.008,70,16),(29.0,.46,304,.15,.0035,76,12),(30.0,.34,315,.20,.0035,80,11)]
def cam_at(t):
    P=CAM; n=len(P)
    if t<=P[0][0]: return P[0][1:]
    for i in range(n-1):
        if t<=P[i+1][0]: break
    t0,t1=P[i][0],P[i+1][0]; h=t1-t0; u=(t-t0)/h
    def tan(j,k):   # finite-difference tangent (zero at the ends)
        if j==0 or j==n-1: return 0.0
        return (P[j+1][k]-P[j-1][k])/(P[j+1][0]-P[j-1][0])
    out=[]
    for k in range(1,7):
        p0,p1=P[i][k],P[i+1][k]; m0,m1=tan(i,k)*h,tan(i+1,k)*h
        h00=2*u**3-3*u**2+1; h10=u**3-2*u**2+u; h01=-2*u**3+3*u**2; h11=u**3-u**2
        out.append(h00*p0+h10*m0+h01*p1+h11*m1)
    return tuple(out)
# glow: torque path (cool -> hot as torque is multiplied) + illustrative ring-pin load
GROUPS=[ # centre time, colour, objects
 (9.8,(0.10,0.35,1.0),["input_shaft","key","shaft_bearing_inner"]),
 (11.0,(0.05,0.80,1.0),["cam_a","cam_b"]+[f"cam_bearing_{p}_{s}" for p in ("inner","cage","outer") for s in "ab"]),
 (12.4,(0.55,1.0,0.25),["disc_a","disc_b"]),
 (13.6,(1.0,0.62,0.05),[f"output_pin_{i}" for i in range(6)]+[f"output_roller_{i}" for i in range(6)]),
 (14.6,(1.0,0.22,0.02),["output_flange","output_cap","hub_bearing_inner"])]
def pulse(t,c):  # rises before the camera arrives, holds dim after, fades out by 15.8
    up=ss((t-(c-0.9))/0.9); down=1-ss((t-15.0)/0.8)
    peak=1-0.0*abs(t-c); near=math.exp(-((t-c)/0.7)**2)
    return min(1,(0.25*up+0.6*near))*down
def pin_load(t):  # illustrative sin-law: load peaks 90 deg from the eccentric direction, zero on the eccentric axis
    env_=keys([(0,0),(15.6,0),(16.6,1),(24.4,1),(25.4,0),(30,0)],t); a=math.radians(alpha(t)); out=[]
    for i in range(12): out.append(0.7*env_*abs(math.sin(2*math.pi*i/12-a))**2)
    return out
def apply(t):
    ex=keys(EXPLODE,t); c=keys(CASING_K,t)
    ctrl["input_rotation"]=alpha(t); ctrl["explode"]=ex; ctrl["cutaway"]=0.0; set_casing(c)
    for _,col,names in GROUPS:
        pass
    for ctime,col,names in GROUPS:
        w=pulse(t,ctime)
        for n in names: bpy.data.objects[n].color=(col[0],col[1],col[2],w)
    for i,w in enumerate(pin_load(t)): bpy.data.objects[f"ring_pin_{i}"].color=(1.0,0.55,0.1,w)
    r,yaw,z,tz,lens,fs=cam_at(t); y=math.radians(yaw)
    co.location=(r*math.cos(y),r*math.sin(y),z); tgt.location=(0,0,tz); cam.lens=lens; cam.dof.aperture_fstop=fs
    ctrl.update_tag(); bpy.context.view_layer.update()
    return dict(ex=ex,c=c,a=alpha(t),rpm_out=60*speed(t))
co.parent=None; co.animation_data_clear(); ctrl.animation_data_clear(); tgt.animation_data_clear()
for k in list(co.constraints): co.constraints.remove(k)
tc=co.constraints.new('TRACK_TO'); tc.target=tgt; tc.track_axis='TRACK_NEGATIVE_Z'; tc.up_axis='UP_Y'
cam.type='PERSP'; cam.dof.use_dof=True; cam.dof.focus_object=tgt
SCENES=[("1 Assembled, running",0,3),("2 Exploded view",3,8),("3 Power path",8,15),("4 Assembled, casing off",15,21),("5 Accelerate and decelerate",21,25),("6 Reassemble",25,30)]
PREVIEW_T=([float(x) for x in os.environ['ONLY'].split(',')] if os.environ.get('ONLY') else [0.0,2.5, 4.2,6.5, 8.3,9.8,11.0,12.4,13.6,14.7, 17.0,19.0,20.7, 21.8,22.9,24.4, 25.8,27.0,28.4,30.0])
if MODE=="preview":
    out=os.path.join(OUT,"v3_preview"); os.makedirs(out,exist_ok=True)
    sc.render.resolution_x,sc.render.resolution_y=960,540; ev.taa_render_samples=24
    for t in PREVIEW_T:
        info=apply(t); sc.render.filepath=os.path.join(out,"t%05.2f.png"%t); bpy.ops.render.render(write_still=True)
        print("PV",t,info)

# ---------------- clip: sample every frame, key everything linearly so EEVEE motion blur sees the real motion
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
def tf(f): return (f-1)/(NF-1)*T          # frame 1 -> t=0, frame NF -> t=30 (exactly the first-frame state)
def casing_visible(margin=0.0):
    """Any casing bbox corner inside the camera frustum?"""
    bad=[]
    for o in CASING:
        for k in o.bound_box:
            p=world_to_camera_view(sc,co,o.matrix_world@Vector(k))
            if -margin<=p.x<=1+margin and -margin<=p.y<=1+margin and p.z>0: bad.append(o.name); break
    return bad
if MODE in ("check","clip"):
    sc.frame_start,sc.frame_end=1,NF; sc.render.fps=FPS
    worst={}; 
    for f in range(1,NF+1):
        t=tf(f); info=apply(t)
        if info["c"]>=0.98:
            b=casing_visible(0.02)
            if b: worst[f]=b
    print("CHECK casing visible while removed (c>=0.98) in",len(worst),"frames", list(worst.items())[:6])
if MODE=="clip":
    glow_objs=[bpy.data.objects[n] for _,_,ns in GROUPS for n in ns]+[bpy.data.objects[f"ring_pin_{i}"] for i in range(12)]
    ctrl.animation_data_clear(); co.animation_data_clear(); tgt.animation_data_clear()
    for f in range(1,NF+1):
        apply(tf(f))
        for pr in ("input_rotation","explode"): ctrl.keyframe_insert(f'["{pr}"]',frame=f)
        for e in (EB,EH,EF): e.keyframe_insert("location",frame=f)
        for o in glow_objs: o.keyframe_insert("color",frame=f)
        co.keyframe_insert("location",frame=f); tgt.keyframe_insert("location",frame=f)
        cam.keyframe_insert("lens",frame=f); cam.dof.keyframe_insert("aperture_fstop",frame=f)
    sc.render.use_motion_blur=True; sc.render.motion_blur_shutter=0.5; ev.motion_blur_max=48
    sc.render.resolution_x,sc.render.resolution_y=1920,1080; ev.taa_render_samples=48
    fdir=os.environ.get("FRAMEDIR") or os.path.join(OUT,"v3_frames"); os.makedirs(fdir,exist_ok=True)
    sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'; sc.render.use_overwrite=False
    sc.render.filepath=os.path.join(fdir,"f_")
    if os.environ.get("FRAMES"): a_,b_=os.environ["FRAMES"].split("-"); sc.frame_start,sc.frame_end=int(a_),int(b_)
    bpy.ops.render.render(animation=True); print("RENDERED",sc.frame_start,sc.frame_end)
