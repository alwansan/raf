# T4 checkpoint — 20261111T0137Z-T4-scheduled-token-boundary-p5r8
origin: scheduled
resumed_from_sessions: 20261111T0040Z-T4-scheduled-marker-guard-v4q8; 20261110T2336Z-T4-scheduled-ci-result-m8q2
base_sha: f8327346ebb103e7dfe87e6892d51aee0c890bfb
scope_commit: 89eef4b0a0eed3e581f5cee63cf3c01285914472
source_commit: 3608a25f3beedb448ffded0ecea4d396be661574
test_commit: 037397c7eaa7f430b2d7cd7fe9a204469a378d75
origin=scheduled
issue=INPUT-005
result: Tightened TOKEN value ending from word boundary to whitespace/end-of-line. Previously frame=12.3 could be parsed as frame=12, and stage=android.extra as android, falsely attributing a mouse event to a valid stage. Two targeted regression tests added for frame, stage and button partial matches.
previous_ci: https://github.com/alwansan/raf/actions/runs/42933224573 success at 2026-11-11T00:40Z (before these changes)
validation: code and tests committed; new CI outcome not yet confirmed. No Android device run, no native input fix, no claim of click success.
device_baseline: owner entered/saved/reopened local world with artifact 42058825739; preserve original .rgd, keyboard, audio, Settings. T5 owns Resolution and buttons placement.
next: inspect fresh classifier CI; then instrument real MotionEvent/Unity/Raft stages under pointer capture with sanitized session/frame markers, and test physical LEFT/RIGHT/MIDDLE/wheel + Raft cursor on device. Do not duplicate running CI.

CI verified: https://github.com/alwansan/raf/actions/runs/42940365685 completed success on test commit 037397c7. Source-only Python regression, not device proof.
