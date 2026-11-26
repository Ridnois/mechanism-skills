#!/bin/zsh
# Usage: preflight.sh <need_disk_GB> [need_ram_MB]   - exit 1 if the machine can't take the job. Run before any long render/encode.
need_gb=${1:-10}; need_mb=${2:-3000}
free_gb=$(df -BG --output=avail . | tail -1 | tr -dc 0-9)
avail_mb=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
echo "disk free ${free_gb} GB (need ${need_gb}), RAM available ${avail_mb} MB (need ${need_mb}), swap used $(free -m | awk '/Swap/{print $3}') MB"
[ $free_gb -ge $need_gb ] && [ $avail_mb -ge $need_mb ] || { echo "PREFLIGHT FAILED"; exit 1; }
