# T4 scheduled session 20261111T0640Z-T4-scheduled-ci-wire-q8m3
origin=scheduled
baseline=d485f212e14c43e2fbc1083e846b9d9321922f7f
plan_commit=87e6f1307a549061abf8f9e90827702a68403db9
workflow_commit=22c1b3f5fc57a0b64508c5527f2e2f87a3250916
scope=INPUT-005 CI wiring for two existing tests; no source game edits
work=prompt/coordination/clients/T4/work/INPUT-005/20261111T0640Z-T4-scheduled-ci-wire-q8m3.md

## Verified
- Read owner 5 Nov device feedback: artifact 42058825739 source e9c358eda01785b65e4eb14f18723da426635628 proves phone world create/save/exit/reopen; publish failure is separate. Keep LOCAL-005 open and original .rgd untouched.
- 8 Nov owner CL mini evidence documented in T4 MEMORY: physical uncaptured LEFT and vertical wheel, no captured=true proof. Real game captured buttons and wheel remain OPEN.
- Previous scheduled session 20261111T0543Z-T4-scheduled-route-a7m4 added tests/test_t4_capture_callback_semantics.py; prior 0442Z added tests/test_t4_captured_action_contract.py; neither was in sparse checkout or execution of .github/workflows/raft-t4-mouse-trace-classifier.yml.
- Added both test files to workflow push path triggers, sparse checkout, py_compile and separate unittest discovery invocations. Existing jobs/tests preserved, timeout 5m, LFS disabled, no Unity/APK. Workflow blob c6d265f8f666551535f9790a099a3b4e9796b0ff.
- At final immediate Actions query latest visible run 42967944744 (05:46 UTC) and no new workflow run for 22c1b3f5; result **waiting_ci**, not PASS. Earlier 42940365685 PASS is older classifier source only.

## Follow-up
Check GitHub Actions for commit 22c1b3f5 or descendants. If CI fails, repair actual test/source mismatch without claiming game-device success. Then collect captured Android and Unity Legacy reader events from SAME signed Raft build for LEFT/RIGHT/MIDDLE, wheel V/H, focus and keyboard; T5 owns Resolution and shared Mini builds. Preserve world .rgd, audio, Settings, keyboard and touch; do not trigger native Unity build or duplicate CI.
status=waiting_ci
