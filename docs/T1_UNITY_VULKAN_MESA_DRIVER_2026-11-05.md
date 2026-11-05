# T1 — source-free Unity 2021 Vulkan ICD / Mesa lavapipe container isolation

Session: `20261105T142000Z-T1-chat-lavapipe-unity` (origin chat), 5 November 2026.
Issue WATER-001 OPEN; overall readiness NOT_READY 0/3.

## Confirmed pre-experiment facts

- Original-SHA-authentic source-derived FFT pair0/1 executed two passes on Unity 2021's OpenGLCore with GPU writes [CI42019283679](https://github.com/alwansan/raf/actions/runs/42019283679); this was not numeric parity.
- Against independent source-original DXBC software Vulkan on identical input bytes, Unity OpenGLCore still differed **63/64 pass0** and **31/32 pass1** written texels [CI42025620147](https://github.com/alwansan/raf/actions/runs/42025620147). No coverage/nonfinite divergence.
- DXBC-derived HLSL and original SPIR-V match **64/64 and 32/32** when both execute on the same lavapipe Vulkan device [CI42030877911](https://github.com/alwansan/raf/actions/runs/42030877911).
- Unity's OpenGLCore input upload/identity copy matched exactly 32768/32768 RGBAfloat texels for each original paired image [CI42033745802](https://github.com/alwansan/raf/actions/runs/42033745802).
- A synthetic editor test with the documented `-force-vulkan` flag on the existing GameCI UnityCI container [CI42042230791](https://github.com/alwansan/raf/actions/runs/42042230791) **FAILED** and reported `runtime_api=other_backend`; an independent stricter source-free 3-test synthetic Vulkan float arithmetic probe [CI42042650298](https://github.com/alwansan/raf/actions/runs/42042650298) **FAILED**, 2/3 actual Unity2021 tests passed, the explicit Vulkan/math test failed. No Raft original bytes acquired by either. Exact missing driver vs Editor fallback remains unknown.

## Distinct executable experiment

[CI42044388619](https://github.com/alwansan/raf/actions/runs/42044388619) from `.github/workflows/raft-t1-sourcefree-mesa-vulkan-overlay.yml` is **running at initial checkpoint**, not a proven result. It:

1. Audits the exact `unityci/editor:ubuntu-2021.3.45f2-linux-il2cpp-3` Linux image for `libvulkan.so.1` and lavapipe ICD existence without Unity license, game assets or logs.
2. Builds a **temporary local Docker image** from this exact original image that installs Ubuntu `libvulkan1`, `mesa-vulkan-drivers` and `vulkan-tools`, without pushing/publishing a new image.
3. Requires an actual `vulkaninfo --summary` success with `VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json`, proving a Vulkan loader can enumerate under the disposable container (not Unity yet).
4. Runs *the same exact strict authored synthetic Unity test* under GameCI CLI v0.1.72 SHA256 `1de550a620ee92e05e920b6db7d431621440b60b2577f04b4a997dc92a58cb0a` with `--customImage=t1-fft-unity2021-lavapipe:local`, `--dockerEnv=VK_ICD_FILENAMES=...` and `--customParameters=-force-vulkan`. Requires **3/3 expected real NUnit tests**, including `SystemInfo.graphicsDeviceType == Vulkan` and actual 64/64 mathematically known synthetic GPU outputs; otherwise fails closed.
5. Captures all Docker pull/build/Unity/test raw logs to temporary runner-local files, prints only bounded boolean/count control messages and disposes of the test project, container layer and logs. No original FFT file, private HLSL, user device data, Unity credential value or native game/build request is read or changed. Source-free Python guard regressions must pass before any Unity step.

The direct GameCI CLI flag `--customParameters` and `--dockerEnv` were confirmed against version **v0.1.72 source**, and `-force-vulkan` is an officially documented Unity2021 Editor flag. A successful software-Vulkan Editor synthetic test would only prove the **source-free runner environment** can execute that graphics backend; it cannot prove real FFT numeric parity, original author/runtime kernel mapping or Adreno phone rendering. Only then is a SHA-authenticated full original-pair Unity Vulkan/CPU Vulkan comparison justified. A failed layer install or Vulkan loader test may instead motivate tracing actual translated HLSL arithmetic under the existing OpenGLCore backend.

Status here remains **WAITING_CI**. WATER-001 OPEN, NOT_READY0/3, latest real game Raft APK86; protect audio/Settings, touch deferred, no cancellation of other jobs.
