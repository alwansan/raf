# T1 scheduled — Unity carrier report shape gate
- session_id: `20261106T1907Z-T1-scheduled-report-shape-n8v2`
- origin: scheduled
- base_sha: `07ab8f0a6a5f1b86806031a01041386e3d0f8da0` (after live HEAD collision/recheck)
- resumed_from_sessions: `20261106T1850Z-T1-chat-gpu-input-join-b71c`, `20261106T1808Z-T1-scheduled-unity-carrier-gate-m4k8`
- work: `prompt/coordination/work/WATER-001/20261106T1907Z-T1-scheduled-report-shape-n8v2.json`
- issue: WATER-001 OPEN; readiness NOT_READY 0/3.

## Device-first baseline
Owner report `docs/DEVICE_FEEDBACK_42058825739_AR.md` and pinned CL 520c4cf: run 42058825739 artifact installed; owner entered, saved, exited and re-entered world. Release publication failed; 220911 log summary 23884 water pass errors and 3850 FFT kernel errors; 230108 39132 and 6026. This does not identify failing kernel by itself. Preserve sound and Settings. Physical mouse T4, three buttons and Resolution T5. T1 vote remains 'لا يحتاج' because no integrated water fix.

## Independent engineering
Scope reserved at commit `c4c52dae7930e36ac0df443bcbd59ef9030e3238` after concurrent HEAD changed from 67e659e to 07ab8f0. New isolated `scripts/t1_fft_carrier_report_shape.py` at `7cde60e6f98dae6eb5578dc5f61f4260dfa980fc` parses precisely ten LF-terminated ASCII decimal counters, bounded to 64 dispatch threads and 512 bytes, rejecting ambiguous/extra/truncated lines. It reports positive controls 0/3/4 separately from seven diagnostic categories; output explicitly refuses GPU, authored-kernel and Android-water claims. New `tests/test_t1_fft_carrier_report_shape.py` at `069ee33c94884939478559e3f6f86c6a8c198a7e` covers valid and malformed controls. Tests not yet executed on repository source; no CI dispatch or Unity test in this cycle. Existing paired Vulkan 42254539826 succeeded for its fixture, original-derived Unity 42198180194 differs; sourcefree diagnostics cannot settle FindKernel/Dispatch.

## Next
Run `python3 -m unittest tests.test_t1_fft_carrier_report_shape` (or discover mode if tests is not a package). Integrate only if existing real Unity ten-counter artifact format is confirmed exactly as assumed; otherwise adapt parser without loosening provenance. Obtain real Unity GPU ten-counter report and paired input/trace, then test actual FindKernel ID, resource bindings, variant and dispatch. No new trial APK or readiness claim.
