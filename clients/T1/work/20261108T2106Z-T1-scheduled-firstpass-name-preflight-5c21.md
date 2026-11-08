# T1 WATER-001 independent scope
session_id: 20261108T2106Z-T1-scheduled-firstpass-name-preflight-5c21
origin: scheduled
base_sha: ce5859d7ee7aff1911b43064727f7ea02bb0af9f
issue_id: WATER-001
intended_files: scripts/t1_fft_first_divergence.py; tests/test_t1_fft_first_divergence_capture_guard.py; this work and matching session file
hypothesis: repeated or blank pass labels should fail during manifest preflight, before any private capture pixel reads, rather than after loading all captures.
experiment_key: t1-fft-firstpass-unique-names-preflight-20261108-ce5859d
resource_key: none; source-only, no Unity/CI dispatch
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 world save/reentry from Artifact confirmed; water/kernel errors remain.
resumed_from: clients/T1/sessions/20261108T2006Z-T1-scheduled-firstpass-json-4a7d.md and prompt/coordination/clients/T1/sessions/20261108T2022Z-T1-chat-fft-source-gate-d8b4.md
status: active

## Outcome
source_commit: 9ac294ff37bb5f34f7190058d45189f15d91c093
test_commit: 8eebe992e6d6802a064f83e19b07f85b6f6694a2
observed_ci: https://github.com/alwansan/raf/actions/runs/42523525581 (in_progress at inspection, source SHA 9ac294ff, so cannot cover new test commit)
status: source_fixed_test_pending
validation: static review; local curl raw.githubusercontent.com DNS failure. New unittest not yet executed. No CI duplicate launched.
limits: input manifest label preflight only; not Unity runtime kernel identity or FFT pixel parity.
next: execute python -m unittest tests.test_t1_fft_pass_label_preflight in available runner; then capture original same-build Unity FFT shader GUID, numeric selector, SetTexture and Dispatch.
