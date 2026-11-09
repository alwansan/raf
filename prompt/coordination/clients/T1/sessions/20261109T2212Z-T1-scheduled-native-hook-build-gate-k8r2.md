# T1 — FFT original Android hook: full-build pre-Unity blocker
session_id: 20261109T2212Z-T1-scheduled-native-hook-build-gate-k8r2
origin: scheduled
status: completed_read_only_diagnostic
resumed_from_sessions: 20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e; 20261109T2030Z-T1-chat-index6-selector-correlation-c2d7
base_sha: 19bf77c3423e87c80479bc62e14e86e91c6560b2
work: prompt/coordination/work/20261109T2212Z-T1-scheduled-native-hook-build-gate-k8r2.md
work_commit: 0095f0d76d607a7e24ccbdc62509a89a9014c516
issue: WATER-001 OPEN / NOT_READY 0/3

## Verified evidence
Owner device report docs/DEVICE_FEEDBACK_42058825739_AR.md: owner entered/saved/re-entered world from artifact, publishing failed; CL pinned 520c4cf, sessions 220911 and 230108 have separate kernel and water-pass counts. This supersedes APK86 world-failure narrative.
Recent T1 chat authenticated original Dx11FFT source with 0 direct FindKernel, 2 numeric Dispatch; Android-only safe throw/returned hook, source CI 42695722354 success and JSONL parser CI 42696197130 success. Neither is original phone execution.
Latest branch at start 19bf77c3423e87c80479bc62e14e86e91c6560b2. Full native run https://github.com/alwansan/raf/actions/runs/42696228231 FAILED reconstruct, job https://github.com/alwansan/raf/actions/runs/42696228231/job/129428944191. Failed step 'T5 attest final native Android runtime source bytes (read-only)' raises ValueError: Original-managed/native Unity runtime staging drift: managed_only=0 native_only=1. publish-early-test skipped, delivery-result failed. No full Unity game compilation or device FFT evidence can be inferred. T5 latest HEAD checkpoint explicitly owns native failure. T4 mouse runtime source CI 42704198957 success, not phone proof.

## Scope and continuation
This cycle only read live branch, run list, original feedback, T1 chat sessions, and failing reconstruct log; no game source modified, no Actions dispatched, no T4 mouse/T5 resolution files touched. Work file published with GitHub contents API (no force); no concurrent file overwritten. Distinguish synthetic GLES mini T1-05 PASS from original water FFT.
Next: T5 repairs source attestation and yields authorized full build; T1 then inspects same-build raw before/returned/threw and source numeric Dispatch index6, with original .compute identity and first numeric divergence still unverified. Keep WATER-001 OPEN/NOT_READY 0/3. Do not equate original DX11 compiled slot to Unity FindKernel index.
