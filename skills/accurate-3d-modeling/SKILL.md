---
name: accurate-3d-modeling
description: Pipeline for building dimensionally accurate, animation-ready 3D models of real-world objects (vehicles, machines, mechanisms, devices) from web research to parametric CAD to clean Blender assets. Use when asked to model a real object accurately, or to make CAD/Blender models of machines, vehicles or mechanisms.
---

# Accurate 3D modeling pipeline

Goal: produce dimensionally accurate, animation-ready 3D models of real-world objects
(vehicles, machines, mechanisms, devices, tools, furniture, architecture parts, etc.) for Blender.

## Tools on this machine
- FreeCAD: use it headless through Python (`freecadcmd` or the FreeCAD Python API) for all CAD work.
- SolidCraft: check what it is and how to drive it before relying on it.
- AutoRemesher: quad remeshing. Use its CLI if it has one, otherwise drive its GUI with agent-desktop.
- Blender: script it with `blender --background --python script.py`.
- agent-desktop (Vercel): operates desktop apps, available as the `agent-desktop` MCP server
  and as a CLI. Run `agent-desktop skills get desktop` and `agent-desktop skills get platform`
  before first use. Use it for GUI-only tools and for visual checks in the FreeCAD/Blender
  viewports. Prefer scripts for the actual modeling.
- Use WebSearch/WebFetch for research and download reference images with Bash.
At the start of a project, check that each tool works (version + entry point) and report
anything missing.

## Working folder
- Work relative to the current working directory (the folder Claude Code was opened in).
  Run `pwd` at the start and use it as the root. Never write outside it.
- Create the project folder as `./<project>/` with research/, cad/, meshes/, blender/, renders/
  inside. If the current folder is already empty or clearly set up for this project, work
  directly in it instead.
- Use relative paths in all scripts (resolve them from the script's own location or a
  PROJECT_ROOT variable), so the whole folder can be moved or shared and still work.

## Progress tracking
- Use a todo list for the six stages below, plus one item per part during CAD and topology,
  and keep it up to date.

## 1. Research
- Find the best available sources: official specs, datasheets, patents, manuals, technical
  drawings, standards, papers, blueprints, and photos from multiple angles.
- Write `research/specs.md` with every dimension and property the model needs. Give a source
  URL for each value and tag it SOURCED, DERIVED (show the math) or ESTIMATED (explain the
  method, e.g. scaled from a photo using a known dimension). Never present an estimate as a fact.
- Pick the right level of accuracy for the object: exact equations where the geometry is
  defined by them (gear teeth, cam profiles, threads, springs, airfoils, standard fasteners),
  and careful reference matching for freeform shapes (body panels, casings, ergonomic parts).
- Save reference images to `research/refs/`. Look at them (Read the image files) to pull out
  proportions and details.

## 2. Breakdown
- Write `parts.csv`: part name, quantity, parent assembly, material, whether it moves
  (fixed / rotates / slides / flexes / deforms), joint axis or pivot, and how it relates to
  other parts (ratios, linkages, limits).
- Choose the level of detail with me: what's modeled in full, what's simplified, what's left out.
- Show me the specs and part list and STOP. Wait for my approval before modeling.

## 3. CAD
- One parametric FreeCAD Python script per part in `cad/parts/`. Dimensions are named
  parameters at the top.
- Use the right modeling approach for each part: solids/sketches for prismatic parts,
  mathematical curves for functional profiles, lofts/surfaces for freeform shapes.
- Model each part in local coordinates with its origin on its pivot/joint.
- Write `cad/assembly.py`, which positions everything, checks for interference and correct
  fits/mating, and reports problems.
- Export each part as STEP (source of truth) and as a mesh into `meshes/`.
- Add a `build.sh` (or `Makefile`) that runs the whole chain: CAD → export → cleanup → Blender.

## 4. Topology for Blender
- Rigid parts: tessellate finely, then clean up (merge by distance, remove degenerate faces,
  weighted normals, mark sharp edges). Quads are not needed if the part never deforms.
- Parts that deform, get subdivided or are organic: quad remesh with AutoRemesher. Edge loops
  should follow the deformation and the silhouettes should match the CAD.
- Real-world scale in meters, +Z up, transforms applied, sensible polycounts (report them).

## 5. Blender assembly
- Name objects to match parts.csv, organize into collections, use a clean parent hierarchy,
  and put every pivot on its true joint axis.
- Rig the motion with constraints, drivers, bones, shape keys or lattices as appropriate, so
  a small number of controls moves everything with the correct real relationships and limits.
- Placeholder PBR materials. Include a test animation and an exploded-view toggle if it fits.
- Save `blender/<project>.blend`.

## 6. Verify
- Render front/side/top/iso (and exploded) views and a short motion clip into `renders/`.
- Read the rendered images and compare them against the references and specs: proportions,
  key dimensions, motion ranges, ratios/directions, no parts passing through each other.
  Fix what's wrong and render again before reporting.
- Report: what's accurate, what's estimated, known problems, and file locations.

## 7. Animate and deliver
- For a request that covers both modeling and animation, start with the `mechanism-studio` orchestrator, which runs this skill and `mechanism-animation-render` in order with approval gates.
- When the request includes an animation, showcase, exploded/cutaway or social-media render, continue with the `mechanism-animation-render` skill (storyboard approval, no-pop casing removal, power-path glow, loopable speed profile, transparent RGBA, chunked rendering with RAM/disk guards, vertical re-cut).

## Working style
- Re-runnable scripts: changing a parameter and re-running `build.sh` rebuilds everything downstream.
- When a key spec can't be found, ask me instead of guessing silently.
- After each project, suggest updates to this skill (lessons learned, reusable scripts such as
  gear generators, cleanup scripts, import/rig helpers), and save reusable scripts in a
  `scripts/` folder next to this SKILL.md.

## Lessons learned (cycloidal drive project) — read before the next mechanism
- **Define the kinematics once, check it three times**: analytic script over a full cycle (numpy, run in the *system* python, not FreeCAD) -> solid-boolean interference at several poses -> driver-evaluated Blender transforms vs the same formulas. Add a deliberate-sabotage self-test so you know the checker can fail.
- **Ideal-contact geometry has zero clearance** (e.g. hole Ø = roller Ø + 2e). Add a real running clearance (0.1 mm) and report the min clearance; tangent contact also makes OCC booleans flaky -> give rolling elements ~0.01 mm clearance.
- **FreeCAD/OCC booleans crash or hang occasionally**: run one pose per process, `timeout 240`, retry up to 3x, never let `set -e` + empty `grep` abort the build.
- **Never wrap a long build in `( ... ) &` inside a tool call** (it dies with the shell); run the build itself as the background job. Never `pkill -f <name>` from a command line containing that name.
- **Blender drivers**: simple-expression drivers zero any result < ~1e-4 (location in metres!). Do not drive small orbits as locations. Build them with parenting (child of the rotating shaft at its fixed eccentric offset) and drive only large-valued rotations. After changing a custom property from Python call `ctrl.update_tag()` before reading evaluated transforms. Animation on the property overrides test values -> `animation_data_clear()` in test scripts.
- **Blender 5.x**: no FFMPEG output in some builds -> render PNG frames and encode with system ffmpeg; action fcurves via `action.layers[0].strips[0].channelbags[0].fcurves`; `use_nodes` is deprecated but still works.
- **STL -> Blender**: STL has no shared verts: merge by ~0.002 mm (in scene units), delete degenerate faces, mark sharp by angle. A BSpline closing seam leaves tiny valid edges that QA flags as duplicates: accept with a reason.
- Reusable scripts in `scripts/`: `cycloid_profile.py` (pure-python epitrochoid-offset disc profile), `cycloid_check_profile.py`.

### Added after the v2 polish pass (chamfers, quad topology, 60 fps render)
- **Verify meshes against CAD volume, but know that `Shape.Volume` can be wrong** for BSpline-profile extrusions (-5.5 % here). Cross-check with an analytic area or a fine mesh before blaming the mesh pipeline.
- **STL -> clean quads recipe** (bmesh): merge verts at ~0.04 mm -> `dissolve_degenerate` -> `dissolve_limit(0.5deg)` -> triangulate n-gons with `EAR_CLIP` -> `beautify_fill(AREA)` -> `join_triangles(15deg/40deg)` -> sharp edges > 30deg. Skipping `beautify_fill` made sliver triangles 6x worse; 245k -> 78k polys, disc 47k tris -> 5.8k faces. Measure slivers (area/L^2) instead of trusting a count.
- **Chamfers via OCC** (`makeChamfer` on circle edges picked by radius) work on BSpline outlines too, but never chamfer a concave junction edge (it adds material: caused a bolt/cover interference the solid check caught).
- **EEVEE metal look**: area lights near the part are what blow out flat machined faces, not the HDRI. Use Blender's bundled `studiolights/world/studio.exr` at ~0.5 strength + 3 soft area lights at ~8-17 W, HDRI for lighting only (mix with a dark gradient for camera rays), AgX, exposure -0.45, keep the camera off the surface normal. Test one hard frame first; A/B lights vs HDRI with env-var overrides at 960x540.
- Procedural metal = Principled + object-space noise driving roughness (MapRange) and a tiny Bump; anodised = metallic 0.55-0.9 + coat 0.15-0.3, and keep the base colour saturated/dark or it washes to pastel.
- 5 s @ 60 fps 1080p EEVEE (raytracing, motion blur, DOF) = ~3-4 s/frame -> ~15 min; render PNG frames in one background job, encode with ffmpeg (`-crf 14 -pix_fmt yuv420p`), delete the frames.
- **zsh traps**: unmatched globs abort a whole `&&` chain (`rm -rf dir/x_*`), and `$var` is not word-split (`${=var}` or arrays).

### Added after the animation passes (storyboard, 30 s loop, transparent, vertical)
- Animation lessons live in the `mechanism-animation-render` skill: read it before rendering anything longer than a still.
- **Cutaways by visibility drivers pop**: prefer parts that fly out of frame on a path (and are parked far away) so nothing appears or vanishes; verify with a frustum check.
- **Check part-removal geometry from the CAD numbers** (bore radii, z extents at explode=1) before choreographing it.
- **Machine safety is part of the job**: check disk and RAM first, chunk long Blender renders, encode sequentially, validate every output frame.
