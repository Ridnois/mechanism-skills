#!/bin/zsh
# Usage: encode_deliverables.sh <frames_dir> <pattern e.g. f_%04d.png> <fps> <WxH> <out_basename> [bg0=14181e bg1=232b35]
# One encode at a time, 2 threads (three parallel encodes + a render exhausted RAM). Alpha masters + an opaque MP4 for platforms without alpha.
d=$1; pat=$2; fps=$3; size=$4; out=$5; c0=${6:-14181e}; c1=${7:-232b35}
ffmpeg -y -loglevel error -threads 2 -f lavfi -i "gradients=s=$size:c0=0x$c0:c1=0x$c1:x0=0:y0=0:x1=0:y1=${size#*x}:r=$fps:n=2" -framerate $fps -i $d/$pat -filter_complex "[0][1]overlay=shortest=1,format=yuv420p" -c:v libx264 -profile:v high -preset slow -crf 17 -maxrate 14M -bufsize 28M -r $fps -g $((fps*2)) -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart -an ${out}_opaque.mp4
ffmpeg -y -loglevel error -threads 2 -framerate $fps -i $d/$pat -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -vendor apl0 ${out}_alpha.mov
ffmpeg -y -loglevel error -threads 2 -framerate $fps -i $d/$pat -c:v libvpx-vp9 -pix_fmt yuva420p -crf 20 -b:v 0 -auto-alt-ref 0 -row-mt 1 ${out}_alpha.webm
for f in ${out}_opaque.mp4 ${out}_alpha.mov ${out}_alpha.webm; do echo $f; ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,duration -of csv=p=0 $f; done
