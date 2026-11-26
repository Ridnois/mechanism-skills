---
name: mechanism-animation-render
description: Turn a finished, rigged Blender mechanism (one control empty, drivers) into a storyboarded, loopable technical animation - exploded view, power-path fly-through with glow, casing removal with no pop-in, speed ramps, transparent RGBA output, vertical 9:16 re-cut - and render it without crashing the machine. Use after accurate-3d-modeling, or for any request to animate, showcase or render a mechanism, gearbox, actuator or machine.
---

# Mechanism animation and render

Distilled from the cycloidal-drive project (v1 5 s hero clip, v2 polish, v3 30 s transparent loop, vertical re-cut).
Scripts live in `scripts/`. They are templates: copy, then edit the project-specific blocks named in each header.

## Order of work (do not skip the approval gate)
1. **Preflight**: `scripts/preflight.sh <GB> <MB>` (disk and RAM). A render once filled the disk and wrote 0-byte PNGs, and a long render plus three parallel encodes ran the machine out of RAM. Estimate frames x size first (1080p RGBA PNG ~1 MB, 1080x1920 ~2 MB).
2. **Storyboard first, no full render**: build the scene table, render ~20 low-res key stills (960x540, 16-24 samples, ~2 s each), composite them on a dark backdrop, look at them yourself, fix, then publish a storyboard page (Artifact) with per-scene description, timing, speed curve, legend, and an explicit "decisions for you" list. Wait for "go".
3. **Check scripts before the render**: casing-visibility check on all frames (seconds), loop-closure arithmetic, one hard frame at full quality.
4. **Render in chunks** (`render_chunks.sh`), resumable, RAM/disk guard, peak RSS logged.
5. **Validate every frame** (PIL `load()`, size, mode) - a crash leaves one truncated PNG that ffmpeg silently drops (899 of 900 frames in the movie). Re-render only bad frames.
6. **Encode one at a time** (`encode_deliverables.sh`): ProRes 4444 alpha master, VP9 alpha WebM, opaque H.264 MP4 over a gradient for platforms without alpha. Decode a frame of each alpha file to prove alpha survived.
7. **Look at frames of the final movie** (contact sheet), and say what you did not look at.

## Design rules that paid off
- **One control empty** drives everything (input angle, explode, ...). Animate by keying that control, not individual parts.
- **State function of time**: write `apply(t)` that sets every channel analytically (camera spline, explode keys, glow, casing). Previews, checks and the clip all call it, so what you approved is what renders.
- **Camera**: cylindrical waypoints (radius, yaw, z, target z, lens, f-stop) with a cardinal Hermite spline (zero end tangents), target empty + Track-To, DOF on the target. Same waypoint at t=0 and t=T closes the loop. Unwrapped, increasing yaw avoids spin-backs.
- **Shot-size lesson**: size the zoom from the measured subject width/height per scene. Fixed crops cut the assembled part; exploded stacks are narrow and tall.
- **Seamless loop** = same camera pose + every part back at its start phase. For a ratio-N mechanism the input angle must end at a multiple of N x 360 deg. Solve it with a speed profile: integrate speed numerically and pick one free level (e.g. the slow-section speed) so the revolutions are an integer. Key frame k at t=(k-1)/(n-1)*T so the last frame is exactly the first state, then drop the duplicate last frame for platform loops.
- **No pop-in/pop-out**: never toggle visibility on screen. Remove casing by parenting it to empties that fly away along collision-free paths and park out of frame; then run a frustum check (`world_to_camera_view` on bbox corners) on every frame where it is parked. The check caught a parked cover visible behind the axis from the opposite camera side: choose a park direction no camera looks through. Check geometry for the path (a bore smaller than a cap blocks axial removal -> leave sideways from the exploded state, where it is clear).
- **Show energy/torque flow**: glow on parts via Object Info colour into Principled emission (set every object colour alpha 0 at start, key colour per frame on glow objects; one hook patches all materials at runtime, no rebuild). Order the glow along the power path with a cool-to-warm ramp. Label any physical model that is only illustrative (the ring-pin load sin-law was) and ask the user whether to keep it.
- **Aliasing**: spec speeds can alias (60 rpm out of an 11:1 drive = 132 deg of input per frame at 30 fps). Warn before rendering, use a 180 deg shutter, offer the slower alternative.
- **Motion blur needs real motion data**: key every frame linearly. Frame-handler-driven values give blur only on the camera. At a hard cut the blur blends old/new camera: re-render the first frame after each cut with `NOBLUR`.
- **Transparent output**: `film_transparent`, RGBA PNG. The HDRI still lights and reflects. Unsaturated HDRIs are safer: a blue studio HDRI turned steel solid blue, so a Hue/Saturation node at ~0.3 on the env fixed it. Lights go down (x0.35-0.45) when the HDRI is strong. Desaturate before tuning anything else.
- **Metal look**: area lights near flat faces blow them out; a specular mirror of the key light (camera at the mirror angle) does too. Turn the view 25 deg, lower exposure/lights in cut scenes, test the worst frame.
- **Vertical 9:16 from finished frames**: `scripts/vertical_vse.py` builds a Video Sequencer scene from the PNG frames (fit ORIGINAL, per-scene keyed scale, view transform Standard or colours shift, alpha-over, RGBA PNG out). Mitchell filter. It is a re-crop: tell the user about upscale softness and empty bands; a native vertical re-render is the better fix.
- **Blender traps**: `bpy.ops.render.render(animation=True)` in one process accumulates memory (sequencer caches too): chunk it. No FFMPEG output in this build: PNG + system ffmpeg. VSE API in 5.x: `sequence_editor.strips.new_image`, `transform.filter` enums are AUTO/NEAREST/BILINEAR/CUBIC_MITCHELL/CUBIC_BSPLINE/BOX. Keep `use_overwrite=False` for resume.
- **Shell traps**: never `kill $(pgrep -f pattern)` or `pgrep -f` waits from a command line containing the pattern (it matches itself: exit 144). Never run a long job as `( ... ) &` in a tool call; run it as the background job and wait for the notification.

## Reporting
State: frame count and validity, which checks ran and their results, what was only spot-checked, what is illustrative vs sourced, file sizes and locations, and the open decisions (speed alias, illustrative physics, disk).
