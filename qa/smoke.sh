#!/usr/bin/env bash
set -euo pipefail
mkdir -p evidence
exec > >(tee evidence/runner.log) 2>&1
phase=setup
cleanup() {
  local rc=$?
  printf "phase=%s\nexit=%s\n" "$phase" "$rc" > evidence/result.txt
  if [[ -n "${emu_pid:-}" ]]; then
    if [[ $(timeout -k 2s 5s adb get-state 2>/dev/null || true) == device ]]; then
      timeout -k 2s 15s adb logcat -d -s RaftQaFixture AndroidRuntime > evidence/fixture.log 2>&1 || true
    fi
    kill "$emu_pid" 2>/dev/null || true
    if (( rc != 0 )); then tail -n 100 evidence/emulator.log || true; fi
  fi
}
trap cleanup EXIT
abi=${EXPECTED_ABI:?}
case "${abi}:$(uname -m)" in x86_64:x86_64|arm64-v8a:aarch64) ;; *) echo "Host ABI mismatch"; exit 2;; esac
phase=sdk-discovery
root=${ANDROID_SDK_ROOT:-${ANDROID_HOME:-/usr/local/lib/android/sdk}}
if [[ ! -d "$root" ]]; then
  echo "Android SDK unavailable for $(uname -m) at $root"
  ls -l /dev/kvm || true
  exit 2
fi
export ANDROID_HOME="$root" ANDROID_SDK_ROOT="$root"
export PATH="$root/cmdline-tools/latest/bin:$root/platform-tools:$root/emulator:$PATH"
phase=sdk
image="system-images;android-35;google_apis;$abi"
sdkmanager "$image" 'platforms;android-35' 'build-tools;35.0.0' platform-tools emulator
phase=host-dependencies
if [[ "$abi" == x86_64 ]]; then
  qemu="$root/emulator/qemu/linux-x86_64/qemu-system-x86_64"
  test -x "$qemu"
  ldd "$qemu" > evidence/qemu-dependencies-before.txt
  if grep -Fq 'libpulse.so.0 => not found' evidence/qemu-dependencies-before.txt; then
    sudo apt-get update -qq
    sudo apt-get install -y --no-install-recommends libpulse0
  fi
  ldd "$qemu" > evidence/qemu-dependencies-after.txt
  # Raw QEMU ldd does not inherit the emulator launcher's bundled library paths.
  # Retain diagnostics, but use the supported launcher as the execution gate.
  if grep -F '=> not found' evidence/qemu-dependencies-after.txt; then
    echo 'Raw QEMU loader diagnostic only; checking official emulator launcher'
  fi
fi
phase=emulator-launcher
emulator -version 2>&1 | tee evidence/emulator-version.txt
phase=kvm
test -c /dev/kvm
if [[ ! -r /dev/kvm || ! -w /dev/kvm ]]; then
  sudo setfacl -m "u:$(id -un):rw" /dev/kvm
fi
test -r /dev/kvm && test -w /dev/kvm
emulator -accel-check 2>&1 | tee evidence/kvm-check.txt
phase=avd-creation
avd_root=$(mktemp -d)
export ANDROID_USER_HOME="$avd_root/.android"
export ANDROID_EMULATOR_HOME="$ANDROID_USER_HOME"
export ANDROID_SDK_HOME="$avd_root"
export ANDROID_AVD_HOME="$ANDROID_USER_HOME/avd"
mkdir -p "$ANDROID_AVD_HOME"
printf 'no\n' | avdmanager create avd -n raft-qa -k "$image" -p "$ANDROID_AVD_HOME/raft-qa.avd" --force 2>&1 | tee evidence/avd-create.txt
ls -la "$ANDROID_AVD_HOME" | tee evidence/avd-directory.txt
test -s "$ANDROID_AVD_HOME/raft-qa.ini"
test -s "$ANDROID_AVD_HOME/raft-qa.avd/config.ini"
emulator -list-avds | tee evidence/avd-list.txt
grep -Fx raft-qa evidence/avd-list.txt
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
deadline=$((SECONDS + 420))
booted=0
while (( SECONDS < deadline )); do
  if ! kill -0 "$emu_pid" 2>/dev/null; then
    echo 'Emulator process exited before Android booted'
    exit 2
  fi
  if [[ $(timeout -k 2s 8s adb get-state 2>/dev/null || true) == device ]]; then
    if [[ $(timeout -k 2s 8s adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true) == 1 ]]; then
      booted=1
      break
    fi
  fi
  sleep 2
done
if (( booted != 1 )); then
  echo 'Android boot deadline exceeded'
  exit 2
fi
echo 'Android reported sys.boot_completed=1'
guest=$(adb shell getprop ro.product.cpu.abi | tr -d '\r')
[[ "$guest" == "$abi" ]]
{ uname -m; adb shell getprop ro.build.fingerprint; adb shell getprop ro.build.version.sdk; adb shell getprop ro.product.cpu.abilist; adb shell wm size; adb shell pm list features | grep -i vulkan || true; } > evidence/device.txt
timeout 15 adb shell cmd gpu vkjson > evidence/vulkan-reported.json 2>&1 || true
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
adb shell input keyevent KEYCODE_WAKEUP
adb shell wm dismiss-keyguard
phase=install
adb install "$tmp/fixture.apk" | tee evidence/install.txt
tr -d '\r' < evidence/install.txt | grep -Fx Success
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
printf 'gles=passed\nabi=%s\n' "$guest" > evidence/gles-result.txt
if [[ "${VULKAN_PROBE:-false}" == true ]]; then
  phase=vulkan-transfer-readback
  bash qa/vulkan_probe.sh "$root" "$tmp"
fi
if [[ "${CAPTURE_VIDEO:-false}" == true ]]; then
  phase=video
  bash qa/capture_video.sh "$x" "$y" "$tmp/venv/bin/python"
fi
if [[ "${ARM_TRANSLATION_PROBE:-false}" == true || "${ARM_VULKAN_PROBE:-false}" == true ]]; then
  phase=arm64-translation
  bash qa/arm_probe.sh "$root" "$tmp"
fi
if [[ "${ARM_SPLIT_PROBE:-false}" == true ]]; then
  phase=arm64-split-install
  bash qa/split_probe.sh "$root" "$tmp"
fi
phase=passed
echo "Synthetic emulator checks passed for $guest"
