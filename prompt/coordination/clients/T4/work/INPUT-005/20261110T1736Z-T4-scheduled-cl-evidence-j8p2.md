# T4 INPUT-005 — signed device evidence coverage
session_id: 20261110T1736Z-T4-scheduled-cl-evidence-j8p2
origin: scheduled
base_sha_observed: 9b89f62772c2c61f6269fd2249f8560af1522892 (repository-wide recent commit search; branch ref not independently verified)
resumed_from: 20261110T1643Z-T4-scheduled-ci-confirmation-n2f7
scope: CL 20261108-164850-270 session-summary and mouse telemetry coverage; no gameplay source, CI or T5 resolution files.
experiment_key: T4-MOUSE-CL-SUMMARY-COVERAGE-20261110
hypothesis: CL summary may not carry event-level evidence needed to discriminate Android button routing from Unity consumption.

## Findings
- CL main/raft log/lf/LogRaft-20261108-164850-270/session-summary.json explicitly reports 7 raw segments, 206855773 recorded bytes, 2061194 final game lines, 0 failed writer batches, but warns OS ring losses cannot be ruled out.
- Summary's milestone and error-category fields have no LEFT/RIGHT/MIDDLE/wheel, pointer-capture gate, action-button, or Unity Mouse0/1/2 counters. Thus summary cannot prove button arrival OR loss. The owner's 8 November direct observation remains the authoritative gameplay failure: camera relative movement works, clicks/scroll do not.
- 74359 invalid water pass errors + 11165 invalid kernel errors + 7372 cursor RGBA32 warnings were recorded in this session. This flood makes a bounded targeted input trace preferable to inferring from generic error counts.
- No gameplay code changed. Successful CI 42846576303 covers classifier tests only.

## Next discriminating experiment
On a signed build, record bounded raw Android dispatchGenericMotionEvent/onCapturedPointerEvent events with source/device/action/buttonState/actionButton/VSCROLL/HSCROLL, plus Unity Mouse0/1/2 and wheel state in the same monotonic time window. Exercise each button down/up, wheel, focus loss/reacquire, and keyboard. Correlate by event timestamp and process ID. Do not disable working relative camera capture; preserve .rgd, sound and Settings. Request shared mini-lab change through T5 only if its current driver lacks these fields; avoid duplicate builds.

Status: evidence gap identified; INPUT-005 OPEN. No phone fix claimed.
