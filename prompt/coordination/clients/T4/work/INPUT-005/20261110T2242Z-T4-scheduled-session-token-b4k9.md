# T4 INPUT-005 scope
session_id: 20261110T2242Z-T4-scheduled-b4k9
origin: scheduled
base_sha: a0380ab6e45cee9012f525df42bc36aded45002c
issue_id: INPUT-005
status: active
intended_files: scripts/t4_mouse_boundary_trace.py; scripts/test_t4_mouse_boundary_trace.py; .github/workflows/raft-t4-mouse-trace-classifier.yml; this work file; independent session file
hypothesis: TOKEN regex does not capture session= although analyzer keys on it; different app restarts can be falsely merged. Existing CI omits boundary regression tests.
experiment_key: t4-boundary-session-token-and-ci-source-a0380ab6
resource_key: none; source-only Python
constraints: preserve keyboard, .rgd, audio, Settings; T5 owns Resolution; no device claims or native builds.
