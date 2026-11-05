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


## Private log classification and derived-image licensing control

[CI42045389521](https://github.com/alwansan/raf/actions/runs/42045389521) **FAILED again** at the pre-NUnit Unity stage after passing all source-free Python tests, confirming the base image lacks `libvulkan.so.1` and lavapipe ICD, rebuilding the derived image, and successful `vulkaninfo --summary` inside that image. This run added an explicitly redacted private GameCI CLI diagnostic. The actual marker included:

```json
{"process_exit_zero":false,"observation_categories":{"cli_unknown_argument":false,"docker_container_launch_error":false,"docker_image_unavailable":false,"explicit_custom_image_mentioned":false,"gameci_test_command_mentioned":true,"test_report_path_seen":true,"unity_csharp_or_shader_error_category":false,"unity_license_failure_category":true,"unity_runner_start_seen":true,"unity_vulkan_device_error_category":false},"unity_vulkan_editor_or_fft_numeric_parity_proven":false}
```

Unity's `editmode-results.xml` was absent, as in the first image-overlay run. The `unity_license_failure_category=true` marker is **only a whitelisted textual symptom**, not proof that the account or license secret is invalid; supported GameCI activation on the original standard image succeeded in CI42011720822. Likewise `unity_runner_start_seen=true` is a log category, not proof the real Unity process fully initialized. No original assets were hydrated or private log lines exported.

To isolate whether **this custom image itself** changes the licensing path, T1 added a second independent synthetic control in the same workflow: a two-test base Unity project that uses the **same disposable Mesa customImage but neither `-force-vulkan` nor `--dockerEnv`**. It must pass real Unity EditMode 2/2 via the already tested private `t1_gameci_private_result_gate` before the stricter Vulkan three-test stage can run. The new [CI42046073285](https://github.com/alwansan/raf/actions/runs/42046073285) is **queued at this checkpoint**. If the custom-image no-Vulkan control fails too, the immediate next action is image/activation compatibility diagnosis, not shader investigation; if it passes but forced Vulkan fails, the difference is the Vulkan launch or driver-enabled Unity runtime. No new private game source consumed.


## Same derived image licensed Unity 2/2 PASS; only combined Vulkan flags pre-NUnit fail (CI42046073285)

[CI42046073285](https://github.com/alwansan/raf/actions/runs/42046073285) completed **FAILURE** overall with a new important independent positive control:

- The identical temporary Mesa/lavapipe custom Unity2021 `t1-fft-unity2021-lavapipe:local` image **ACTUALLY RAN licensed Unity2021** and passed both original-free `T1SourceFreeEditorTest` NUnit tests **2/2** without `--dockerEnv` or `--customParameters`. This is a real supported GameCI CLI run, not merely a Docker/Vulkaninfo check. The strict private XML gate emitted `all_expected_tests_passed=true`, `observed_test_case_count=2`, `failed_count=0`, `synthetic_unity_compute_test_verified=true`. Therefore **the custom image's Mesa package addition does not by itself break activation or normal synthetic ComputeShader import**; do not claim it cannot use the existing credentials.
- On that SAME custom image, when invoking `--dockerEnv=VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json` **together with** `--customParameters=-force-vulkan`, GameCI again exited before producing NUnit XML. Its private Boolean-category report showed `process_exit_zero=false`, `unity_license_failure_category=true` as a textual category, but `cli_unknown_argument=false`, `docker_container_launch_error=false`, `docker_image_unavailable=false`, `unity_csharp_or_shader_error_category=false`. This does **not** prove the secret/account lacks entitlement: the immediate no-flag activation succeeded. It also does not establish which of the two Vulkan flags caused the pre-NUnit exit. No game data acquired.
- A true experiment to resolve this two-factor confound was prepared at [commit5e19fe8](https://github.com/alwansan/raf/commit/5e19fe8f445cf353e583ec868eb19c77fbefab44) in the existing isolated, source-free workflow. With the same image, same Unity version and exact GameCI CLI SHA, the workflow now runs an **ICD environment-only** two-NUnit license/control test (no forced API) and—only after that succeeds—a separate **`-force-vulkan` only** 3-NUnit Vulkan+64-texel arithmetic test (no injected ICD environment). The previously reproduced combination is deliberately not repeated. Real run [CI42047391061](https://github.com/alwansan/raf/actions/runs/42047391061) was queued at this checkpoint; **neither factor can yet be identified as the cause**.

Keep the combined-flags failure and original OpenGLCore FFT numeric mismatch as negative evidence, original FFT import/Dispatch scoped successes intact, WATER-001 OPEN, global NOT_READY0/3. There is no Android/Adreno/rendered water or new APK acceptance from this image test.


## Conclusive orthogonal source-free flag isolation — CI42047391061

[CI42047391061](https://github.com/alwansan/raf/actions/runs/42047391061) **FAILED overall at the intentional strict forced-Vulkan gate**, but its independently separated controls resolve the previous A/B ambiguity:

1. The original UnityCI image again had **no `libvulkan.so.1` loader** and no lavapipe ICD. The disposable derived Mesa image **built successfully**, and `VK_ICD_FILENAMES=... vulkaninfo --summary` **succeeded** inside it.
2. **Same disposable derived image, NO additional Vulkan flags**: actual licensed Unity2021.3.45f2 source-free NUnit **2/2 PASS**; fixed exact private XML acceptance `all_expected_tests_passed=true`, `process_exit_zero=true`.
3. **Same derived image, ONLY `--dockerEnv=VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json`**, with **NO `-force-vulkan`**: real licensed Unity2021 source-free NUnit **2/2 PASS**, exact private XML gate, exit0; safe marker `RAFT_T1_MESA_VULKAN_ENVONLY license_2of2=true icd_env_injected=true force_flag=false original_data=false`. Merely injecting the loader/ICD environment does **NOT** reproduce the startup failure.
4. **Same derived image, ONLY `--customParameters=-force-vulkan`**, with **NO explicit injected ICD environment**: GameCI exited **before NUnit XML**, strict gate emitted `invalid_or_missing_test_report=true`; classifier `process_exit_zero=false`, `unity_license_failure_category=true` as a *textual marker*, no unknown-argument, Docker launch/image-pull or C#/shader error category. **No synthetic Vulkan GPU dispatch or original FFT was exercised** in this last stage.

Hence the immediate regression **correlates with Unity's explicit forced Vulkan launch path**, not with the additional Mesa driver package, the custom image itself, or `VK_ICD_FILENAMES` alone. It remains unknown whether the command-line flag is not honoured, the Editor backend cannot establish a usable Vulkan graphics device, or Unity's licensing/graphics init fails in that particular combination; a regex license text-category is **not conclusive root cause** and does not contradict genuine Unity activation in the no-flag and env-only controls. The old combined-flags failure is reproduced by the forced flag alone, and therefore should **not** be rerun without a new discriminating change.

This result closes only the source-free **flag isolation diagnostic**, not the original-water FFT issue. The real numeric OpenGLCore-vs-source-DXBC Vulkan mismatch from [CI42025620147](https://github.com/alwansan/raf/actions/runs/42025620147) remains **63/64** written pixels outside tolerance in pass0 and **31/32** in pass1. No original author Unity multi-variant kernel mappings, output parity, Android/Adreno/device pixels or native playable APK are proven. WATER-001 **OPEN**, readiness **NOT_READY 0/3**.

**Next distinct engineering target:** inspect the Unity Editor GPU backend startup conditions (DISPLAY/X11, Vulkan surface/instance extensions, container GPU devices, Vulkan ICD/loader init) with a bounded source-free classifier, or investigate already measured OpenGLCore shader arithmetic and sampled-coordinate differences using private original pair capture/instrumentation. Do **not** reacquire the 116MB original FFT just to repeat `-force-vulkan` failure; no need to change native game shaders, audio, Settings or touch.
