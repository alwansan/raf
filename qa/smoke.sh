#!/usr/bin/env bash
set -euo pipefail
mkdir -p evidence
exec > >(tee evidence/runner.log) 2>&1
phase=setup
trap 'rc=$?; printf "phase=%s\nexit=%s\n" "$phase" "$rc" > evidence/result.txt; if [[ -n "${emu_pid:-}" ]]; then adb logcat -d -s RaftQaFixture AndroidRuntime > evidence/fixture.log 2>&1 || true; kill "$emu_pid" 2>/dev/null || true; fi' EXIT
abi=${EXPECTED_ABI:?}
case "${abi}:$(uname -m)" in x86_64:x86_64|arm64-v8a:aarch64) ;; *) echo "Host ABI mismatch"; exit 2;; esac
root=${ANDROID_SDK_ROOT:-${ANDROID_HOME:?}}
export PATH="$root/platform-tools:$root/emulator:$PATH"
phase=sdk
image="system-images;android-35;google_apis;$abi"
sdkmanager "$image" 'platforms;android-35' 'build-tools;35.0.0' platform-tools emulator
emulator -version
phase=kvm
test -c /dev/kvm
if [[ ! -r /dev/kvm || ! -w /dev/kvm ]]; then
  sudo setfacl -m "u:$(id -un):rw" /dev/kvm
fi
test -r /dev/kvm && test -w /dev/kvm
emulator -accel-check
printf 'no\n' | avdmanager create avd -n raft-qa -k "$image" --force
phase=build-fixture
bt="$root/build-tools/35.0.0"
jar="$root/platforms/android-35/android.jar"
tmp=$(mktemp -d)
mkdir "$tmp/classes" "$tmp/dex"
javac --release 8 -cp "$jar" -d "$tmp/classes" qa/Probe.java
"$bt/d8" --min-api 23 --lib "$jar" --output "$tmp/dex" "$tmp/classes/org/raft/qa/fixture/Probe.class"
"$bt/aapt2" link -o "$tmp/unsigned.apk" -I "$jar" --manifest qa/AndroidManifest.xml
(cd "$tmp/dex"; zip -q "$tmp/unsigned.apk" classes.dex)
"$bt/zipalign" -f 4 "$tmp/unsigned.apk" "$tmp/aligned.apk"
keytool -genkeypair -keystore "$tmp/fixture.jks" -storepass android -keypass android -alias fixture -keyalg RSA -keysize 2048 -validity 30 -dname 'CN=Ephemeral QA Fixture' >/dev/null 2>&1
"$bt/apksigner" sign --ks "$tmp/fixture.jks" --ks-pass pass:android --out "$tmp/fixture.apk" "$tmp/aligned.apk"
{ sha256sum "$tmp/fixture.apk"; "$bt/apksigner" verify --print-certs "$tmp/fixture.apk"; } > evidence/artifact-provenance.txt
phase=boot
emulator -avd raft-qa -port 5554 -no-window -no-audio -no-boot-anim -no-snapshot -gpu swiftshader -accel on > evidence/emulator.log 2>&1 &
emu_pid=$!
export ANDROID_SERIAL=emulator-5554
timeout 300 adb wait-for-device
for i in {1..180}; do
  [[ $(adb shell getprop sys.boot_completed | tr -d '\r') == 1 ]] && break
  kill -0 "$emu_pid"
  sleep 2
done
[[ $(adb shell getprop sys.boot_completed | tr -d '\r') == 1 ]]
guest=$(adb shell getprop ro.product.cpu.abi | tr -d '\r')
[[ "$guest" == "$abi" ]]
{ uname -m; adb shell getprop ro.build.version.sdk; adb shell getprop ro.product.cpu.abilist; adb shell wm size; adb shell pm list features | grep -i vulkan || true; } > evidence/device.txt
timeout 15 adb shell cmd gpu vkjson > evidence/vulkan-reported.json 2>&1 || true
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
adb shell input keyevent KEYCODE_WAKEUP
adb shell wm dismiss-keyguard
phase=install
adb install "$tmp/fixture.apk" | tee evidence/install.txt
grep -Fx Success evidence/install.txt
adb logcat -c
adb shell am start -W -n org.raft.qa.fixture/.Probe | tee evidence/launch.txt
grep -qi '^Status: ok' evidence/launch.txt
wait_frame() {
  for i in {1..25}; do
    adb logcat -d -s RaftQaFixture:I > "$tmp/frame.log"
    grep -Fq "$1" "$tmp/frame.log" && return
    sleep 1
  done
  return 1
}
phase=screenshot
wait_frame FRAME_BASELINE
sleep 1
adb exec-out screencap -p > evidence/baseline.png
python3 -m venv "$tmp/venv"
"$tmp/venv/bin/python" -m pip -q install 'Pillow==11.3.0'
read -r x y < <("$tmp/venv/bin/python" -c 'from PIL import Image; i=Image.open("evidence/baseline.png"); print(i.width//2, i.height//2)')
adb shell input tap "$x" "$y"
wait_frame FRAME_FLIPPED
sleep 1
adb exec-out screencap -p > evidence/tapped.png
"$tmp/venv/bin/python" qa/check_pixels.py
grep -F 'GL_RENDERER=' "$tmp/frame.log" > evidence/gles-renderer.txt
grep -Fq TOUCH_ACCEPTED "$tmp/frame.log"
if [[ "${CAPTURE_VIDEO:-false}" == true ]]; then
  phase=video
  adb shell screenrecord --time-limit 10 /data/local/tmp/raft-qa.mp4 &
  recorder=$!
  sleep 2
  adb shell input tap "$x" "$y"
  wait "$recorder"
  adb pull /data/local/tmp/raft-qa.mp4 evidence/fixture.mp4
fi
phase=passed
