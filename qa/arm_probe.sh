#!/usr/bin/env bash
set -euo pipefail
root="$1"
tmp="$2/arm-translation"
mkdir -p "$tmp/classes" "$tmp/dex" "$tmp/apk/lib/arm64-v8a"
[[ $(uname -m) == x86_64 ]]
[[ $(adb shell getprop ro.product.cpu.abi | tr -d '\r') == x86_64 ]]
{
  for prop in ro.product.cpu.abi ro.product.cpu.abilist ro.dalvik.vm.native.bridge ro.dalvik.vm.isa.arm64; do
    printf '%s=' "$prop"
    adb shell getprop "$prop" | tr -d '\r'
  done
} | tee evidence/arm-translation-environment.txt
grep -E '^ro.product.cpu.abilist=.*arm64-v8a' evidence/arm-translation-environment.txt

ndk_version=27.2.12479018
cc="$root/ndk/$ndk_version/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android24-clang"
if [[ ! -x "$cc" ]]; then sdkmanager "ndk;$ndk_version"; fi
test -x "$cc"
if [[ "${ARM_VULKAN_PROBE:-false}" == true ]]; then
  "$cc" -std=c11 -Wall -Wextra -Werror -O2 -fPIC -shared -DRAFT_ANDROID_JNI_LOG \
    qa/arm_probe.c qa/vulkan_probe.c -lvulkan -llog -o "$tmp/apk/lib/arm64-v8a/libraftarmprobe.so"
  readelf -d "$tmp/apk/lib/arm64-v8a/libraftarmprobe.so" | tee evidence/arm-vulkan-elf-dependencies.txt
  grep -Fq '[libvulkan.so]' evidence/arm-vulkan-elf-dependencies.txt
else
  "$cc" -std=c11 -Wall -Wextra -Werror -O2 -fPIC -shared qa/arm_probe.c -o "$tmp/apk/lib/arm64-v8a/libraftarmprobe.so"
fi
readelf -h "$tmp/apk/lib/arm64-v8a/libraftarmprobe.so" | tee evidence/arm-elf.txt
grep -E 'Machine: *AArch64' evidence/arm-elf.txt

bt="$root/build-tools/35.0.0"
jar="$root/platforms/android-35/android.jar"
javac --release 8 -cp "$jar" -d "$tmp/classes" qa/ArmProbe.java
"$bt/d8" --min-api 24 --lib "$jar" --output "$tmp/dex" "$tmp/classes/org/raft/qa/armfixture/ArmProbe.class"
"$bt/aapt2" link -o "$tmp/unsigned.apk" -I "$jar" --manifest qa/ArmManifest.xml
cp "$tmp/dex/classes.dex" "$tmp/apk/classes.dex"
(cd "$tmp/apk"; zip -q "$tmp/unsigned.apk" classes.dex lib/arm64-v8a/libraftarmprobe.so)
"$bt/zipalign" -f 4 "$tmp/unsigned.apk" "$tmp/aligned.apk"
"$bt/apksigner" sign --ks "$2/fixture.jks" --ks-pass pass:android --out "$tmp/armfixture.apk" "$tmp/aligned.apk"
{
  sha256sum "$tmp/armfixture.apk" "$tmp/apk/lib/arm64-v8a/libraftarmprobe.so"
  "$bt/apksigner" verify --print-certs "$tmp/armfixture.apk"
} > evidence/arm-apk-provenance.txt
unzip -Z1 "$tmp/armfixture.apk" | tee evidence/arm-apk-entries.txt
[[ $(grep -E '^lib/.*\.so$' evidence/arm-apk-entries.txt) == lib/arm64-v8a/libraftarmprobe.so ]]
"$bt/aapt2" dump badging "$tmp/armfixture.apk" > evidence/arm-apk-badging.txt
grep -Fx "native-code: 'arm64-v8a'" evidence/arm-apk-badging.txt
adb install --abi arm64-v8a "$tmp/armfixture.apk" | tee evidence/arm-install.txt
tr -d '\r' < evidence/arm-install.txt | grep -Fx Success
adb shell dumpsys package org.raft.qa.armfixture > "$tmp/package.txt"
grep -E 'primaryCpuAbi=|secondaryCpuAbi=|nativeLibraryDir=' "$tmp/package.txt" | tee evidence/arm-package-abi.txt
grep -Eq 'primaryCpuAbi=arm64-v8a([[:space:]]|$)' evidence/arm-package-abi.txt
adb logcat -d -s RaftQaFixture AndroidRuntime > evidence/gles-fixture-before-arm.log
adb logcat -c
args=()
if [[ "${ARM_VULKAN_PROBE:-false}" == true ]]; then args=(--ez vulkan true); fi
timeout -k 5s 45s adb shell am start -W -n org.raft.qa.armfixture/.ArmProbe "${args[@]}" | tee evidence/arm-launch.txt
grep -qi '^Status: ok' evidence/arm-launch.txt
for i in {1..75}; do
  timeout -k 2s 10s adb logcat -d -s RaftQaArm:I RaftQaArmVk:I AndroidRuntime:E > evidence/arm-runtime.log
  if grep -Fq ARM64_VULKAN_FAIL evidence/arm-runtime.log; then
    cat evidence/arm-runtime.log
    exit 2
  fi
  if grep -Fq 'ARM64_JNI_PASS results=17,18' evidence/arm-runtime.log; then
    printf 'result=passed\nhost=x86_64\nguest=x86_64\napk_library=arm64-v8a\nscope=translated_arm64_jni_not_native_arm64_guest\n' > evidence/arm-translation-result.txt
    if [[ "${ARM_VULKAN_PROBE:-false}" == true ]]; then
      if ! grep -Fq 'ARM64_VULKAN_PASS pixels=32' evidence/arm-runtime.log; then
        sleep 1
        continue
      fi
      grep -F 'VK_DEVICE=' evidence/arm-runtime.log
      grep -F 'VK_FRAME_0_FIRST_RGBA=255,0,0,255' evidence/arm-runtime.log
      grep -F 'VK_FRAME_1_FIRST_RGBA=0,255,0,255' evidence/arm-runtime.log
      grep -F 'VULKAN_TRANSFER_READBACK_PASS pixels=32' evidence/arm-runtime.log
      printf 'result=passed\npixels=32\nscope=translated_arm64_vulkan_not_native_arm64_guest\n' | tee evidence/arm-vulkan-result.txt
    fi
    cat evidence/arm-runtime.log
    sleep 1
    adb exec-out screencap -p > evidence/arm-screen.png
    exit 0
  fi
  sleep 1
done
cat evidence/arm-runtime.log
exit 2
