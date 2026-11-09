# T1 WATER-001 binding evidence validation
session_id: 20261109T0011Z-T1-scheduled-binding-duplicates-6a8d
origin: scheduled
issue_id: WATER-001
baseline_sha: d4d1243243e0f53c10093c325145ee89895e94af
intended_files: scripts/t1_fft_runtime_evidence_gate.py; scripts/test_t1_fft_runtime_evidence_gate.py; clients/T1/sessions/20261109T0011Z-T1-scheduled-binding-duplicates-6a8d.md
experiment_key: t1-runtime-gate-duplicate-and-blank-bindings-v1
resource_key: none (Python-only)
status: active
Hypothesis: duplicate or whitespace-only resource binding names can satisfy the runtime-evidence envelope without identifying distinct bound resources. Reject these malformed names before calling evidence complete. This remains structural validation, not GPU proof.
Owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md, source e9c358e; world save/reopen from Artifact successful, water errors unresolved. Preserve T4 pointer and T5 UI/Resolution scope.
