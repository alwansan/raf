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


## First real image/loader result and next bounded diagnostics

[CI42044388619](https://github.com/alwansan/raf/actions/runs/42044388619) **COMPLETED FAILURE** at its Unity-run stage, with several independently useful actual earlier steps:

- Actual original UnityCI 2021.3.45f2 `linux-il2cpp-3` Docker image inspection: `baseline_vulkan_loader=false` and `baseline_mesa_lavapipe_icd=false`. This directly explains why forcing Vulkan on the unmodified image was not justified as a Vulkan backend test.
- Disposable derived image `apt-get install libvulkan1 mesa-vulkan-drivers vulkan-tools` **BUILT SUCCESSFULLY**. Inside it, `VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json vulkaninfo --summary` **EXITED SUCCESSFULLY**, so the isolated container exposes a software Vulkan loader/ICD. This proves a Vulkan loader can run in the container, **not** that Unity can render through it.
- The subsequent `game-ci test --docker --customImage=t1-fft-unity2021-lavapipe:local --dockerEnv=VK_ICD_FILENAMES=... --customParameters=-force-vulkan` exited before publishing `editmode-results.xml`. The safe gate emitted `RAFT_T1_UNITY_VULKAN_SOURCEFREE invalid_or_missing_test_report=true`. Because all raw CLI logs were private/deleted as designed, the immediate cause (CLI argument vs Docker startup vs Unity startup) could **not be established from this run**. Do not claim Vulkan passed, computed a synthetic texel, or that generated FFT was the cause. No proprietary source/asset fetched.
- Cleanup was successful; the derived image was never uploaded or installed in the playable game.

To discriminate the remaining **pre-NUnit** failure without publishing raw Unity/credential logs, T1 added `scripts/t1_unity_vulkan_cli_failure_classifier.py` and six adversarial synthetic controls. They only emit whitelisted private-log message-presence categories (`cli_unknown_argument`, `docker_image_unavailable`, `docker_container_launch_error`, `unity_runner_start_seen`, `unity_license_failure_category`, `unity_vulkan_device_error_category`, `unity_csharp_or_shader_error_category`, and `explicit_custom_image_mentioned`) and an exit status boolean. They cannot establish a Vulkan backend by themselves. [Follow-up CI42045389521](https://github.com/alwansan/raf/actions/runs/42045389521) is **in progress** at this checkpoint on source `40a66ba28`; check its bounded diagnostic result before changing image flags or original shader code.

This removes the first environment unknown (missing loader and ICD in the original image), but leaves Unity/CLI execution under the temporary overlay unknown. WATER-001 remains OPEN and project NOT_READY0/3. No native APK/OBB/XAPK or Adreno/source parity evidence from these runs.
