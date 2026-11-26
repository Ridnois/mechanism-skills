#!/bin/zsh
# Usage: render_chunks.sh <blend> <script.py> <first> <last> [chunk=75] [mode-args...]
# Renders FRAMES=a-b chunks, each in a fresh Blender (one long render grew past RAM and killed the system). Resumable: rerun with the first missing frame.
# Aborts if MemAvailable < 3000 MB or disk < 5 GB before a chunk. Prints peak RSS per chunk. Script must honour env FRAMES (a-b).
blend=$1; py=$2; a=$3; last=$4; n=${5:-75}; shift 5 2>/dev/null
while [ $a -le $last ]; do
  b=$((a+n-1)); [ $b -gt $last ] && b=$last
  avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); gb=$(df -BG --output=avail . | tail -1 | tr -dc 0-9)
  echo "chunk $a-$b  RAM ${avail}MB  disk ${gb}GB"
  [ $avail -lt 3000 ] && { echo "ABORT low RAM"; exit 3; }; [ $gb -lt 5 ] && { echo "ABORT low disk"; exit 4; }
  FRAMES=$a-$b /usr/bin/time -f "peakRSS_KB=%M" blender -b $blend --python $py -- "$@" 2>&1 | grep -E "RENDERED|peakRSS|Error|Traceback"
  a=$((b+1)); sleep 2
done; echo ALLDONE
