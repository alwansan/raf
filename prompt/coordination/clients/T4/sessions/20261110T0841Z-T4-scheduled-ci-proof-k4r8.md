# T4 scheduled checkpoint — CI regression proof

- session_id: 20261110T0841Z-T4-scheduled-ci-proof-k4r8
- origin: scheduled
- resumed_from_sessions: 20261110T0740Z-T4-scheduled-eligibility-ci-q7m3.md; 20261110T0545Z-T4-scheduled-capture-gate-e2c9.md
- base_sha: c32eeafc4a3097a4944fa4ef6f9466279a7ce855
- work_plan_commit: 9bdc64d06828db2fd4253402097068ee6af62fc4
- issue_id: INPUT-005
- outcome: **SOURCE_TESTED**, not DEVICE_CONFIRMED.

## Evidence

Run [42776921454](https://github.com/alwansan/raf/actions/runs/42776921454), created 2026-11-10T07:40:24Z, completed **success**, head 7d3f11ecd1f022f52240a15e6ec4c002636cae62. Job classifier-source-only and step Verify source-only classifier regression suite completed success. Workflow checked out the classifier, retry contract and capture eligibility contract tests; ran Python py_compile and three unittest discover commands, including `tests/test_t4_capture_eligibility_contract.py`. This closes the prior **CI-not-executed** evidence gap for the newly wired tests. It does not prove Android pointer capture or Raft click actions.

Owner's device feedback: world entered, saved, exited and reopened on artifact 42058825739; do not overwrite this successful phone evidence because packaging publication failed. The later mini-lab report says camera mouse capture works but physical left/right/middle click and wheel still fail. The keyboard and .rgd compatibility must remain intact. No source modifications to input, keyboard, Settings, audio, touch, or Resolution this cycle. T5 owns overlapping Resolution/layout work.

## Verification boundaries and next step

No duplicate CI dispatched. Source-only CI success is not signed APK, Unity runtime, device logs, or gameplay proof. Need fresh signed Raft JSONL containing capture gate transitions, request/grant, Android mouse button/axis event, Unity Legacy Input frame, Raft action; classify first missing boundary for LEFT/RIGHT/MIDDLE/wheel. Preserve mouse cursor and keyboard; coordinate source changes with concurrent T4 chat and T5 before editing. If CI gate confirms Unity device absent but Android mouse present, test narrow eligibility correction under focus/pause guards. Keep INPUT-005 OPEN.

- independent work: [20261110T0841Z-T4-scheduled-ci-proof-k4r8](../../T_TEAM/work/20261110T0841Z-T4-scheduled-ci-proof-k4r8.md)
- live branch observed before work: c32eeafc4a3097a4944fa4ef6f9466279a7ce855
