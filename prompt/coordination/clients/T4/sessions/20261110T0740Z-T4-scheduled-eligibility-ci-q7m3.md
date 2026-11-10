# T4 scheduled checkpoint 20261110T0740Z-T4-scheduled-eligibility-ci-q7m3
origin: scheduled
session_id: 20261110T0740Z-T4-scheduled-eligibility-ci-q7m3
resumed_from: 20261110T0643Z-T4-scheduled-eligibility-contract-m8q5
baseline_sha: 7d1133d3144c897d9635c326e6f7ed7d09fb958a
scope_commit: f2e246a122c8aeb6540ae64aefbf9affcf196a90
implementation_commit: 7d3f11ecd1f022f52240a15e6ec4c002636cae62
issue: INPUT-005
status: waiting_ci

## Verified source-level change
Four regression tests were introduced by T4 at 597faee0 but the existing .github/workflows/raft-t4-mouse-trace-classifier.yml neither checked out nor ran tests/test_t4_capture_eligibility_contract.py. Updated existing workflow's push paths, sparse checkout, py_compile and unittest invocation to include this test module. No new workflow, native build, or phone claims. Source update committed successfully. Latest visible workflow run 42763994149 SUCCESS is for older be31b553, **not** this change; no new run visible at checkpoint. CI status remains unverified.

## Device and preservation
Owner confirms world create/save/exit/reopen only on artifact 42058825739, source e9c358eda01785b65e4eb14f18723da426635628. CL owner mini shows physical uncaptured LEFT and VSCROLL; captured buttons and game consumption unproven. Input camera capture observed separately. Existing original .rgd, keyboard, audio, Settings, Android input behavior unchanged. T5 owns Resolution and three right-side controls. No proprietary assets exposed.

## Next
Check latest GitHub Actions run of raft-t4-mouse-trace-classifier.yml for commit 7d3f11ec; fix any test failures with new independent scope. Then correlate physical_mouse_capture_eligibility marker and Android request/callback with Unity Legacy Input and actual Raft LEFT/RIGHT/MIDDLE/wheel on signed phone build. If no CI triggers, inspect workflow event/path filter; avoid duplicate Unity runs. INPUT-005 OPEN, NOT_READY 0/3.
