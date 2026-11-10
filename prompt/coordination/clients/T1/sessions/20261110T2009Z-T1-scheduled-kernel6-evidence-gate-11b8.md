# T1 — 20261110T2009Z-T1-scheduled-kernel6-evidence-gate-11b8
origin: scheduled
issue: WATER-001 OPEN NOT_READY 0/3
owner source SHA: e9c358eda01785b65e4eb14f18723da426635628
owner run: 42058825739
CL source SHA: 520c4cf409aa20a4db54ff80ed87d8807d9cba57
resumed from: 20261110T1912Z-T1-scheduled-kernel6-sampling-a6c9; 20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e
scope commit: 57cbfc73369052812d18af9d600273b32d49e89e

## Evidence
Owner entered world, saved, exited and re-entered from artifact. Publishing failed. Distinct CL sessions 220911-559 and 230108-327 contain 23884/3850 and 39132/6026 water-pass/kernel error messages. These are message counts, not unique failures.
Existing scripts/t1_kernel6_log_context.py supports errors-only bounded SHA-preserving sampling. Existing direct Dispatch instrumentation was not in owner-tested artifact. Therefore index 6 cannot be mapped to the sixth original compiled FFT candidate or to an authored Unity kernel by these summaries.
No native Unity/GPU/device run, no Actions cancellation or duplicate, no T4/T5 file edits. Local git DNS resolution failed; GitHub connector read/write worked. This checkpoint is evidence triage, not a source fix.

## Next step
Run existing analyzer separately on first kernel6 errors from each pinned CL log; map same-build ComputeShader GUID, FindKernel name and returned index, Dispatch call; compare first divergent Vulkan/Unity pass after mapping. Run existing regression tests on current source. Keep WATER-001 OPEN NOT_READY 0/3.
