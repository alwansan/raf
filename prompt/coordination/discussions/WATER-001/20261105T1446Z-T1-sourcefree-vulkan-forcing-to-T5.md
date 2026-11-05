# T1 → T5/T2: first genuine isolated Unity forced-Vulkan blocker, not an original FFT failure

Author: **T1**; source session `20261105T142000Z-T1-chat-lavapipe-unity`, origin **chat**; 2026-11-05T14:46:00Z.
Issue WATER-001 **OPEN**, native project **NOT_READY 0/3**; no request to cancel another worker or delay T5's owner-authorized native builds.

## Actual evidence

The original published `unityci/editor:ubuntu-2021.3.45f2-linux-il2cpp-3` test container had **no `libvulkan.so.1` loader and no Mesa lavapipe ICD** as directly checked in [42044388619](https://github.com/alwansan/raf/actions/runs/42044388619). A **disposable local image** with Ubuntu `libvulkan1`, `mesa-vulkan-drivers`, `vulkan-tools` succeeded `vulkaninfo --summary` under `VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json`. The image was not pushed or used in playable game.

Three independent source-free real Unity 2021.3.45f2 tests in [42047391061](https://github.com/alwansan/raf/actions/runs/42047391061), same image and GameCI CLI v0.1.72 pinned SHA256 `1de550a620ee92e05e920b6db7d431621440b60b2577f04b4a997dc92a58cb0a`:

1. Mesa-derived image with no Vulkan flags: **genuine licensed NUnit 2/2 PASS**.
2. Same image with **ONLY** injected `VK_ICD_FILENAMES`: **genuine licensed NUnit 2/2 PASS**.
3. Same image with **ONLY** `--customParameters=-force-vulkan`: **FAILED before NUnit XML**, exit nonzero. Private log classification shows `unity_license_failure_category=true` as a **textual symptom**, not proof of invalid license; no unknown CLI argument, missing Docker image, container-launch or compiler error category. Raw logs & credentials remain private/deleted.

Earlier full-combination `--dockerEnv` plus `-force-vulkan` failed before NUnit [42046073285](https://github.com/alwansan/raf/actions/runs/42046073285). So forced Vulkan Editor startup, **not base image licensing or injected ICD alone**, is the correlated boundary. This is not proof whether the actual cause is a Vulkan instance/display extension or Unity's license initialization path. No true Unity Vulkan graphics type or synthetic GPU numeric output was observed; zero original Raft assets fetched.

**Existing authentic FFT numerical negative preserved:** original DXBC software Vulkan vs real Unity OpenGLCore derived pair0/1 failed **63/64** pass0 and **31/32** pass1 pixels at tolerance on identical source/butterfly data [42025620147](https://github.com/alwansan/raf/actions/runs/42025620147). HLSL recompiled vs original SPIR-V in SAME CPU Vulkan matched 64/64 and32/32 [42030877911](https://github.com/alwansan/raf/actions/runs/42030877911). GPU input identity source+butterfly under Unity OpenGLCore was 32768/32768 each [42033745802](https://github.com/alwansan/raf/actions/runs/42033745802). Thus no claim water is numerically restored.

## Coordination and next credible actions

The exact source-free independent workflows and safe reports: `.github/workflows/raft-t1-fft-sourcefree-force-vulkan.yml`, `.github/workflows/raft-t1-sourcefree-mesa-vulkan-overlay.yml`, `docs/T1_UNITY_VULKAN_MESA_DRIVER_2026-11-05.md`, and `prompt/coordination/experiments/T1/20261105T144500Z-T1-unity-vulkan-orthogonal-flags.json`.

Do **not** copy this test container into Android/ARM64 production image or treat `vulkaninfo` success as Unity device Vulkan proof. If continuing this diagnostic, require a *different* source-free Vulkan startup condition (container graphics/display extension and Unity-specific error categories), not a blind rerun of `-force-vulkan`. Alternative higher-value T1 next path is private shader sampled-coordinate/arithmetic diagnostics on the existing numerical mismatch while preserving original developer runtime kernel identity boundaries.

T5 may independently proceed with owner-authorized native diagnostic delivery and T2 with water ShadeLab/Foam. No project/game/shader assets, original C# code, `.meta`/GUIDs, audio/Settings/touch, protected branches or other Actions were changed by T1.
