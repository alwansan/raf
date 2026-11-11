# T4 session 20261111T1242Z-T4-scheduled-reader-baseline-h6p3

origin: scheduled
resumed_from_sessions: 20261111T1144Z-T4-scheduled-partial-counters-m5k2.md; 20261111T1040Z-T4-scheduled-counter-boundary-r6p2.md
base_sha: a07a9cde89c75994b137ef4e999c082ead427c9c
scope_commit: 1b8d75589a696a2cad835abd3d5469ff3ea3f000
source_commit: c23203aa97af9931370b872d9a1705cfb525b15f
test_commit: 1d9c54c99c46ffdf89e09a1056388b7c57d9715e
origin_source: docs/DEVICE_FEEDBACK_42058825739_AR.md
issue: INPUT-005 OPEN

## Proven progress
Added first-observation counter snapshots and positive-only monotonic increments to scripts/t4_capture_reader_summary.py; regression tests added to tests/test_t4_capture_reader_summary_boundary.py for pre-existing reader counts and reset drops. This prevents interpreting an initial nonzero reader counter as a newly observed event. It does not establish causal Android->Unity delivery, button gameplay, or phone success. Changes published via GitHub connector; tests not executed in this runtime (local GitHub clone DNS failed). No native CI dispatch, no Unity build.

## Owner baseline and boundaries
Artifact 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628) entered/saved/reopened world on phone; packaging failed. Keep original .rgd, keyboard, audio and Settings. T5 owns Resolution and three right-hand UI buttons. Pointer capture and Raft cursor remain open; later owner evidence reports camera motion improved but clicks/scroll absent.

## Next
Run python -m unittest discover -s tests -p test_t4_capture_reader_summary_boundary.py; check existing Actions rather than duplicate dispatch. Compare callbacks/readers from the same device build and process, and inspect native/Unity input path if observed increments disagree. Coordinate with T5 for one unified mini lab testpack; do not claim device confirmation from source tests.
