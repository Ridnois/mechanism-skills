# Mechanism skills for Claude Code

Three skills that take a real mechanism from research to finished media.

| Skill | What it does |
|---|---|
| `mechanism-studio` | Orchestrator. Runs the other two in order with approval gates, a status file and machine-safety checks. |
| `accurate-3d-modeling` | Sourced research, parts breakdown, parametric FreeCAD CAD, verified kinematics, rigged Blender model. |
| `mechanism-animation-render` | Storyboard, no-pop casing removal, power-path glow, loopable speed profile, transparent RGBA, chunked render, vertical re-cut. |

Built and tested on a cycloidal drive (11:1, two discs, 12 ring pins). The animation scripts are templates: copy them and edit the project-specific blocks named in each file header. They have not yet been run on a second mechanism.

## Install
```sh
cp -r skills/* ~/.claude/skills/
```
Needs FreeCAD (`freecadcmd`), Blender 5.x, ffmpeg and Python 3 with numpy and Pillow.
