# T4 INPUT-005 isolated work
session_id: 20261110T0740Z-T4-scheduled-eligibility-ci-q7m3
origin: scheduled
baseline_head: 7d1133d3144c897d9635c326e6f7ed7d09fb958a
issue: INPUT-005
scope: .github/workflows/raft-t4-mouse-trace-classifier.yml; tests/test_t4_capture_eligibility_contract.py (read only); isolated session record.
hypothesis: Four new eligibility tests added at 597faee0 are not included in the existing sparse checkout or executed by classifier CI. Wire them into existing 5-minute source-only job, no duplicate CI/native build.
experiment_key: T4-INPUT005-ELIGIBILITY-CI-20261110-q7m3
shared_resource: existing T4 classifier workflow only; T5 Resolution, shared Mini, full build untouched.
owner_evidence: artifact 42058825739 world save/reopen confirmed for that artifact only. Phone buttons and scroll not confirmed.
acceptance: workflow explicitly checks out and executes four source-contract tests; GitHub Actions must pass before calling them verified. No device claims.
