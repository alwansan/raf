#!/usr/bin/env bash
set -euo pipefail
root="$1"
tmp="$2"
ndk_version=27.2.12479018
ndk="$root/ndk/$ndk_version"
cc="$ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/x86_64-linux-android24-clang"
[[ $(uname -m) == x86_64 ]]
[[ $(adb shell getprop ro.product.cpu.abi | tr -d '\r') == x86_64 ]]
if [[ ! -x "$cc" ]]; then
  sdkmanager "ndk;$ndk_version"
fi
test -x "$cc"
{
  printf 'NDK=%s\n' "$ndk_version"
  "$cc" --version
} > evidence/vulkan-toolchain.txt
"$cc" -std=c11 -Wall -Wextra -Werror -O2 -fPIE -pie qa/vulkan_probe.c -lvulkan -o "$tmp/raft-qa-vk"
readelf -h "$tmp/raft-qa-vk" | tee evidence/vulkan-elf.txt
grep -Fq 'Advanced Micro Devices X86-64' evidence/vulkan-elf.txt
expected=$(sha256sum "$tmp/raft-qa-vk" | cut -d ' ' -f 1)
remote=/data/local/tmp/raft-qa-vk
adb push "$tmp/raft-qa-vk" "$remote"
adb shell chmod 700 "$remote"
actual=$(adb shell sha256sum "$remote" | tr -d '\r' | cut -d ' ' -f 1)
printf 'host=%s\nguest=%s\n' "$expected" "$actual" | tee evidence/vulkan-binary-sha256.txt
[[ "$actual" == "$expected" ]]
timeout -k 5s 90s adb shell "$remote" 2>&1 | tee evidence/vulkan-execution.txt
grep -Fx 'VK_FRAME_0_FIRST_RGBA=255,0,0,255' evidence/vulkan-execution.txt
grep -Fx 'VK_FRAME_1_FIRST_RGBA=0,255,0,255' evidence/vulkan-execution.txt
grep -Fx 'VULKAN_TRANSFER_READBACK_PASS pixels=32' evidence/vulkan-execution.txt
