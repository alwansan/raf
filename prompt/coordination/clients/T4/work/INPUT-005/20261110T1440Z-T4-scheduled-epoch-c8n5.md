# 20261110T1440Z-T4-scheduled-epoch-c8n5
origin=scheduled; owner=T4; issue=INPUT-005
baseline_sha=a788a5732de043b55370f7f7a6a72b5f72bc4b26
Hypothesis: scripts/t4_diagnose_mouse_eligibility.py combines global request/callback counts with last eligibility gate, potentially attributing old capture evidence to a new disconnected mouse epoch.
Scope: scripts/t4_diagnose_mouse_eligibility.py and independent regression test; no Unity/game input, keyboard, save, Settings, T5 resolution or shared build files.
Experiment key: T4-ELIGIBILITY-EPOCH-20261110. No shared CI/build resource. Owner phone evidence 42058825739 world/save/reentry remains device-confirmed for that artifact only.
Plan: classify only markers following last eligibility transition, retain all-time counts for diagnostics; add regression for old callback followed by mouse absent; verify with Python; do not infer phone success.
