# T4 scope 20261111T1144Z-T4-scheduled-partial-counters-m5k2
origin=scheduled
issue=INPUT-005

Owner phone evidence: artifact 42058825739 entered, saved and reopened a world; no mouse-button proof. Preserve .rgd, keyboard, audio and Settings. Resolution belongs to T5.

Hypothesis: t4_capture_reader_summary.py replaces the entire cumulative counter snapshot on each report. Partial reports omit keys and make previously observed counters disappear, leading to false conclusions when diagnosing physical LEFT/RIGHT/MIDDLE/scroll. Implement merge of present counters, keep maxima, and add regression test for partial reports. Do not touch runtime mouse implementation, Unity build, shared files or T5's display scope.

Files: scripts/t4_capture_reader_summary.py; tests/test_t4_capture_reader_summary_boundary.py; this work file; unique session file.
Experiment key: T4-PARTIAL-COUNTERS-20261111; resource: none, source-only. Validate locally with unittest, avoid duplicate Actions. Re-read current blob SHA before update; no force.
