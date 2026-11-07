# 20261107T0615Z-T1-scheduled-source-sha-4c8f

- origin: scheduled
- identity: T1
- issue: WATER-001 (OPEN; NOT_READY 0/3)
- initial HEAD: d41b218e999bcee051a95ff0610f26f95ec0fb35
- latest observed HEAD: a739471fca8ed421652ca8ffc4e5096820d9d49e
- owner device baseline: [42058825739](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md). World entry/save/re-entry confirmed by owner from Artifact; publishing failed. Water pass and FFT kernel errors remain; no new device proof.
- work scope: prompt/coordination/work/WATER-001/20261107T0615Z-T1-scheduled-source-sha-4c8f.json
- hypothesis: cross-backend source_sha legitimately differs, but within one trace mixed compiled program source_sha invalidates a single immutable experiment.
- source fix: [3d26a3f](https://github.com/alwansan/raf/commit/3d26a3f109349e1c06309cedd05bd180338bdff9) adds source_sha to per-capture consistency check; [a739471](https://github.com/alwansan/raf/commit/a739471fca8ed421652ca8ffc4e5096820d9d49e) adds adversarial two-sided mixed-program regression.
- evidence boundary: source-only code change; no actual Vulkan/Unity paired captures, no FindKernel/Dispatch runtime proof, no GPU, device or water repair. New regression not yet executed in CI.
- next: run python3 -m unittest tests.test_t1_fft_trace_first_divergence_7c3a; compare real source-authenticated matched input traces; identify first numerical divergence; coordinate T2 bindings and T5 Unity proof. Do not repeat native build or alter T4/T5 scopes.
- origin constraints: branch feature/android-native-port only; no raw original data published; preserve GUID/.rgd and working audio/Settings.
