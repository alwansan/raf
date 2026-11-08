# T1 chat session — 20261108T1836Z-T1-chat-water-startup-order-c5e7

**origin:** chat | **worker:** T1 | **issue:** WATER-001 (OPEN)
**resumed_from:** `20261108T1811Z-T1-chat-gles-gate-9d3f` and `20261108T1714Z-T1-scheduled-fft-shared-lab-b6d2`
**base_sha:** `d11d383f8bd222c7873f50a97d348d955998f44c`
**scope:** independently verify first water/FFT failures precede the world-loaded log milestone, using one pinned CL JSON summary and strict final counter consistency. No Raft game or Mini APK change.
**intended_files:** `scripts/t1_water_startup_order.py`, `tests/test_t1_water_startup_order.py`, `.github/workflows/raft-t1-water-startup-order.yml`, this session, own WATER-001 work record, own experiment/event/memory and own shared Mini vote.
**experiment_key:** `water-first-error-preworld-v1-CL-61f71ceb`
**resource_key:** `CL/61f71ceb/raft log/lf/LogRaft-20261108-164850-270/session-summary.json`
**run_urls:** https://github.com/alwansan/raf/actions/runs/42512589682 (FAILED), https://github.com/alwansan/raf/actions/runs/42512805526 (FAILED at intermediate source before fixture update), https://github.com/alwansan/raf/actions/runs/42512840042 (latest)
**status:** WAITING_CI for pinned actual CL agreement, after repairing schema mismatch.

## Observations from authentic CL summary

- Exact **CL main source commit:** `61f71ceb3b9e6f16c8fb300656f6e6baf32b33e8`. GitHub blob SHA of existing `session-summary.json`: `18a125b1753182974a5905280f03ebdc96687b33`. LogRaft collector session `20261108-164850-270` was recorded on owner's POCO F5 Pro Android15, target app `com.alwansan.raft.androidtest`.
- First water invalid-pass event `1794145757579` ms, first compute invalid-kernel event `1794145757581` ms, early startup milestone `1794145750876` ms, first world-loaded milestone `1794145822065` ms. Therefore first water warning **64,486 ms before** world-loaded, first FFT warning **64,484 ms before**, and water first warning **6,703 ms after** early-startup event. Both roots appear in the log before the eventual world_loaded marker. This is temporal ordering ONLY; the precise original Unity ComputeShader kernel identity, stage binding, numeric mismatch and actual water pixels remain unverified.
- Final authoritative root counts: water `74,359` = Spectrum `29,700` + Foam Global `44,659`; invalid kernel `11,165`, all indexed `6` in classified root messages. This alone **does not identify Unity FFT kernel name**. The sampled performance counters at last sample were `73,663` water and `11,049` compute, **696** and **116** below final root totals (events after last sample).
- No proof a single warning directly caused a visual defect or that any specific number of errors occurred before world_loaded (only the first one is timestamped precisely). Logcat ring losses possible; KGSL GPU busy/SurfaceFlinger FPS are not Unity GPU or engine FPS.

## Engineering and CI

- Source `scripts/t1_water_startup_order.py` introduced [4133ef8](https://github.com/alwansan/raf/commit/4133ef856deb80c031b4d006a1f1a8e38bf72302); bounded no-symlink/no-FIFO open with O_NONBLOCK, size cap, mtime/ctime mutation checks, duplicate-key audit, source package/session validation, final root-count reconciliation, privacy-preserving sanitized report only. JSON from untrusted import cannot execute code; raw logs are never uploaded.
- Adversarial tests `tests/test_t1_water_startup_order.py` initially 10, then 13 after correction. CI workflow `.github/workflows/raft-t1-water-startup-order.yml` privately downloads only the immutable 18 KB summary by pinned CL commit and runs actual chronological assertions; **no Unity/APK build, no raw log artifact, no exposure of original shaders**.
- First [CI42512589682](https://github.com/alwansan/raf/actions/runs/42512589682) FAILED **after 10/10 synthetic tests PASS**: script read final counters from assumed root JSON fields, while authentic CL schema stores final session count under `stop_time_android_process_exit_info`. This is a real mismatch between fixture and original source, not GPU failure. Corrected code [087b765](https://github.com/alwansan/raf/commit/087b76579ab4c6fffbe1902af434ed9cedf89994), updated authentic fixture [2328a7d](https://github.com/alwansan/raf/commit/2328a7d6efd8b6b3800c0c7bea31ac1ec6c1a664), and added negative controls for authoritative stop-time group inconsistency and boolean schema.
- R2 shared Mini readiness: **T1 NO_BUILD** [0499fe15](https://github.com/alwansan/raf/commit/0499fe15afd4c1bb77292c7e7b7056f46b9e58cf); this session changes no compiled APK T1 GPU driver, and previously delivered T5 unified APK [42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) still awaits Adreno tests.
- No interference with T2 Foam/T3 ShaderLab/T4 Mouse/T5 packaging; no native game build request modified or duplicate shared Mini dispatched.

**next_step:** inspect latest source-only CI 42512840042 and classify first failing actual gate if any; only after validated source result record experiment/event and T1 checkpoint. WATER-001 remains OPEN / full game NOT_READY 0/3.
