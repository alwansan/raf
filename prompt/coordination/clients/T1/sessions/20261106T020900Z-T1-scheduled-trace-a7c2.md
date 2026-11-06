# T1 scheduled — 20261106T020900Z-T1-scheduled-trace-a7c2

origin: scheduled
issue_id: WATER-001
resumed_from_sessions: 20261105T121347Z-T1-paired-capture; prior scheduled T1 original-coordinate rewrite checkpoint (cc135ad)
scope_commit: f177ecb0be974c9ff6eef433005a513614046db7
source: feature/android-native-port
owner_phone_reference: https://github.com/alwansan/raf/actions/runs/42058825739
device_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md
original_experiment: https://github.com/alwansan/raf/actions/runs/42141540903
job: 127642764973

## New verified finding from the completed CI job logs

The original-slot0 private Vulkan experiment **completed successfully as a diagnostic** on 2026-11-06 01:17 UTC; the job executed actual private trace dispatch/readback, not just static inspection. Authenticated source metadata: ZIP2 commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385; original FFT object SHA256 9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247.

Observed source/butterfly image fetch sites = 1/2. Captured **384 actual fetch records** (source 64; butterfly site 1 256; butterfly site 2 64), with **0 out-of-bounds** at each site. Self-comparison of the exact private trace returned **0 missing/extra coordinate records and 0 value-bit mismatches**; this checks trace export/reader consistency, NOT cross-backend agreement. Baseline original-derived Vulkan pair pass0 compared 64 written pixels, pass1 32, with 0 mismatches and 0 coverage differences against its same-source roundtrip comparator. After rewriting exactly **one source fetch** to integer coordinates, the same Vulkan roundtrip remained 64/64 and 32/32 parity. This is a negative discriminating result for the hypothesis that *the isolated source-fetch integer-coordinate rewrite alone* explains the Vulkan same-source parity failure: there was no failure in either Vulkan control. It **does not** address the prior Vulkan↔Unity mismatch (63/64 pass0 and 31/32 pass1 from CI42025620147).

SPIR-V provenance observed float32→sint32 bitcast at all three fetch coordinate sites. The HLSL roundtrip trace reached depth_limit, so a static conclusion that the bitcast alone causes the Unity difference is unsupported. The promoted-SSA variant introduced extra bitcasts/OpCompositeInsert and altered a butterfly Y lane boundary; preserve this as a candidate for a controlled cross-backend experiment, not a proven repair.

## Device correlation and limits

Owner phone CL 220911-559: 23,884 water pass errors and 3,850 kernel errors; CL 230108-327: 39,132 and 6,026. Kernel index 6 remains **unmapped to an original Unity FindKernel identity**. No valid numeric connection between these repeated log errors and any of the three slot0 Vulkan fetch sites is established. The owner confirmed world entry/save/reopen on artifact 42058825739, but the packaging publication failed; do not regress this evidence to APK86.

No native Unity Editor FindKernel/Dispatch, Android GPU or actual water pixel validation in this run. No CI was dispatched or cancelled. No original raw game assets were published. T4 physical mouse and T5 three buttons/Resolution have their own active scopes; no overlap.

## Next exact experiment

On the existing SHA-pinned original slot0 private fixture, capture **both Vulkan and Unity** fetch coordinates and values at source site0 and butterfly sites1/2 using identical uploaded RGBA32F input, dimensions, sampler and per-dispatch thread IDs; compare first divergent site/coordinate before arithmetic. Add a cross-backend integer-coordinate variant only after a differing fetch is established. Independently map the phone's kernel index6 through logged Unity kernel name, shader asset GUID and actual FindKernel result before binding any original compiled slot. Keep WATER-001 OPEN / NOT_READY 0/3.
