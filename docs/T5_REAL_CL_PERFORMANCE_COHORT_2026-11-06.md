# T5 — SurfaceFlinger presentation evidence versus render-error phase (6 Nov 2026)

## Purpose and source boundary

The owner successfully entered, saved, exited and reopened the Raft world using the original source-pinned Android artifact of native run 42058825739. The same phone's 5 Nov 2026 logs report missing Ultimate Water shader passes and invalid FFT compute kernels in large numbers. A reported high FPS should not be interpreted as a fix if it was measured **before** water render errors appeared or if there were virtually no later valid frame samples.

This investigation is limited to the exact public source snapshot `alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57`, `raft log/lf/LogRaft-20261105-220911-559/metrics-20261105-220911-559-00001.jsonl` (Git blob `bb24dda68503897cf4e2a5e4e2d8aef3e71777b8`) and `LogRaft-20261105-230108-327/metrics-20261105-230108-327-00001.jsonl` (blob `0327e5a3bb01ca944b2c40e07d49f503914dd274`). These are **LogRaft** per-sample telemetry, **not** raw Unity `FrameTimingManager` frames. All telemetry is treated as untrusted input, and only aggregate, non-private counts are published.

## Directly inspected observations before automation

| Session | Samples | Game-running samples | Fresh SurfaceFlinger FPS samples | Stale telemetry flags | First observed render error sample | Fresh frames before error | Fresh frames with or after error |
|---|---:|---:|---:|---:|---:|---:|---:|
| 220911-559 | 71 | 70 | 57 | 6 | 11 | 0 | 57 |
| 230108-327 | 119 | 113 | 2 | 105 | 16 | 2 | 0 |

- In the first session, FPS estimates of **3.02–33.56**, mean **22.29** over 57 usable SurfaceFlinger samples, were recorded while shader/kernel-error counters were already active. This is a distribution of sampled **presented** frames, not GPU or Unity engine frame time.
- In the second session, the only valid FPS readings were **120.77** and **120.78** at samples **10–11**. The first observed render error occurs at sample **16**. There were **zero** valid FPS readings from this measurement source after that initial error onset; 105 samples are flagged `frame_telemetry_stale=true`. Comparing 120.78 to 22.29 as a gameplay speedup is invalid.
- GPU busy percentages in this dataset are from **system-wide KGSL**, not isolated Raft GPU timing. PSS may include Android memtrack; RSS/PSS are not directly interchangeable. Render error flood and CPU utilization occur together but do not establish either as the other one's cause. A missing presented-frame estimate **does not prove a frozen game**; SurfaceFlinger surface changes, lack of timestamps and telemetry gaps all need checking.
- Thermal and scene variables differ: first session battery temperatures ranged ~43.9–45°C, second ~38–40.1°C; scene and graphics settings are not pinned to equivalent states. Even with 10+ post-error readings in both sessions, exact same-scene, same-resolution, same-APK SHA and true Unity frame metrics must precede a comparative claim.

## Implementation and reproducibility

`scripts/t5_cl_fps_cohort_gate.py` strictly validates source/package and monotonic timestamp/sample ordering, filters out unverified PID or window, stale and insufficient SurfaceFlinger readings, and splits fresh samples by the **first observed render-error counter** in the same telemetry session. It reports small count/median/range summaries only, and fails comparison closed if one session has under 10 valid post-error samples. Even if both exceed 10, comparison remains unverified without matching scene/settings and binary provenance.

`tests/test_t5_cl_fps_cohort_gate.py` adds 18 negative/positive source-free tests including synthetic high-FPS startup, stale non-null FPS, missing present timestamp freshness, wrong process/status/schema/package, invalid numeric samples, strict ordering and compute-only failure onset.

`.github/workflows/raft-t5-cl-real-fps-cohort.yml` executes a **one-shot, read-only** CI of 8-minute maximum, downloads only those two <2MB public CL metrics files through the GitHub API pinned to the original CL commit, verifies each Git blob identity against its declared SHA, runs the synthetic tests and asserts the exact actual cohort counts and `NOT_COMPARABLE` decision. No source game's raw APK/OBB assets, saves or LogRaft raw logcat payload are downloaded or published as artifacts. No Unity/build/preview/renderer changes.

Run: https://github.com/alwansan/raf/actions/runs/42145219506 — **check its actual conclusion before accepting the automated proof.**

## Next evidence requirement

When a later Android test is performed with a **matched signed APK/OBB identity, same world/scene, same render scale/quality, and captured `FrameTimingManager`/SurfaceFlinger freshness**, compare distributions (gameplay frame p50 and p95, error roots/s, CPU, system GPU busy with caveats, memory/RSS/PSS separately). Do not project older sample counts onto newer builds. Independently resolve WATER-001/RENDER-002 shader/kernel roots with T1–T3 and preserve working singleplayer save/audio. This work does not repair water or improve FPS directly; it prevents an unsupported success verdict and pinpoints the telemetry gap to close.

Status: PERF-007 diagnostic scope pending CI; original full game readiness NOT_READY 0/3.

## Completed source-authenticated CI — 2026-11-06 01:39 UTC

[Run 42145219506](https://github.com/alwansan/raf/actions/runs/42145219506), job **127654944860**, exact workflow source `7c0f7fb78a178d32c3539b35b661a848ffa8a9b9`: **COMPLETED SUCCESS**.

- **18/18** synthetic positive and negative controls passed (0.005s); `py_compile` passed.
- Actual CL metrics files downloaded read-only, pinned to source commit; verified both original Git blob SHA1 identities, sizes **374,587** and **646,527** bytes. No raw telemetry uploaded as artifact or exposed in CI outputs.
- Output on genuine 190 records reproduced **57 vs 2** valid SurfaceFlinger FPS samples, **6 vs 105** stale, first render-error samples **11 vs 16**, and **57 vs 0** valid FPS samples at/after observed render error phase. The first session post-error fresh FPS sample median was **23.87**, min **3.02**, max **33.56**; second has **no valid post-error SurfaceFlinger FPS**, so **NOT_COMPARABLE_inadequate_fresh_post_render_error_samples**.
- This is a **diagnostic refusal of an unsupported comparison**, not proof the game froze or got faster. In fact, contemporaneous Unity internal persistent JSONL data also exist and must be independently linked/qualified; SurfaceFlinger unavailability is NOT Unity frame unavailability.

Next independent T5 work should analyze actual `raft-logs` game-side interval measurements with scene identity and startup/frame window gates; do not infer comparative FPS from their simple averages either.
