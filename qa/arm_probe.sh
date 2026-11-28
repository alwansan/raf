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
"$cc" -std=c11 -Wall -Wextra -Werror -O2 -fPIC -shared qa/arm_probe.c -o "$tmp/apk/lib/arm64-v8a/libraftarmprobe.so"
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
adb logcat -c
adb shell am start -W -n org.raft.qa.armfixture/.ArmProbe | tee evidence/arm-launch.txt
grep -qi '^Status: ok' evidence/arm-launch.txt
for i in {1..40}; do
  adb logcat -d -s RaftQaArm:I AndroidRuntime:E > evidence/arm-runtime.log
  if grep -Fq 'ARM64_JNI_PASS results=17,18' evidence/arm-runtime.log; then
    cat evidence/arm-runtime.log
    adb exec-out screencap -p > evidence/arm-screen.png
    printf 'result=passed\nhost=x86_64\nguest=x86_64\napk_library=arm64-v8a\nscope=translated_arm64_jni_not_native_arm64_guest\n' | tee evidence/arm-translation-result.txt
    exit 0
  fi
  sleep 1
done
cat evidence/arm-runtime.log
exit 2
