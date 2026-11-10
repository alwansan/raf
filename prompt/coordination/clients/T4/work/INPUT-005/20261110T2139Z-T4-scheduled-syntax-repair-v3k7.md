# T4 INPUT-005 — source regression syntax repair
session_id: 20261110T2139Z-T4-scheduled-v3k7
origin: scheduled
issue_id: INPUT-005
status: active
updated_at: 2026-11-10T21:39:00Z
base_sha: 2d915eff9e63cc12c05bff5a35a57d931a6af370
resumed_from_session: 20261110T2042Z-T4-scheduled-r6p8
intended_files: scripts/test_t4_mouse_boundary_trace.py; this work file; unique session file
experiment_key: t4-boundary-python-literal-backslash-n-syntax-fix-v1
resource_key: source-only-no-unity
hypothesis: Newly added session isolation tests contain literal backslash-n outside Python strings and therefore cannot be parsed by Python; fix source encoding without changing assertions.
observed: GitHub fetch_file blob 21518837081b29d998bc0d577153be6909c2c702 contains literal \\n in method definition and assertions. No runtime proof claimed.
owner_phone_baseline: Artifact 42058825739 local world/save/re-entry success; mouse button/wheel not device-confirmed. Preserve keyboard, .rgd, audio, Settings; T5 owns Resolution.
next: fix only literal newline escape block; run syntax and unit tests locally; verify HEAD and CI; no Unity build.
