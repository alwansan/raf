# T5 source UI regression CI scope — 2026-11-11T09:45Z
session_id: 20261111T0945Z-T5-scheduled-7f31
origin: scheduled
baseline_sha: 4582baa585b90a7841f8a24d3e5fe8d9b1299fc5
status: IN_PROGRESS

## Evidence / hypothesis
Owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md proves world/save/reentry only for 42058825739; UI changes 6da432b/18d5d88 and 85fc2a2/84d72a0 remain source-only. The last T5 session 20261111T0854Z-T5-scheduled-4e6a says panel regression has not been run in CI. A bounded source-only workflow can verify all four right-button/panel tests on a clean runner without launching Unity or touching T4 mouse.

## Exclusive files / experiment
New .github/workflows/raft-t5-right-panel-source-regression.yml and this work file; new clients/T5/sessions/20261111T0945Z-T5-scheduled-7f31.md. No edits to existing Unity/UI source, T4 files, shared request JSON or other workflows. Key T5-UI-CI-20261111-7f31; no shared Unity resource. Run on changes to exact tests/source and manual dispatch; concurrency cancel-in-progress false, pinned checkout, no LFS. Validate existing tests rather than duplicate a game build.

## Limits
Python source tests cannot prove device geometry or resolution callback, FPS or signed APK/OBB identity. No native build requested.
