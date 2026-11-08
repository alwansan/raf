# T1 scheduled session — 20261108T1714Z-T1-scheduled-fft-shared-lab-b6d2
origin: scheduled
resumed_from: 20261108T1506Z-T1-scheduled-trace-ci-8f2c (historical previous summary); older state.json is stale 20261105T002850Z.
base_sha: 31412fcbd7b0db23c4c07787c1ce1e6dbfe06caf
scope: WATER-001, FFT kernel attribution and first numeric divergence.
work: prompt/coordination/work/T1-20261108T1714Z-T1-scheduled-fft-shared-lab-b6d2.md
experiment_key: t1-fft-unity-vulkan-first-divergence-20261108
resource_key: none
run_urls: https://github.com/alwansan/raf/actions/runs/42493143730 ; https://github.com/alwansan/raf/actions/runs/42497767712 ; https://github.com/alwansan/raf/actions/runs/42503889895
status: WAITING_CI for shared Java source compile; independent evidence analysis completed.

## Verified inputs and evidence separation
- Owner phone 5 Nov: source e9c358eda01785b65e4eb14f18723da426635628; entered/saved/reopened world from Artifact 42058825739; package publishing failed. This supersedes APK86 failure for that scenario only.
- 5 Nov CL 220911-559: 23884 water invalid pass / 3850 FFT invalid kernel. CL 230108-327: 39132 / 6026. These are separate logger sessions, not deltas or GPU execution counts.
- 8 Nov CL 164850-270: 74359 water invalid pass / 11165 FFT invalid kernel / 7372 cursor RGBA32 warnings. Session counters are not cross-version normalized and do not identify the first failed kernel. Mouse camera capture works; buttons and wheel fail, T4-owned.
- Unified team-testpack revision 1 T1-01..04 only tests GLES capability, synthetic SSBO one-pass, two-pass barrier, negative shader compilation. These do NOT test authored Unity FFT, FindKernel index mapping, Vulkan/Unity numerical agreement, or original water material passes. Shared mini Java compile 42503889895 was in_progress at review; no duplicate build.
- Latest owner policy requires one shared APK com.alwansan.raft.lab.shared and one data-only testpack, T5 owns integration/build. Older T1 standalone mini APK is historical.

## Decisive next experiment contract (not yet executed)
For each authored compute program use a verified source SHA, GUID/.meta, actual Unity import name, and kernel-name enumeration from the SAME build. Capture FindKernel(name) returned index and HasKernel(name), then bind each required texture/buffer with dimensions, formats, stride and CB layout; capture Dispatch(x,y,z), group size and Unity graphics API. For every FFT stage store deterministic input seed, dimensions, normalization, butterfly order, precision and CPU/Vulkan reference digest; compare first mismatching stage with max abs/relative error and element coordinates. Preserve private original bytes; public output is names/hashed provenance, counters and redacted numeric summary only.
Acceptance gates: (1) original program provenance SHA/GUID; (2) actual Unity 2021.3 FindKernel+Dispatch runtime trace; (3) per-stage Vulkan vs Unity numeric readback on identical inputs; (4) Android Adreno phone image/device trace; (5) full Raft water device confirmation. A source-only CI PASS cannot satisfy gates 2-5. Do not infer index 6 from raw error text alone.
Critical unknown: original authored FFT kernel source matching ZIP2 and Unity import not yet verified; original shader/program mapping and per-stage numerical trace remain unproven.
next_step: inspect shared CI result without rerunning; coordinate T5 to incorporate a real original-derived GPU test only after authentic source provenance; use isolated T1 case revision/driver change and request NEED_BUILD only when integrated. Preserve WATER-001 OPEN / NOT_READY 0/3. No Unity build or phone test performed.
