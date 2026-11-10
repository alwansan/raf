# T4 scheduled checkpoint — 2026-11-10 16:43 UTC
session_id: 20261110T1643Z-T4-scheduled-ci-confirmation-n2f7
origin: scheduled
resumed_from_sessions: 20261110T1538Z-T4-scheduled-epoch-ci-k9v2; 20261110T1440Z-T4-scheduled-epoch-c8n5
base_sha: ceeb2cedb8d586f196effa9c9c897b8443239505
scope_commit: 21e40dd27da1d70f367c647d28256b49c0aab2ce
status: completed (CI verification only); INPUT-005 OPEN

## Verified new evidence
The previously pending regression workflow at https://github.com/alwansan/raf/actions/runs/42846576303 is **completed / success**, with job `classifier-source-only` and step `Verify source-only classifier regression suite` successful. Run head 9a9db82ad048bcfc2994917a05981eb31d5f87bd. Workflow explicitly invokes `python3 -m unittest discover -s scripts -p 'test_t4_mouse_eligibility_epoch.py' -v` and previous tests. This verifies source-only Python regressions, **not** runtime device capture or gameplay mouse buttons.

Owner's 5 November phone report confirms world entry/save/exit/reentry for artifact 42058825739 only; delivery packaging failed. No source or CI evidence supersedes this device result. T5 owns resolution; preserve keyboard, sound, Settings and original .rgd.

## Next step
Analyze a fresh signed Raft runtime log with `scripts/t4_diagnose_mouse_eligibility.py`, compare `physical_mouse_capture_eligibility`, request, relative and action callbacks with actual LEFT/RIGHT/MIDDLE/wheel game handling. If Android reports mouse while Unity Mouse.all is absent, implement a narrow gated fallback and regression; otherwise fix first demonstrated boundary. Do not repeat CI run 42846576303. No phone success claimed.

## Evidence boundaries
This cycle did not change gameplay code, build Unity or access a new phone capture. A missing callback marker alone is not a definitive failure because logging is sampled and input may be absent.
