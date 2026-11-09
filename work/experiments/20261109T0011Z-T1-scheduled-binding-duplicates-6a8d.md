# T1 WATER-001 binding evidence validation
session_id: 20261109T0011Z-T1-scheduled-binding-duplicates-6a8d
origin: scheduled
issue_id: WATER-001
baseline_sha: d4d1243243e0f53c10093c325145ee89895e94af
intended_files: scripts/t1_fft_runtime_evidence_gate.py; scripts/test_t1_fft_runtime_evidence_gate.py; clients/T1/sessions/20261109T0011Z-T1-scheduled-binding-duplicates-6a8d.md
experiment_key: t1-runtime-gate-duplicate-and-blank-bindings-v1
resource_key: none (Python-only)
status: completed_source_only
Hypothesis: duplicate or whitespace-only resource binding names can satisfy the runtime-evidence envelope without identifying distinct bound resources. Reject these malformed names before calling evidence complete. This remains structural validation, not GPU proof.
Owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md, source e9c358e; world save/reopen from Artifact successful, water errors unresolved. Preserve T4 pointer and T5 UI/Resolution scope.

Result: code commit 9eddf988699280263dcabcd65e23431b967a08c6; regression test commit 9602952aaf2a51c57411e0c06650ede1b766566c. The gate now rejects duplicate, blank and padded resource binding names; three tests added. Local execution blocked by container DNS (curl error 6). No new CI dispatched; earlier 42529039014 succeeded but predates these changes. Source-only, no device proof. Next: run unittest in existing FFT CI or available runner, then obtain authentic per-pass runtime bindings and paired Vulkan/Unity captures.
