# T4 scheduled session 20261111T1337Z-T4-scheduled-zip-log-input-k9r2
origin: scheduled
baseline_sha: 136527eb2711a2b3836891b66a8ec90f7425e15f
scope_commit: 064b8f0af6beff7174b3fbd38989a764dad4e4b7
source_commit: 7430ca8be5322914f3f771890a6aba19ffe120df
test_commit: a8dae71c0d9cc5e122c78585a053040a31664cc7
issue: INPUT-005 OPEN

## Proven source progress
Extended scripts/t4_capture_reader_summary.py to stream one UTF-8 .log/.txt member directly from a ZIP export, requiring --member for ambiguous multiple-session bundles and rejecting declared members over 64 MiB before decompression. Added three regression cases for one-member extraction, ambiguous-session refusal/selection, and oversized archive member rejection. Source published, but tests and CI have NOT been executed in this run. This is diagnostics usability, not game input fix.

## Owner/device boundary
Owner's Artifact 42058825739 (e9c358eda01785b65e4eb14f18723da426635628) entered/saved/reopened world on phone; packaging failed. Later Nov 8 owner reports camera pointer capture works, LEFT/RIGHT/MIDDLE/scroll fail. CL session LogRaft-20261108-164850-270 confirms render floods, but session-summary has no mouse click/wheel telemetry; no gameplay success inferred. Previous authentic bridge source CI42518143297 passed source-level checks only. Original .rgd, keyboard, touch, audio, Settings untouched; T5 owns Resolution and on-screen button placement.

## Coordination and next
Work: prompt/coordination/clients/T4/work/INPUT-005/20261111T1337Z-T4-scheduled-zip-log-input-k9r2.md. No Actions canceled or dispatched; no Unity build. Next: execute python -m unittest discover -s tests -p test_t4_capture_reader_summary_boundary.py and inspect one same-build/process CL mouse callback+reader log. If callbacks increment but readers do not, debug native bridge -> frame latch; if both increment, inspect original Raft action call sites. Do not combine sessions or treat nonzero initial counters as new actions. Keep INPUT-005 OPEN, game NOT_READY 0/3.
