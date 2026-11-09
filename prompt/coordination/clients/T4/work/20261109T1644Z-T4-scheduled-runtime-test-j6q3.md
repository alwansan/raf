# T4 scheduled independent scope
session_id: 20261109T1644Z-T4-scheduled-j6q3
origin: scheduled
base_head: d8a7e46839ccbaba873830279c52a228aac6ea05
issue: INPUT-005
experiment_key: t4-runtime-gate-test-20261109-j6q3
hypothesis: Previously committed eight runtime acceptance-gate regressions remain unexecuted; a narrowly scoped source-only GitHub Actions workflow can provide an actual PASS/FAIL without Unity or game assets.
files: .github/workflows/raft-t4-capture-gate-runtime.yml; scripts/t4_capture_acceptance_gate.py (read-only); scripts/tests/test_t4_capture_acceptance_gate_runtime.py (read-only)
shared_resource: GitHub Actions lightweight ubuntu runner; no Unity, no APK, no CL writes.
constraints: preserve original world/save success on Artifact 42058825739, keyboard, settings, audio, .rgd; T5 owns resolution and shared Mini.
collision: dedicated workflow name/path; no equivalent known runtime test execution. Check Actions again before creating workflow.
next: create narrowly scoped manual+path-filtered source-only regression workflow, inspect result, write independent session record.
