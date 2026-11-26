---
name: mechanism-studio
description: Orchestrator for the full path from "a real mechanism" to finished media. Runs accurate-3d-modeling (research, parts, CAD, verified kinematics, rigged Blender model) and then mechanism-animation-render (storyboard, approval, checks, chunked render, alpha/vertical deliverables) in order, with approval gates, a project status file and machine-safety checks. Use when the request is to model AND animate/showcase a mechanism, gearbox, actuator, linkage or machine, or says "build it and make the video".
---

# Mechanism studio (orchestrator)

Runs two skills in order. Load each one with the Skill tool when its phase starts; do not re-explain them here.
- Phases 1-4 -> `accurate-3d-modeling`
- Phases 5-8 -> `mechanism-animation-render`
This skill owns only: the order, the gates, the status file, and the final report.

## 0. Intake (ask once, then proceed on defaults)
Collect in one message, with defaults stated so the user can just say "go":
- Object and target parameters (counts, diameters, ratio) and the **purpose** (technical animation, product shot, social, print).
- Deliverables: stills, clip length/fps/resolution, transparent (alpha) or opaque, vertical 9:16, loop, cutaway/exploded.
- Speed spec and whether the physics shown (glow, load) must be sourced or may be illustrative.
Defaults if unanswered: 1080p, 30 fps, 30 s, alpha master + opaque MP4, loop, exploded + power-path + casing-off scenes.
Scaffold: `scripts/new_project.sh <name>` creates the folder layout and `STATUS.md`.

## Phases and gates
Each gate = stop, show the evidence, wait for an explicit user answer. A background notification or silence is never approval.

| # | Phase | Skill | Output | Gate (user) |
|---|---|---|---|---|
| 1 | Research + specs | modeling | `research/specs.md` (every value SOURCED / DERIVED / ESTIMATED) | none, but unknown key specs -> ask |
| 2 | Breakdown | modeling | `parts.csv`, detail-level choices | **G1: approve parts + specs** |
| 3 | CAD + verify | modeling | per-part STEP/STL, `params.py`, kinematic check, solid interference at several poses incl. a sabotage self-test | none; report min clearance etc. |
| 4 | Blender model | modeling | rigged `.blend`, one control empty, mesh-vs-CAD volume check, asset QA | none; report counts and accepted warnings |
| 5 | Storyboard | animation | scene table, 20 key stills, storyboard page | **G2: approve scenes + decisions** |
| 6 | Pre-render checks | animation | frustum/pop check, loop arithmetic, speed-alias warning, 1 hard frame, `preflight.sh` | none |
| 7 | Render + validate | animation | chunked frames, every frame validated | **G3: "go"** (given at G2 or separately) |
| 8 | Encode + variants | animation | alpha MOV/WebM, opaque MP4, optional vertical | none; look at frames |

If the user says "go" at G2 and storyboard is unchanged, G3 is satisfied. If scenes changed after approval, ask again.

## Rules that span both skills
- **Single source of truth**: dimensions in `cad/params.py`, scenes in one table. A change re-runs from the earliest affected phase (`build.sh` for 3-4, previews for 5).
- **Machine safety before every heavy step** (phases 3, 7, 8): `scripts/preflight.sh` from the animation skill (disk, RAM, swap). If swap is mostly used, tell the user which processes hold memory and ask before stopping anything. Never kill services the user did not name.
- **Verify, then report only what you verified.** Say what was spot-checked and what was not. Mark illustrative physics as illustrative.
- **Loop closure and kinematic ratios are computed, not eyeballed.**
- **Keep the user informed on long jobs**: one line on what is running, then wait for the completion notification; do not poll.
- **Ask only at gates and for missing key specs.** Everything else uses the stated defaults.

## STATUS.md (kept current, one line per phase)
`phase | state (todo/doing/done/blocked) | evidence path | open decisions`. Update after each phase. On resume after a crash or context reset, read STATUS.md first and continue from the first non-done phase; resume renders from the first missing frame.

## Final report (always this shape)
1. What was built (parts count, key specs, ratio) and where (paths).
2. Verification results (numbers: min clearance, interference count, mesh volume error, frames validated, checks run).
3. Deliverables table (file, format, size, use).
4. Known limits and what was only spot-checked.
5. Open decisions / suggested next variant.
Then suggest skill updates if anything new was learned, and save reusable scripts.

## Variants (cheap once phases 1-4 are done)
Parameter family (ratio/count change -> rebuild), vertical or square re-cut, slower speed for aliasing, a second storyboard for the same model, STEP + BOM handoff.
