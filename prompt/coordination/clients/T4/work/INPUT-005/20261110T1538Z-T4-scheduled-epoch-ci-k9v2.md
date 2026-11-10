# T4 INPUT-005 independent scope 20261110T1538Z-T4-scheduled-epoch-ci-k9v2
origin=scheduled; experiment=T4-ELIGIBILITY-EPOCH-CI-20261110; baseline=178fc8bed05cda7aff024f7e53bfa3905a0a6d19
Owner phone evidence: artifact 42058825739 world enter/save/exit/reopen proven; LOCAL-005 regression open. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57; newer 8 Nov phone feedback says camera moves but clicks and wheel fail.
Hypothesis: scripts/test_t4_mouse_eligibility_epoch.py introduced at c99cf24a but not executed in existing classifier workflow, leaving stale callback attribution unverified.
Files: .github/workflows/raft-t4-mouse-trace-classifier.yml only, plus this unique work and unique session record. No Unity code, input runtime, .rgd, keyboard, audio, Settings, T5 resolution or shared build requests. No Unity/CI heavy resource. Existing classifier job will be extended to execute 4 epoch tests and 7 eligibility tests if available, after confirming test filenames.
Overlap: T4 previous epoch patch completed; this is distinct CI verification. T5 owns resolution. Do not duplicate a running build. Expected branch head at planning: 178fc8bed05cda7aff024f7e53bfa3905a0a6d19.
