

## Original FFT caller reachability — 3 November 2026

Client raft-20261103T103610Z-4e91b2cd inspected SHA-pinned WavesRendererFFT e7f6b8fd477f321120fc626781f0653fe1168f0e86daad0cdf8d9c4e56b323e9. Added scripts/probe_fft_caller_policy.py, an explicitly modeled source-policy table guarded by the full source SHA. Local112 boolean/size cases pass, including10 compute selections; unknown source rejected. Actual caller chooses pixel when ForcePixelShader, missing compute asset, unsupported compute, or resolution>512; high precision is requestedHighPrecision OR resolution>=2048. Thus the earlier N2048 half-integer compute storage negative control is unreachable through this selector, not a demonstrated game defect. N1024 pixel/half remains source-reachable if high precision is false, but active resolution/quality, texture creation and GPU execution remain unknown. No original shader/quality/source changed; WATER-001/RENDER-002/FFT-FORMAT-009 stay open and NOT_READY/0-of-3. No queued/in_progress runs returned; CL identities unchanged; lograf-65 is not game delivery. Next correlate active quality and requested resolution before numeric shader replay. No Unity/LFS/native request/task changes.

Correlate active quality/resolution and pixel N1024 half possibility; do not infer a GPU defect from the model.

## FFT policy CI verified — 3 November 2026

CPU-only [41630004335](https://github.com/alwansan/raf/actions/runs/41630004335) SUCCESS on72a42aac4cf97575e3d7bd4ad964a4291167fc71:112 caller cases,4 storage variants,16 capability cases,1 discrepancy. Pinned original-source decompilation; no LFS, Unity/GPU or raw source artifacts. New12-minute independent lane. Source/evaluator negative controls and local workflow parse pass. Water restoration/format blockers remain OPEN; NOT_READY/0-of-3. No native request/task changes. Next: actual compatible-format and shader numeric evidence.


## Read-only builtin identity coverage diagnosis — 3 November 2026

Investigated confirmed preview41624581951 first failure: zero exported built-in identity matches before Unity, not a signature/package failure. A9/A6 have corrected separate identity/include bugs without closing that blocker; their production files were left untouched. Added scripts/probe_builtin_export_coverage.py, a read-only lexical count probe with SHA-pinned official2021.3.45f2 ZIP and no source/name disclosure. Existing local107-file shader subset:24 empty,83 parseable non-vendor identities,0 exact matches against198 vendor identities. Ordered content digest e3aafd61acef71530e263b1aade4e8ba5e2ad2f164c231d9fffc696b69963906. Unknown archive and empty inventory negative controls pass. This local subset has NOT been authenticated as the complete failed-run export; it cannot establish the full-export cause or justify substituting custom shaders, weakening gates or a retry. Next obtain full-export count/identity provenance through CPU reconstruction evidence. No Unity/build/request change; no APK produced by this work. RENDER-002/WATER-001 remain open.


# Original CPU FFT two-dimensional oracle — 2026-11-03

## Evidence
Source: 555e7f6e39416b65d0e657db43e71d0be7d1949e.
[Actions run](https://github.com/alwansan/raf/actions/runs/41637650224), attempt 1, job 125922799795: completed success.
Implementation: scripts/verify_original_fft_cpu_2d.py and .github/workflows/raft-fft-cpu-2d.yml.
The generator retains the authenticated original-body hash checks from verify_original_butterfly_numeric.py. Original source remains private temporary runner input; logs contain aggregate results.

## Experiment and actual result
The original CPU complex lane executes all rows then all columns for four 32×32 inputs: asymmetric complex impulse, constant, asymmetric complex tone, and deterministic real random input. Comparison is against an independent direct two-dimensional DFT with negative exponent and no normalization, rather than a second separable FFT.
- Four cases passed: maximum relative L2 = 1.8933043868319998e-7, threshold 1e-5.
- Two negative controls passed: a transpose and an extra 1/(N*N) normalization are rejected on the random signal.
- Existing original butterfly suite also passed: 40 cases, 194893 checks, 3 negative controls; maximum float relative L2 1.88937368177527e-7, half-table 0.00023868836710026192, original CPU 2.0495406296816126e-7.
- Local Python syntax and workflow YAML checks passed before submission; actual C# execution was performed by Actions, not locally.

## Limits and next work
This establishes a bounded CPU oracle for axis order, sign and normalization at N=32 using the original complex lane. It does not execute a translated shader, a Unity import, GPU, half-precision intermediate render textures, every CPU lane, or Android. It cannot close WATER-001, RENDER-002 or FFT-FORMAT-009. No runtime source, original asset, GUID/meta, quality setting, build request or scheduled task changed.
Next use this oracle when authentic shader bodies/resource bindings become available; validate two-pass shader output and intermediate precision independently. Project remains NOT_READY, no candidate, 0/3 complete reviews.


## Verified original CPU inverse FFT
2026-11-03: https://github.com/alwansan/raf/actions/runs/41645609498 SUCCESS on753a3d71d870edf821210bb50cc7dfa67ed977ee: 4/4 original CPU32x32 inverse roundtrips relativeL2<1e-5, 4 direct2D comparisons max1.8933e-7 and2 negative controls pass. No GPU/Unity/device claim; WATER-001/RENDER-002 remain OPEN, NOT_READY0/3. Next compare restored shader arithmetic. No native build or tasks changed.


## Original CPU complex random FFT reference — verified 2026-11-03
[Run41667519615](https://github.com/alwansan/raf/actions/runs/41667519615) SUCCESS on86dedcecaa54d18966a13f6eba04a02d2a689a39: **5 direct2D comparisons and5 inverse roundtrips**, including independent deterministic random real/imaginary inputs, N32. Max forward relativeL2=1.8933043868319998e-7; all inverse errors<1e-5;2negativecontrols pass. Existing40-case original butterfly suite194899checks passes. Actual original-body C# CPU execution, no shader/Unity/device execution, intermediate half precision or all-channel proof. WATER/RENDER/FFT OPEN, NOT_READY0/3. Next use this completed reference for recovered arithmetic comparisons; avoid further incremental oracle cases without a demonstrated missing behavior. W1's independent Depth numerical/raster work is not replaced or duplicated.


## Correction: FFT canary mode flag — 2026-11-03
Run41686164808 failed20/20 at validation because the newly authored boundary incorrectly required synthetic_canary_verified=true for actual FFT workloads. C++ emits this flag from --canary mode only; the workflow separately verifies the known8x1 sum before original FFT execution. Corrected boundary requires production mode(false), exact1024x1024 extent and requested seed/group. Six exact AST-extracted controls pass locally; fixture corrected. Previous statement that false meant failed canary is superseded. No shader arithmetic or historical equivalence result invalidated by this diagnostic regression. Next inspect justified same-workflow rerun triggered by corrected source; no Unity/native build.


## FFT executor boundary correction verified
Actual CPU Vulkan run41687345468 SUCCESS at9cd002eec0b3fe623d1e58a570320251a6d51176: all20 authenticated program pairs execute again; all20 match within selected RGBA32F scenarios. Rejected-run41686164808 remains recorded as diagnostic regression, not shader failure. Some scenarios write only64pixels, so equal output does not imply full1024x1024 coverage or full-water correctness. Separate no-LFS workflow raft-fft-workload-boundary.yml now explicitly runs the new requested-workload fixture and existing schema suite; prior heavy workflow selected only its old test filename. No Unity/device/full-water proof. Next verify cheap fixture CI and continue original shader restoration rather than repeating this numeric workload.


## Workload boundary regression final verification — 2026-11-03
Run41696574334/source42cbccbf6108f3ca082711f0d067369971a62709 SUCCESS, job126128580376. Actual logs confirm new workload fixture1/1 (six positive/negative controls) and schema suite8/8 executed. No LFS or Unity. Together with original software Vulkan41687345468 this closes the diagnostic workload-boundary repair only. Canary semantics correction remains explicit; no full water/device proof.
Next independent source-restoration target: A12 nonzero constant-buffer reflection blocker (88-byte original metadata,544usedSize across2CBs); read exact stage pins and common parameter layouts before making changes. Do not discard CB records or alter W1 empty-override assumptions. No repeated numeric run needed.


## ZIP2 Blur member observation — 2026-11-04
Read live A12R report/source/state (completed structural reflection41736229248), coordination README/unified/templates, owner ZIP2 provider and active native41741108965. Did not duplicate A12R reflection or touch W1/build. Independent source7bbc443c run41742032440 job126285649840 SUCCESS: 14/14 originals488439356bytes restored and SHA-verified, all6CB explicitlypartial,7matrix/vector member records recovered as numeric indices/dimensions; all fit compiled spans under an explicitly unverified byte-offset model, no overlaps. Four local+CI test methods pass. Report docs/ORIGINAL_BLUR_PARTIAL_CB_MEMBERS_2026-11-04.md contains numeric table and limits. A12R's earlier absence-of-RDEF error is now superseded by authenticated structural diagnostics; do not repeat old failure. No private source publication or Unity/native request. Game NOT_READY0/3. Next: Correlate actual DXBC CB operand masks and translator offsets with the seven original partial-CB members before any named uniform/ShaderLab rewrite; do not repeat unchanged observation.
