#!/usr/bin/env bash
set -euo pipefail
root="$1"
tmp="$2/split-probe"
mkdir -p "$tmp/classes" "$tmp/dex" "$tmp/lib/arm64-v8a"
[[ $(adb shell getprop ro.product.cpu.abi | tr -d '\r') == x86_64 ]]
ndk_version=27.2.12479018
cc="$root/ndk/$ndk_version/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android24-clang"
if [[ ! -x "$cc" ]]; then sdkmanager "ndk;$ndk_version"; fi
test -x "$cc"
"$cc" -std=c11 -Wall -Wextra -Werror -O2 -fPIC -shared qa/arm_probe.c -o "$tmp/lib/arm64-v8a/libraftarmprobe.so"
readelf -h "$tmp/lib/arm64-v8a/libraftarmprobe.so" | tee evidence/split-elf.txt
grep -E 'Machine: *AArch64' evidence/split-elf.txt
bt="$root/build-tools/35.0.0"
jar="$root/platforms/android-35/android.jar"
javac --release 8 -cp "$jar" -d "$tmp/classes" qa/ArmProbe.java
"$bt/d8" --min-api 24 --lib "$jar" --output "$tmp/dex" "$tmp/classes/org/raft/qa/armfixture/ArmProbe.class"
"$bt/aapt2" link -o "$tmp/base-unsigned.apk" -I "$jar" --manifest qa/ArmManifest.xml
(cd "$tmp/dex"; zip -q "$tmp/base-unsigned.apk" classes.dex)
"$bt/aapt2" link -o "$tmp/split-unsigned.apk" -I "$jar" --manifest qa/ArmSplitManifest.xml
(cd "$tmp"; zip -q "$tmp/split-unsigned.apk" lib/arm64-v8a/libraftarmprobe.so)
for kind in base split; do
  "$bt/zipalign" -f 4 "$tmp/$kind-unsigned.apk" "$tmp/$kind-aligned.apk"
  "$bt/apksigner" sign --ks "$2/fixture.jks" --ks-pass pass:android --out "$tmp/$kind.apk" "$tmp/$kind-aligned.apk"
done
cert=$("$bt/apksigner" verify --print-certs "$tmp/base.apk" | sed -n 's/^Signer #1 certificate SHA-256 digest: //p')
# Trusted record generated from synthetic CI-owned inputs only.
python3 - "$tmp" "$cert" <<'PY'
import hashlib, json, pathlib, sys
p=pathlib.Path(sys.argv[1])
record={"package":"org.raft.qa.armfixture","version_code":"1","signer_sha256":[sys.argv[2]],
        "abi":"arm64-v8a","require_native":True,"files":[]}
for name, split in [("base.apk",None),("split.apk","config.arm64_v8a")]:
    record["files"].append({"path":name,"split":split,"sha256":hashlib.sha256((p/name).read_bytes()).hexdigest()})
(p/"pinned.json").write_text(json.dumps(record,indent=2))
for name, modify in [
    ("wrong_hash", lambda r: r["files"][0].update(sha256="0"*64)),
    ("wrong_signer", lambda r: r.update(signer_sha256=["0"*64])),
    ("missing_base", lambda r: r["files"].pop(0)),
    ("wrong_abi", lambda r: r.update(abi="x86_64")),
]:
    copy=json.loads(json.dumps(record))
    modify(copy)
    (p/(name+".json")).write_text(json.dumps(copy))
PY
cp "$tmp/pinned.json" evidence/split-pinned-synthetic.json
python3 qa/audit_apk_set.py --manifest "$tmp/pinned.json" --build-tools "$bt" | tee evidence/split-audit.json
for bad in wrong_hash wrong_signer missing_base wrong_abi; do
  if python3 qa/audit_apk_set.py --manifest "$tmp/$bad.json" --build-tools "$bt" > "evidence/split-reject-$bad.txt" 2>&1; then
    echo "Negative control unexpectedly passed: $bad"
    exit 2
  fi
  grep -F APK_SET_REJECTED "evidence/split-reject-$bad.txt"
done
adb install-multiple --abi arm64-v8a "$tmp/base.apk" "$tmp/split.apk" | tee evidence/split-install.txt
tr -d '\r' < evidence/split-install.txt | grep -Fx Success
adb shell pm path org.raft.qa.armfixture | tee evidence/split-installed-paths.txt
[[ $(grep -c '^package:' evidence/split-installed-paths.txt) == 2 ]]
adb shell dumpsys package org.raft.qa.armfixture | grep -E 'primaryCpuAbi=|splitNames=|nativeLibraryDir=' | tee evidence/split-installed-abi.txt
grep -Eq 'primaryCpuAbi=arm64-v8a([[:space:]]|$)' evidence/split-installed-abi.txt
adb logcat -d -s RaftQaFixture AndroidRuntime > evidence/gles-fixture-before-split.log
adb logcat -c
timeout -k 5s 45s adb shell am start -W -n org.raft.qa.armfixture/.ArmProbe | tee evidence/split-launch.txt
grep -qi '^Status: ok' evidence/split-launch.txt
for i in {1..40}; do
  adb logcat -d -s RaftQaArm:I AndroidRuntime:E > evidence/split-runtime.log
  if grep -Fq 'ARM64_JNI_PASS results=17,18' evidence/split-runtime.log; then
    cat evidence/split-runtime.log
    sleep 1
    adb exec-out screencap -p > evidence/split-screen.png
    printf 'SPLIT_INSTALL_JNI_PASS controls=4 abi=translated_arm64\n' | tee evidence/split-result.txt
    exit 0
  fi
  sleep 1
done
cat evidence/split-runtime.log
exit 2
