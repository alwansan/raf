# T1 scoped work — 20261107T2110Z-T1-scheduled-fft-evidence-a4d9
origin: scheduled
track: WATER-001
source_branch: feature/android-native-port
base_head_observed: c5c75b6d7f14f463d1e4c7315ce6465580ea9cac
experiment_key: fft-original-to-unity-kernel6-auth-bridge
shared_resource: none; no Unity/CI dispatch
files_owned: prompt/coordination/work/20261107T2110Z-T1-scheduled-fft-evidence-a4d9.md; prompt/coordination/clients/T1/sessions/20261107T2110Z-T1-scheduled-fft-evidence-a4d9.md

## Evidence and hypothesis
Owner phone run 42058825739 source e9c358eda01785b65e4eb14f18723da426635628: world/save/reopen succeeds from artifact; publish fails. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57: sessions 220911-559 and 230108-327 report 23884/39132 water-pass errors and 3850/6026 kernel errors respectively. T1 prior kernel6/material-split reports classify errors but do not prove original FFT kernel identity. Existing source-only gate scripts/t1_kernel_index_identity_gate.py accepts claimed GUID/name/hash metadata as STRUCTURAL_ONLY, never as runtime proof. Latest T1 tests/test_t1_kernel_index_identity_gate.py contains five synthetic checks. Source files were read live; no device Vulkan/Unity paired buffers supplied.

Hypothesis: index 6 is a Unity runtime Dispatch index whose originating ComputeShader GUID, FindKernel name, and source-original program have not yet been causally linked. Do not infer FFT from numeric coincidence.

## Non-overlap and next executable experiment
T4 owns mouse and T5 owns UI/Resolution and packaging. Do not modify these. T1 next evidence: one captured actual Unity FindKernel/Dispatch call tuple (GUID, kernel name, returned index, groups, bound resource names and dimensions, scene phase, immutable build/source SHA) from original-staged candidate; matching original program SHA/descriptor identity; then same-input Vulkan vs Unity per-pass output hashes and first divergent coordinates. Without those captures, numeric comparison would be fabricated. No new equivalent CI was launched. Preserve original shader bytes privately.

Status: waiting_evidence; WATER-001 OPEN; NOT_READY 0/3.
