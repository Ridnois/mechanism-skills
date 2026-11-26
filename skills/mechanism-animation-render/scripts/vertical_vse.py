"""Vertical 9:16 adaptation of the finished 30 s clip, built in the Video Sequencer from the already rendered RGBA frames.
blender -b --python blender/vertical_vse.py        env FRAMES=a-b for a test range. Output: renders/v3_vertical_frames/ (RGBA PNG, 1080x1920, 30 fps)"""
import bpy, os, math
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
SRC=os.path.join(ROOT,"renders","v3_frames"); OUT=os.environ.get("VOUT") or os.path.join(ROOT,"renders","v3_vertical_frames"); os.makedirs(OUT,exist_ok=True)
N=899; FPS=30; W,H=1080,1920
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage=W,H,100; sc.render.fps=FPS
sc.frame_start,sc.frame_end=1,N
sc.view_settings.view_transform='Standard'; sc.view_settings.look='None'; sc.display_settings.display_device='sRGB'
sc.render.use_sequencer=True; sc.render.film_transparent=True
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'; sc.render.image_settings.color_depth='8'
se=sc.sequence_editor_create(); strips=se.strips if hasattr(se,"strips") else se.sequences
st=strips.new_image("clip",os.path.join(SRC,"f_0001.png"),channel=1,frame_start=1,fit_method='ORIGINAL')
for i in range(2,N+1): st.elements.append(f"f_{i:04d}.png")
st.blend_type='ALPHA_OVER'
try: st.transform.filter='CUBIC_MITCHELL'
except Exception as e: print("filter:",e)
# zoom set per scene from the subject width (assembled drive is ~980 px wide in the 1920 source, the exploded stack ~400 px); 1.0 at both ends so the loop matches
ZK=[(0,1.0),(2.8,1.0),(4.2,1.5),(5.2,1.8),(7.2,1.8),(9.0,1.25),(15.0,1.2),(16.6,1.1),(21.0,1.1),(22.0,1.0),(25.0,1.0),(26.3,1.6),(27.5,1.7),(28.8,1.2),(29.9,1.0)]
def ss(u): u=min(1,max(0,u)); return u*u*(3-2*u)
def zoom(t):
    for (t0,a),(t1,b) in zip(ZK,ZK[1:]):
        if t<=t1: return a+(b-a)*ss((t-t0)/(t1-t0))
    return ZK[-1][1]
for f in range(1,N+1):
    z=zoom((f-1)/FPS); st.transform.scale_x=z; st.transform.scale_y=z
    st.transform.keyframe_insert("scale_x",frame=f); st.transform.keyframe_insert("scale_y",frame=f)
for fc in sc.animation_data.action.fcurves if hasattr(sc.animation_data.action,"fcurves") else []:
    for k in fc.keyframe_points: k.interpolation='LINEAR'
sc.render.filepath=os.path.join(OUT,"v_")
if os.environ.get("FRAMES"): a,b=os.environ["FRAMES"].split("-"); sc.frame_start,sc.frame_end=int(a),int(b)
bpy.ops.render.render(animation=True); print("RENDERED",sc.frame_start,sc.frame_end)
