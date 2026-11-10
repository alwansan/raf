# T5 independent scope — 20261110T1349Z-T5-scheduled-n8v2
origin: scheduled
baseline_sha: 8067b1c49c48ac20250e348175747ed6275b939f
owner_report: docs/DEVICE_FEEDBACK_42058825739_AR.md
resumed_from: clients/T5/sessions/20261110T1250Z-T5-scheduled-j6q2.md
hypothesis: the pending full regression CI 42819012779 may confirm or reject unsupported OBB compression-method controls.
experiment_key: T5-INTEGRATION-001-zip-method-CI-proof-4621e6a
files: this isolated work record and new T5 session only; no T4 mouse, Unity, shared build, or game assets.
shared_resource: none. No new CI dispatch.
verified: API workflow run 42819012779 completed success on head_sha 4621e6ae8de9a133db35889e3e48c2c4d546332c at 2026-11-10T12:49:51Z. Prior checkpoint had waiting_ci.
limitations: CI validates synthetic fixtures/source; not signed APK/OBB, device mount, Resolution, right-side button placement, FPS or GPU.
next: inspect workflow job steps to distinguish regression tests from unrelated green steps, then check actual signed APK/OBB metadata when accessible.