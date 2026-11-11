# T4 scheduled session 20261111T1144Z-T4-scheduled-partial-counters-m5k2
origin=scheduled
issue=INPUT-005

## Restored evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md and team policy. Owner phone artifact 42058825739 at source e9c358eda01785b65e4eb14f18723da426635628 confirmed world entry/save/exit/reopen, NOT physical mouse buttons. Latest prior T4 scheduled session 20261111T1040Z-T4-scheduled-counter-boundary-r6p2.md. Keyboard, .rgd, audio and Settings preserved; T5 owns Resolution. Mini APK is unified team lab.

## Work and commits
Scope: prompt/coordination/clients/T4/work/INPUT-005/20261111T1144Z-T4-scheduled-partial-counters-m5k2.md, commit b10add64d55efe0bf2746f92cb24e0ec243e1732.
Source change: scripts/t4_capture_reader_summary.py, commit 65f090bf5445dd74e309bd18856bed161e38e739. Previous parser replaced the entire cumulative snapshot on every partial log report, losing keys not repeated in a later report. Changed to update only present keys, retaining last observed values while maxima and decreases retain their previous semantics.
Regression: tests/test_t4_capture_reader_summary_boundary.py, commit bb46276596fa339d39a66411ca04b7731457ac61; sparse callback reports left/right/middle/scroll test added.

## Verification / limitations
Both edits were accepted by GitHub Contents API using current per-file blob SHA. Runtime environment cannot resolve github.com for checkout, so local Python unittest and CI execution were NOT verified in this run. No Unity build or Android device run, no proof of mouse buttons, no runtime game code changed. No Actions duplicated. This parser improvement is not a gameplay fix.

## Next
Run python -m unittest discover -s tests -p 'test_t4_capture_reader_summary_boundary.py' on checked-out source, or wire existing cheap CI only after checking equivalent running Actions. Compare Android callback and Unity reader counters from same build/PID and add instrumentation if needed; then implement real LEFT/RIGHT/MIDDLE/scroll routing fix. Coordinate T5 mini lab. Keep INPUT-005 OPEN.
