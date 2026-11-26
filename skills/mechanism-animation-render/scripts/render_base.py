"""Render stills / clip from blender/cycloidal_drive.blend.
blender -b blender/cycloidal_drive.blend --python blender/render.py -- <shot> [shot...]
shots: front side top iso iso_cutaway cutaway_back exploded detail_cap clip_hero   (env FRAMES="a-b" renders a subset of the clip; env TEST=1 = 1 frame)"""
import bpy, sys, os, math, subprocess
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(bpy.data.filepath))); OUT=os.path.join(ROOT,"renders"); os.makedirs(OUT,exist_ok=True)
shots=sys.argv[sys.argv.index("--")+1:]
sc=bpy.context.scene; ctrl=bpy.data.objects["CTRL"]; sc.render.engine='BLENDER_EEVEE'
ev=sc.eevee; ev.use_raytracing=True; ev.ray_tracing_method='SCREEN'; ev.use_shadows=True; ev.shadow_ray_count=2; ev.shadow_step_count=8
ev.use_fast_gi=True; ev.fast_gi_method='AMBIENT_OCCLUSION_ONLY' if hasattr(ev,'fast_gi_method') else None
sc.render.film_transparent=False; sc.render.use_motion_blur=False
sc.view_settings.view_transform='AgX'
for look in ('AgX - Medium High Contrast','Medium High Contrast'):
    try: sc.view_settings.look=look; break
    except TypeError: pass
sc.view_settings.exposure=-0.45
# ---- world: studio HDRI lights/reflects, dark gradient is what the camera sees
hdri=os.path.join(bpy.utils.system_resource('DATAFILES'),"studiolights","world","studio.exr")
w=bpy.data.worlds.new("W"); w.use_nodes=True; sc.world=w; nt=w.node_tree; nt.nodes.clear()
out=nt.nodes.new("ShaderNodeOutputWorld"); mix=nt.nodes.new("ShaderNodeMixShader"); nt.links.new(mix.outputs[0],out.inputs[0])
env=nt.nodes.new("ShaderNodeTexEnvironment"); env.image=bpy.data.images.load(hdri); bgh=nt.nodes.new("ShaderNodeBackground"); bgh.inputs["Strength"].default_value=float(os.environ.get("HDRI_STR","0.5"))
nt.links.new(env.outputs[0],bgh.inputs[0])
tcw=nt.nodes.new("ShaderNodeTexCoord"); grad=nt.nodes.new("ShaderNodeTexGradient"); grad.gradient_type='SPHERICAL'
cr=nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color=(0.012,0.014,0.018,1); cr.color_ramp.elements[1].color=(0.06,0.07,0.085,1)
nt.links.new(tcw.outputs["Window"],grad.inputs["Vector"]); nt.links.new(grad.outputs["Fac"],cr.inputs["Fac"])
bgd=nt.nodes.new("ShaderNodeBackground"); nt.links.new(cr.outputs[0],bgd.inputs[0])
lp=nt.nodes.new("ShaderNodeLightPath"); nt.links.new(lp.outputs["Is Camera Ray"],mix.inputs["Fac"]); nt.links.new(bgh.outputs[0],mix.inputs[1]); nt.links.new(bgd.outputs[0],mix.inputs[2])
def light(name,kind,loc,energy,size=0.3,color=(1,1,1)):
    l=bpy.data.lights.new(name,kind); l.energy=energy*float(os.environ.get("LIGHT_SCALE","1")); l.color=color
    if kind=='AREA': l.size=size
    o=bpy.data.objects.new(name,l); sc.collection.objects.link(o); o.location=loc
    o.rotation_euler=(Vector((0,0,0.0))-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return o
light("key",'AREA',(0.22,-0.26,0.30),8,0.30,(1.0,0.97,0.92)); light("rim",'AREA',(-0.2,0.28,-0.22),6.5,0.35,(0.75,0.85,1.0)); light("back",'AREA',(-0.28,0.20,-0.26),17,0.55)
# ---- camera
cam=bpy.data.cameras.new("Cam"); co=bpy.data.objects.new("Cam",cam); sc.collection.objects.link(co); sc.camera=co
tgt=bpy.data.objects.new("CamTarget",None); sc.collection.objects.link(tgt)
cam.sensor_width=36
def aim(loc,target=(0,0,0.0),ortho=None,lens=70,dof=0.0):
    co.parent=None; co.animation_data_clear(); co.location=loc; tgt.location=target
    for c in list(co.constraints): co.constraints.remove(c)
    tc=co.constraints.new('TRACK_TO'); tc.target=tgt; tc.track_axis='TRACK_NEGATIVE_Z'; tc.up_axis='UP_Y'
    if ortho: cam.type='ORTHO'; cam.ortho_scale=ortho; cam.dof.use_dof=False
    else:
        cam.type='PERSP'; cam.lens=lens
        if dof: cam.dof.use_dof=True; cam.dof.focus_object=tgt; cam.dof.aperture_fstop=dof
        else: cam.dof.use_dof=False
def setup(inp=0.0,expl=0.0,cut=0.0):
    ctrl.animation_data_clear(); ctrl["input_rotation"]=inp; ctrl["explode"]=expl; ctrl["cutaway"]=cut; ctrl.update_tag(); bpy.context.view_layer.update()
def still(name,samples=96,res=(1920,1080)):
    name=name+os.environ.get("SUFFIX","")
    if os.environ.get("SUFFIX"): res=(960,540); samples=16
    sc.render.resolution_x,sc.render.resolution_y=res; ev.taa_render_samples=samples
    sc.render.image_settings.file_format='PNG'; sc.render.filepath=os.path.join(OUT,name+".png"); bpy.ops.render.render(write_still=True); print("RENDERED",name)
def ease(fc):
    for k in fc.keyframe_points: k.interpolation='BEZIER'
def fcurves(idb):
    a=idb.animation_data.action
    return a.layers[0].strips[0].channelbags[0].fcurves
for s in shots:
    if s=="front":   setup(); aim((0,0,0.9),(0,0,0.0),ortho=0.1); still("front")
    elif s=="side":  setup(); aim((0.9,0,0.0035),(0,0,0.0035),ortho=0.13); still("side")
    elif s=="top":   setup(); aim((0,0.9,0.0035),(0,0,0.0035),ortho=0.13); still("top")
    elif s=="iso":   setup(); aim((0.24,-0.24,0.2),(0,0,0.0035),lens=80,dof=11); still("iso")
    elif s=="iso_cutaway": setup(cut=1.0); aim((0.2,-0.25,-0.17),(0,0,0.0),lens=75,dof=11); still("iso_cutaway")
    elif s=="cutaway_back": setup(inp=25,cut=1.0); aim((0.09,0.06,-0.55),(0,0,0.0),lens=210,dof=16); still("cutaway_back")
    elif s=="exploded": setup(expl=1.0); aim((0.62,-0.5,0.07),(0,0,0.002),lens=85); still("exploded",res=(1800,1100))
    elif s=="detail_cap": setup(); aim((0.07,-0.09,0.075),(0,0,0.0265),lens=85,dof=9); still("detail_cap")
    elif s=="clip_hero":
        # 5 s @ 60 fps = 300 frames. Exploded->assembled while running; camera dollies in and orbits; cutaway (back cover hidden, housing quadrant cut)
        setup(inp=0.0,expl=1.0,cut=1.0); sc.render.fps=60; sc.frame_start,sc.frame_end=1,300
        ctrl["input_rotation"]=0.0; ctrl.keyframe_insert('["input_rotation"]',frame=1); ctrl["input_rotation"]=1440.0; ctrl.keyframe_insert('["input_rotation"]',frame=300)
        for fc in fcurves(ctrl):
            if 'input_rotation' in fc.data_path:
                for k in fc.keyframe_points: k.interpolation='LINEAR'
        ctrl["explode"]=1.0; ctrl.keyframe_insert('["explode"]',frame=1); ctrl.keyframe_insert('["explode"]',frame=24)
        ctrl["explode"]=0.0; ctrl.keyframe_insert('["explode"]',frame=150)
        for fc in fcurves(ctrl):
            if 'explode' in fc.data_path: ease(fc)
        rig=bpy.data.objects.new("CamRig",None); sc.collection.objects.link(rig)
        co.parent=rig; co.animation_data_clear()
        for c in list(co.constraints): co.constraints.remove(c)
        tc=co.constraints.new('TRACK_TO'); tc.target=tgt; tc.track_axis='TRACK_NEGATIVE_Z'; tc.up_axis='UP_Y'
        cam.type='PERSP'; cam.lens=55; cam.dof.use_dof=True; cam.dof.focus_object=tgt; cam.dof.aperture_fstop=9.0
        def key(ob,path,idx,frame,val):
            setattr_=getattr(ob,path); setattr_[idx]=val; ob.keyframe_insert(path,index=idx,frame=frame)
        key(co,"location",0,1,0.27); key(co,"location",1,1,0.20); key(co,"location",2,1,-0.48)
        key(co,"location",0,300,0.135); key(co,"location",1,300,0.10); key(co,"location",2,300,-0.255)
        key(tgt,"location",2,1,-0.012); key(tgt,"location",2,300,0.0)
        key(rig,"rotation_euler",2,1,math.radians(-28)); key(rig,"rotation_euler",2,300,math.radians(18))
        for ob in (co,tgt,rig):
            for fc in fcurves(ob): ease(fc)
        sc.render.use_motion_blur=True; sc.render.motion_blur_shutter=0.4; ev.motion_blur_max=40
        sc.render.resolution_x,sc.render.resolution_y=1920,1080; ev.taa_render_samples=48
        fdir=os.path.join(OUT,"clip_hero_frames"); os.makedirs(fdir,exist_ok=True)
        sc.render.image_settings.file_format='PNG'; sc.render.filepath=os.path.join(fdir,"f_")
        if os.environ.get("TEST"): sc.frame_start=sc.frame_end=int(os.environ["TEST"]); sc.render.filepath=os.path.join(OUT,"test_frame_")
        elif os.environ.get("FRAMES"): a,b=os.environ["FRAMES"].split("-"); sc.frame_start,sc.frame_end=int(a),int(b)
        bpy.ops.render.render(animation=True); print("RENDERED clip frames",sc.frame_start,sc.frame_end)
