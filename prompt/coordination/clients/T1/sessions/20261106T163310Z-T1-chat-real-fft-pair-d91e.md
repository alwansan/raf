# T1 — first authenticated original-SPIR-V vs HLSL keyed FFT numerical pair

- session_id: 20261106T163310Z-T1-chat-real-fft-pair-d91e
- origin: chat
- status: waiting_ci
- issue_id: WATER-001 OPEN / NOT_READY
- base_sha: 8e2a01bcfd2de019e904190c4dc6fffb7abd6fb4
- resumed_from_sessions: 20261106T161112Z-T1-chat-original-keyed-recorder-7be2; 20261106T151730Z-T1-chat-keyed-candidate-3a7f; 20261106T130729Z-T1-chat-pair-gate-6c2e
- work: prompt/coordination/work/WATER-001/T1-20261106T163310Z-T1-chat-real-fft-pair-d91e.json
- scope_commit: d438a5620572c670fb6c685cecc7509713b386da
- host_input_dump_commit: 8511c2f84dde90970f09a36b73865d28d2d0ebad
- private_input_hash_helper_commit: 051b80ba754b652e8fe20092559da7197029cdcf
- original_evidence_commit: ff5b59d0cbc2804168943eabfd1d9b1885396bcd
- candidate_evidence_commit: 8866b0e8525add6f6ef5bb3e006df107bd6c1244
- private_pair_report_commit: b249628ca2a227810a5263f880b74c5421bd5797
- unit_tests_commit: c7631ed7aef24cccc13e3efc7f9d5c38474eb0ed
- source_only_workflow_commit: 6e0065cb991eebbf1779584ded7acf73ab451fd0
- original_vs_HLSL_workflow_commit: fe3cff4899a19b197b64d692a28b2fdaf980fb7f
- source_pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- source_only_run: https://github.com/alwansan/raf/actions/runs/42254324601
- real_pair_run: https://github.com/alwansan/raf/actions/runs/42254539826

## Starting verified evidence

SHA-authentic original SPIR-V direct `OpImageFetch` instrumented on Vulkan in [42252268973](https://github.com/alwansan/raf/actions/runs/42252268973) SUCCESS: 384 reads [64,256,64], no duplicate invocation keys, original traced-vs-original untraced output invariance 64 written pixels. Separately SHA-original-derived HLSL candidate `--invocation-keys` capture [42242127723](https://github.com/alwansan/raf/actions/runs/42242127723) SUCCESS: another 384 reads [64,256,64]. Those were previous separate GPU runs and have not been paired numerically. The full fixed original source is not public, and data remains private.

## Actual same-input capture protocol

- Extended `trace_host` with an OPTIONAL private Vulkan input dump flag that reads the actual mapped `source` and `butterfly` images after GPU completion and before unmapping, without changing original workloads.
- Added `scripts/t1_fft_private_input_evidence.py` to SHA256 bind actual two input readback byte sequences (framed by sizes), a deterministic canonical dispatch spec (1024x32 rgba32f, seed19, 1x1x1 groups), the compiled privately instrumented shader and actual trace bytes. The digest sidecar is private and never printed/uploaded.
- Updated both original and HLSL candidate trace analyzers with `--export-private-evidence` opt-in; existing default behavior remains unchanged and both original/candidate binaries/sidecars remain in `$TMPDIR`. Each private host uses identical original fixture generation, and reports exact input and dispatch hashes to a private sidecar for the strict pair gate.
- New `scripts/t1_fft_private_invocation_pair_report.py` accepts original & candidate evidence files with bounded duplicate-key-rejecting schema; verifies same actual input SHA, identical dispatch SHA, independent trace files/digests/site census via existing `scripts.t1_fft_invocation_pair_gate`; reports only aggregate per-site x/y/mip coordinate mismatch, value bit mismatch, missing/extra reads and mapping classifications. It does NOT reveal hashes, SSA IDs, invocation coordinates, pixel values or original shader source. A valid numerical mismatch is a successful *diagnostic experiment*, not a parity claim.
- Added `tests/test_t1_fft_private_invocation_pair_report.py` with 13 adversarial/positive tests including independent identical inputs, mismatched input/dispatch/traces, empty/partial data, identical files, matching counts but differing coordinate or value, private output redaction and correct optional C++ source/butterfly dump insertion.
- [Source-only CI 42254324601](https://github.com/alwansan/raf/actions/runs/42254324601) SUCCESS; no original private assets involved.

## Real pinned ZIP2 run in progress

[Run 42254539826](https://github.com/alwansan/raf/actions/runs/42254539826) started on `fe3cff4899a19b197b64d692a28b2fdaf980fb7f`, **pending exact original and translated private same-fixture replay**. It stages ZIP2 pinned bytes, captures direct original `set0` and HLSL `set1` keyed traces, verifies each as before, and now validates actual input/dispatch SHA sidecars and invokes private strict pair reporter. No Unity heavy or Android native build, no authored game shader, resource GUID, Settings/audio/input or other T-client files changed. No private original binaries/readback artifacts published.

Read on completion only `RAFT_T1_ACTUAL_PAIRED_FFT_KEYED` safe JSON marker. If the gate fails, diagnose the input/dispatch/capture identity or host patch first; if it passes and reports differing coordinates, record the exact aggregate per-site/axis counts while keeping the source numerical values secret. A same-Mesa-Vulkan original-vs-HLSL candidate result is still not authenticated Unity runtime FindKernel mapping nor Adreno water acceptance. WATER-001 OPEN.
