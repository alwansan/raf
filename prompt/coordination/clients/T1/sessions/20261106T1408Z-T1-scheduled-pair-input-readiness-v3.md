# T1 scheduled — original/translated FFT paired capture readiness

- session_id: 20261106T1408Z-T1-scheduled-pair-input-readiness-v3
- origin: scheduled
- issue_id: WATER-001; status: blocked_on_missing_paired_capture (not game readiness)
- resumed_from_sessions: 20261106T133640Z-T1-chat-nested-phi-8d31; 20261106T1310Z-T1-scheduled-ulp32-m4q8
- base_sha: 70134bae931a241f3de981904e5c1aca5b67ee4c
- scope_commit: 3039d687d50fc0aebedbec0784c792c063235923
- original_source_pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- experiment_key: water001-original15964ea8-butterfly1-x-source-candidate-invocation-paired-capture-prerequisites-v3
- work: prompt/coordination/work/WATER-001/20261106T1408Z-T1-scheduled-pair-input-readiness-v3.json

## Priority and provenance
Read docs/DEVICE_FEEDBACK_42058825739_AR.md before selection. Owner confirmed world entry/save/exit/reentry on artifact from 42058825739; publish failed. CL pinned 520c4cf: session 220911-559 has 23,884 water pass and 3,850 FFT kernel errors; session 230108-327 has 39,132 water pass and 6,026 FFT kernel errors. This is not a regression to APK86 and is not proof of a fix. T4 owns physical mouse, T5 owns three right-side buttons/Resolution; no overlapping input files changed.

## Verified newest evidence
- SHA-original Vulkan source run 42228497335 completed SUCCESS, head e936ad1f96c0bb0617a7a7199c2304c5f47442ff. Its prior T1 session documents real structural CFG backedge and loop-carried float32 vector Phi for translated butterfly1 X; **not** dynamic branch execution or numeric equality.
- Source-only run 42228404633 SUCCESS, head ca66e4bbb9e5594d662eee8a0a99405ec88a3e65, 61/61 tests per previous session. No original shader execution in that run.
- Original source run 42227795780 SUCCESS, head 2225efcef4071b768f85103727fbbb4225dd18ed.
- Checked run artifacts API for all three: no retained artifacts listed. No paired original+candidate invocation-keyed buffers or SHA-bound same-input/same-dispatch manifest were available from these runs. Thus there is no defensible first numeric divergence or ULP value to report.
- Latest checked branch HEAD 70134bae931a241f3de981904e5c1aca5b67ee4c (before scope commit). T5 signed OBB attestation 42230326050 in_progress; no overlap with T1 FFT, not cancelled or repeated.

## Decision and bounded continuation
Do **not** launch duplicate original structural provenance runs or fabricate numeric samples. The required next engineering experiment is two independently authenticated captures of butterfly1 X original and translated candidate on identical dispatch/input, private runner with ZIP2 pin and resource/dispatch manifest; sanitize outputs, feed strict pair gate scripts/t1_fft_invocation_pair_gate.py, coordinate comparator and ULP helper. If the gate rejects, fix capture identity, not shader math. If accepted, record first invocation key and ULP before editing HLSL. Source artifacts remain private, no raw shader or game payload published.

No authored Unity .compute/Android/Adreno proof, no FindKernel/Dispatch runtime binding proof and no new device test this cycle. WATER-001 remains OPEN; NOT_READY 0/3. This cycle establishes a concrete evidence blocker rather than claiming a completed GPU experiment.
