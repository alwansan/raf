

## Original FFT caller reachability — 3 November 2026

Client raft-20261103T103610Z-4e91b2cd inspected SHA-pinned WavesRendererFFT e7f6b8fd477f321120fc626781f0653fe1168f0e86daad0cdf8d9c4e56b323e9. Added scripts/probe_fft_caller_policy.py, an explicitly modeled source-policy table guarded by the full source SHA. Local112 boolean/size cases pass, including10 compute selections; unknown source rejected. Actual caller chooses pixel when ForcePixelShader, missing compute asset, unsupported compute, or resolution>512; high precision is requestedHighPrecision OR resolution>=2048. Thus the earlier N2048 half-integer compute storage negative control is unreachable through this selector, not a demonstrated game defect. N1024 pixel/half remains source-reachable if high precision is false, but active resolution/quality, texture creation and GPU execution remain unknown. No original shader/quality/source changed; WATER-001/RENDER-002/FFT-FORMAT-009 stay open and NOT_READY/0-of-3. No queued/in_progress runs returned; CL identities unchanged; lograf-65 is not game delivery. Next correlate active quality and requested resolution before numeric shader replay. No Unity/LFS/native request/task changes.

Correlate active quality/resolution and pixel N1024 half possibility; do not infer a GPU defect from the model.

## FFT policy CI verified — 3 November 2026

CPU-only [41630004335](https://github.com/alwansan/raf/actions/runs/41630004335) SUCCESS on72a42aac4cf97575e3d7bd4ad964a4291167fc71:112 caller cases,4 storage variants,16 capability cases,1 discrepancy. Pinned original-source decompilation; no LFS, Unity/GPU or raw source artifacts. New12-minute independent lane. Source/evaluator negative controls and local workflow parse pass. Water restoration/format blockers remain OPEN; NOT_READY/0-of-3. No native request/task changes. Next: actual compatible-format and shader numeric evidence.


## Read-only builtin identity coverage diagnosis — 3 November 2026

Investigated confirmed preview41624581951 first failure: zero exported built-in identity matches before Unity, not a signature/package failure. A9/A6 have corrected separate identity/include bugs without closing that blocker; their production files were left untouched. Added scripts/probe_builtin_export_coverage.py, a read-only lexical count probe with SHA-pinned official2021.3.45f2 ZIP and no source/name disclosure. Existing local107-file shader subset:24 empty,83 parseable non-vendor identities,0 exact matches against198 vendor identities. Ordered content digest e3aafd61acef71530e263b1aade4e8ba5e2ad2f164c231d9fffc696b69963906. Unknown archive and empty inventory negative controls pass. This local subset has NOT been authenticated as the complete failed-run export; it cannot establish the full-export cause or justify substituting custom shaders, weakening gates or a retry. Next obtain full-export count/identity provenance through CPU reconstruction evidence. No Unity/build/request change; no APK produced by this work. RENDER-002/WATER-001 remain open.
