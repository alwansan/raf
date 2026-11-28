#!/usr/bin/env bash
set -euo pipefail
x="$1"
y="$2"
python="$3"
if ! command -v ffmpeg >/dev/null || ! command -v ffprobe >/dev/null; then
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends ffmpeg
fi
remote=/data/local/tmp/raft-qa.mp4
adb shell rm -f "$remote"
timeout -k 5s 25s adb shell screenrecord --time-limit 10 --bit-rate 1000000 "$remote" > evidence/screenrecord.log 2>&1 &
recorder=$!
sleep 3
kill -0 "$recorder"
adb shell input tap "$x" "$y"
wait "$recorder"
adb pull "$remote" evidence/fixture.mp4
adb shell rm -f "$remote"
test -s evidence/fixture.mp4
"$python" qa/check_video.py
