# T4 scheduled 20261111T0040Z-T4-scheduled-marker-guard-v4q8
origin=scheduled
branch=feature/android-native-port
base_head=6698b0dc40a0909a7b712d179efdc28142839459
scope=INPUT-005 trace parser integrity; no game source edits
work=prompt/coordination/clients/T4/work/INPUT-005/20261111T0040Z-T4-scheduled-marker-guard-v4q8.md

## Evidence and result
Read owner device report docs/DEVICE_FEEDBACK_42058825739_AR.md and T4 prior session 20261110T2336Z-T4-scheduled-ci-result-m8q2.md. Owner proved create/save/exit/reopen .rgd on artifact 42058825739; retain LOCAL-005 regression protection. CI 42916987581 passed prior source-only classifier, not Android gameplay.

Observed defect in scripts/t4_mouse_boundary_trace.py: marker detected by substring and fields extracted from entire log line, including unrelated logcat prefix; repeated frame fields silently overwritten. Such input can produce false Android→Unity→Raft correlations. New parser requires exact T4_MOUSE_STAGE marker, reads fields only after marker, rejects duplicate keys; legacy marker without session still accepted. Added three unittest cases for false prefix/suffix marker, metadata leakage, duplicate fields.

Commits: scope 65ee646f7901479a4c68ea28fb55f975ea458739; parser final 634571847bde1a0aebc9ff3b15c53dd0fb1f9d65 (intermediate e705a49 and 752c997 had incorrect regex escapes, superseded); tests 521c12d23ce317fce45a67e172711f2b6c64e71e.

Validation: source published. Local test execution blocked: curl raw.githubusercontent.com DNS resolution failed (exit 6). New tests NOT claimed passing; CI not launched or duplicated. Preserve keyboard, audio, Settings, .rgd, touch. No Resolution or shared T5 files touched.

Next: inspect existing CI result for tests on newest SHA, run tests when runner available; highest-priority remaining task is instrumentation of real MotionEvent buttonState/actionButton/AXIS_VSCROLL and Unity Mouse0/1/2/scroll with session/event IDs, and Raft consumer path, then T5 unified mini lab device verification. INPUT-005 OPEN.
