# T1 — exact ZIP2 HLSL FFT candidate real Vulkan invocation-keyed capture

- session_id: 20261106T151730Z-T1-chat-keyed-candidate-3a7f
- origin: chat
- status: completed (real HLSL candidate keyed Vulkan readback)
- issue_id: WATER-001 / OPEN / NOT_READY
- resumed_from_sessions: 20261106T1511Z-T1-scheduled-invocation-cli-k7m2; 20261106T1408Z-T1-scheduled-pair-input-readiness-v3; 20261106T133640Z-T1-chat-nested-phi-8d31
- original_source_pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- base_sha: 12318c5849d17316a488fa14a8304396843542dc
- work_path: prompt/coordination/work/WATER-001/T1-20261106T151730Z-T1-chat-keyed-candidate-3a7f.json
- scope_commit: 9a109902fefcff43945ccc141cf762ce7a44876b
- scheduled_CLI_workflow_commit: 18d091707e9374e4a01d4256d65a16db397f6458
- new_audit_source_commit: dac32a05bba4e4563ab222b460e898b86797c655
- new_audit_tests_commit: 5c8d91c4b5f397db1ea988f1e52d40767ada13b4
- source_only_workflow_commit: f94a0b4bd86ae6c83a2d91d854e03a7bd68ce482
- private_Vulkan_workflow_commit: 9505df9a085bbf800c303d6dfa5ee750012eba32
- source_only_success: https://github.com/alwansan/raf/actions/runs/42242015941
- authentic_source_run: https://github.com/alwansan/raf/actions/runs/42242127723

## Restored baseline and distinct question

Last session 20261106T133640Z proved that translated Butterfly1 X is a signed-integer bitcarrier plus a loop-carried float32 vector Phi; authentic original SPIR-V was retained private, but numeric original-vs-translated invocation parity has **NOT** been proven. Scheduled T1 session 20261106T1408Z found no independent paired capture artifacts, and 20261106T1511Z created `scripts/t1_fft_invocation_trace_cli.py` + five unrun source-only tests. Prior T1 `scripts/t1_fft_pass0_vulkan_trace.py` already includes an invocation-keyed candidate mode but original SHA-pinned runtime had only exercised the legacy coordinate histogram trace and then compared a file to itself for parser smoke check. A self-comparison is **not** genuine parity. No active/queued T1 private Vulkan resource at reservation.

## Engineering delivered

- In current source-only 4-minute workflow, run five scheduled invocation CLI tests. Source-only CI [42241766200](https://github.com/alwansan/raf/actions/runs/42241766200) already passed these (pending earlier checkpoint); new cycle independently added candidate-specific audit.
- New `scripts/t1_fft_candidate_keyed_trace_audit.py` and `tests/test_t1_fft_candidate_keyed_trace_audit.py`, eight adversarial tests. The audit requires exact `INVOCATION_SIZE`, nonempty three-site coverage, valid unique invocation+occurrence keys through existing `decode_invocations`. Its output contains only aggregate per-site counts and explicitly states `original_spirv_keyed_capture_present=false`, `independent_pair_comparison_performed=false`, `vulkan_vs_unity_numeric_parity_proven=false`. No coordinates, values, raw shader bytes, private trace fingerprints or original assets appear in log.
- [CI 42242015941](https://github.com/alwansan/raf/actions/runs/42242015941) job 127974449564 **SUCCESS**, 20/20 paired-gate tests, 11/11 coordinate tests, 9/9 invocation trace tests, 14/14 nested Phi, 7/7 ULP, 5/5 scheduled invocation CLI, 8/8 candidate keyed audit = **74/74**.
- Extended only existing isolated T1 exact-original Vulkan 20-minute workflow `.github/workflows/raft-t1-fft-vulkan-roundtrip-isolation.yml` to run the previously available `scripts.t1_fft_pass0_vulkan_trace --invocation-keys --export-private-trace ...` on the original-derived HLSL candidate in private scratch, immediately followed by safe candidate-only audit. Binary never retained as Actions artifact. Private original SPIR-V and unmodified game files remain confidential.

## Current state and next step

[Run 42242127723](https://github.com/alwansan/raf/actions/runs/42242127723) running; wait for actual full Vulkan compile/GPU dispatch. Verify `RAFT_T1_HLSL_KEYED_CANDIDATE_TRACE`, per-site record counts, duplicate-key rejection and original-source recovery before marking this scope completed. If failing, identify exact safe failing stage and implement minimal fix before retrying; do not assert any candidate capture success without the marker. Then build the original SPIR-V independently instrumented keyed capture, attest both same input/dispatch, and use strict paired manifest gate. Original-vs-Unity numeric parity and Android water acceptance remain unproven; WATER-001 stays OPEN. No heavy Unity build/Android APK/shader rewrite was launched, no other agents' jobs canceled.

## Exact-original source-authenticated GPU result (final)

[GitHub Actions 42242127723](https://github.com/alwansan/raf/actions/runs/42242127723), job `127974821489`, **COMPLETED SUCCESS** on workflow commit `9505df9a085bbf800c303d6dfa5ee750012eba32`. Original ZIP2 immutable SHA verification, private shader staging, glslang compilation, SPIR-V validation, Vulkan CPU/Mesa dispatch, private scratch cleanup all passed.

The new execution of `--invocation-keys --export-private-trace` produced exactly **384 real original-derived HLSL candidate GPU reads**, **[64, 256, 64]** by source / butterfly1 / butterfly2. All per-invocation+occurrence keys decoded without duplicate, out-of-bounds counts **[0,0,0]**. Two same-Vulkan pass output readbacks within this host fixture compared 64 and 32 written pixels and both matched expected outputs internally; this does **not** mean original source and translated HLSL coordinate arrays matched. The audit emitted only `RAFT_T1_HLSL_KEYED_CANDIDATE_TRACE`, candidate-only, no original keyed buffer, no source vs translated invocation-keyed comparison. Binary trace remained in temporary private runner scratch and was removed; no game shader, trace or original SPIR-V was exported in Artifacts.

Source-only [CI 42242015941](https://github.com/alwansan/raf/actions/runs/42242015941): **74/74 PASS**, including all five newly added scheduled CLI tests and eight candidate keyed audit tests.

## Final scope and next step

- origin: chat
- status: completed scoped candidate HLSL real keyed GPU readback
- experiment: `prompt/coordination/experiments/T1/20261106T151730Z-T1-chat-keyed-candidate-3a7f.json`
- canonical event: `prompt/coordination/B_TEAM/events/T1/20261106T151730Z-T1-chat-keyed-candidate-3a7f.json`
- run_urls: https://github.com/alwansan/raf/actions/runs/42241766200 ; https://github.com/alwansan/raf/actions/runs/42242015941 ; https://github.com/alwansan/raf/actions/runs/42242127723
- next: independently recover and instrument **original SPIR-V** source reads for invocation-keyed capture on same input/dispatch; source-free preflight tool `scripts/t1_fft_original_keyed_preflight.py` is already 86/86 synthetic CI validated in separate T1 session `20261106T152810Z-T1-chat-original-key-preflight-c41b`, but not yet run on original SHA-private SPIR-V. Execute that private preflight first. Then use strict `scripts/t1_fft_invocation_pair_gate.py` with original/candidate independent trace/manifest and real numeric proof before shader patch.
- No authored shader/native Android changes, Unity heavy build, T2–T5 overlap or device acceptance; WATER-001 remains **OPEN / NOT_READY**.
