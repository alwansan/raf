# T1 WATER-001 — pinned LogRaft first-water / FFT warning chronology

**Date:** 2026-11-08 (T1 chat `20261108T1836Z-T1-chat-water-startup-order-c5e7`)  
**Source:** [CL original fixed commit](https://github.com/alwansan/CL/tree/61f71ceb3b9e6f16c8fb300656f6e6baf32b33e8/raft%20log/lf/LogRaft-20261108-164850-270), `session-summary.json` SHA256 `941d37d4b18a2bf11471098bd0668029add11913d76b0a97086dd9fb185e7ff7` (Git blob `18a125b1753182974a5905280f03ebdc96687b33`).  
**Verified by:** [T1 source-only CI #42512986569](https://github.com/alwansan/raf/actions/runs/42512986569), source `fbfe06be8f88133d4e0bee76fc1e86b008afe3d1`, 13/13 adversarial synthetic cases + pinned real CL source audit.  
**Target:** `com.alwansan.raft.androidtest`, POCO F5 Pro, Android 15. **No new APK/Unity/Adreno compute dispatch executed by this validation.**

## Earliest observed milestones in same session

| Evidence milestone | Unix ms | Local time (Baghdad, UTC+03) |
|---|---:|---|
| FMOD bootstrap log observed | 1794145741759 | 16:49:01.759 |
| Raft Android early-startup log observed | 1794145750876 | 16:49:10.876 |
| First Ultimate Water invalid-pass log | 1794145757579 | 16:49:17.579 |
| First invalid compute-kernel log | 1794145757581 | 16:49:17.581 |
| First world-loaded message observed | 1794145822065 | 16:50:22.065 |

The first invalid water pass is **64,486 ms BEFORE** the first world-loaded log; the first invalid kernel warning is **64,484 ms BEFORE** it. First water warning follows the early startup log by **6,703 ms**, with the first kernel warning **2 ms after** the water warning. These statements compare *observed Logcat event timestamp fields from the same pinned session*; they do **not** prove that an issue in a particular shader caused the world failure, or that these are the very first engine events if logcat dropped lines. World-loaded is a log milestone and does not prove full scene GPU readiness.

## Mandatory counter consistency

The final stop-time root counts are **74,359** invalid Ultimate Water passes and **11,165** invalid compute-kernel messages. The pass components sum exactly: **29,700 Spectrum + 44,659 Foam Global + 0 other = 74,359**. The classified kernel-index root messages are **11,165 index-6 + 0 other-index**; numeric index 6 in a log **does not prove a Unity kernel name, compiled DXBC slot, original FFT stage or precise shader resource binding**.

Unlike stop-time totals, the last 3-second performance sample showed **73,663** water and **11,049** kernel messages. It precedes final counts by **696 water / 116 kernel** messages, so use final stop-time counters for whole-session claims. Neither figure is the number of GPU dispatches: these count emitted root errors, potentially with Logcat loss. The screen presentation estimate is **SurfaceFlinger**, not Unity `Time.deltaTime` or Unity GPU frames; KGSL GPU busy is system-wide.

## Reproducible bounded evidence gate

Source checker: `scripts/t1_water_startup_order.py`. Regressions: `tests/test_t1_water_startup_order.py`. Workflow `.github/workflows/raft-t1-water-startup-order.yml` pins CL commit, downloads only the existing 18 KB public JSON session summary to runner private TEMP, validates source checksum and chronology, prints **aggregates only**, deletes the temporary file and publishes no raw assets. It refuses symlink/nonregular/FIFO, >128 KiB, truncation/mutation, duplicate authoritative JSON keys, wrong package/session and mismatched final categories or stop-time counters. Non-authoritative `last_sample` duplicates are counted and never used for the authoritative final gate.

**Corrected audit failure history:** [CI #42512589682](https://github.com/alwansan/raf/actions/runs/42512589682) first had 10/10 synthetic tests PASS but rejected actual CL because fixture wrongly assumed root-level `final_shader_pass_errors_total`. Original stores it at `stop_time_android_process_exit_info`; fixed [087b765](https://github.com/alwansan/raf/commit/087b76579ab4c6fffbe1902af434ed9cedf89994) and added nested-view consistency. [CI #42512840042](https://github.com/alwansan/raf/actions/runs/42512840042) failed one adversarial test because it tried to duplicate a no-longer-present field, fixed [fbfe06b](https://github.com/alwansan/raf/commit/fbfe06be8f88133d4e0bee76fc1e86b008afe3d1). Final [CI #42512986569](https://github.com/alwansan/raf/actions/runs/42512986569) **SUCCESS: 13/13 + original pinned summary assertions**; no failed gates hidden.

## Implementation decision / next falsifiable test

Water warnings already appear before the **world_loaded log milestone**, so a diagnosis constrained to *only* scene navigation after world load cannot account for the first observed errors. This increases the value of tracing early UltimateWater initialization and original shader/pass creation before world entrance. It does **not** distinguish missing ShaderLab pass/incorrect original material from runtime GPU kernel identity and dispatch defects.

Next evidence required to advance original WATER-001: *same immutable game build* and original SHA-authenticated `.compute` GUID/name, Unity `HasKernel/FindKernel(name)` returned ID, `GetKernelThreadGroupSizes`, `SetTexture/SetBuffer` resource identities and `Dispatch` parameters at the first failing call; then staged numeric CPU/Vulkan/Unity readback for identical inputs; finally Android Adreno visual validation. Keep proprietary game assets private. Do not infer that log index 6 corresponds to any one reconstructed bank/program slot.

**Status:** source evidence chronology VERIFIED; Raft original water shader/FFT repair **OPEN**, device proof **NOT_TESTED**, full Raft readiness **NOT_READY 0/3**. Current unified Mini APK is an unrelated synthetic GLES diagnostic and already available as an Actions Artifact ZIP; this report does not justify another Mini APK or a new full XAPK.
