# T5 independent work: OBB GUID/JSON regression CI
session_id=20261109T1855Z-T5-chat-obb-contract-b1d7
origin=chat
status=active
base_sha=3aa107eec32e14c06454075ad069b49a9302606c
resumed_from_sessions=20261109T1655Z-T5-scheduled-obb-path-f83c,20261109T1750Z-T5-scheduled-obb-json-a9e4
issue_id=OBB-GUID-CLASSIFICATION-REGRESSION
scope=Run previously unexecuted OBB path and duplicate JSON regression tests on the actual repository checkout without editing shared classifier/test source owned by the scheduled cycle.
intended_files=.github/workflows/raft-t5-obb-guid-contract-regression.yml,work/T5/20261109T1855Z-T5-chat-obb-contract-b1d7.md,clients/T5/sessions/20261109T1855Z-T5-chat-obb-contract-b1d7.md
experiment_key=t5-obb-guid-unique-json-path-regression-v1:source-3aa107e:test-t5-obb-guid-contract:ubuntu-24.04:python3
resource_key=source-only-ci-t5-obb-contract; no Unity, APK/OBB extraction, CL writes, mouse or shaders
work_overlap=Scheduled T5 work owns scripts/t5_classify_obb_guid_logs.py and scripts/test_t5_obb_guid_contract.py; this session will not modify either. Other T1-T4 files unaffected.
actions_at_start=2026-11-09T18:55Z branch queued=0 in_progress=0 pending=0; newest inspected run 42673027759 was completed failure in T2 unrelated.
plan=Add isolated lightweight source-only Actions workflow to execute 10 recent tests plus pre-existing legacy contract tests and py_compile; assess actual test output before any change.
source_only=true; phone_proof=false; signed_delivery_proof=false
updated_at=2026-11-09T18:55:00Z

## CI result — 2026-11-09T18:58:49Z
status=completed
run_url=https://github.com/alwansan/raf/actions/runs/42678868120
run_id=42678868120
run_head_sha=0b2510460e6c54c519a6b494add5b0b0b103cda8
run_conclusion=success
assertions=10/10 latest path/duplicate JSON +16/16 legacy classifier=26/26 PASS; py_compile PASS
job_id=129367641103
proof_boundary=Source-only synthetic logs/manifests on Ubuntu-24.04. No signed delivery.json bytes, no real APK/OBB pairing, no Android15 device mount test. T1-T4/shared code untouched; no APK/Unity.
next_step=Obtain exact signed delivery.json from installed 42058825739 downstream artifact and classify original LogRaft segments. Re-test only if classifier/tests change.
updated_at=2026-11-09T18:59:00Z
