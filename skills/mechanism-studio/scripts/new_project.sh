#!/bin/zsh
# Usage: new_project.sh <project-name>   (run in the folder the work should live in)
n=$1; [ -z "$n" ] && { echo "usage: new_project.sh <name>"; exit 1; }
mkdir -p $n/{research/refs,cad/parts,cad/step,meshes,blender,renders}
cat > $n/STATUS.md <<EOT
# $n status
| phase | state | evidence | open decisions |
|---|---|---|---|
| 0 intake | todo | | |
| 1 research + specs | todo | research/specs.md | |
| 2 breakdown (G1) | todo | parts.csv | |
| 3 CAD + verify | todo | cad/ | |
| 4 Blender model | todo | blender/$n.blend | |
| 5 storyboard (G2) | todo | renders/*preview* | |
| 6 pre-render checks | todo | | |
| 7 render + validate (G3) | todo | renders/*_frames | |
| 8 encode + variants | todo | renders/ | |
EOT
echo "created $n/ with STATUS.md"; zsh ~/.claude/skills/mechanism-animation-render/scripts/preflight.sh 10 3000 || true
