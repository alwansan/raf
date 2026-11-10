# T4 INPUT-005 scope — 20261110T1036Z-T4-scheduled-native-device-gate-b7q2
origin: scheduled
issue_id: INPUT-005
status: active
base_sha_observed: 9b89f62772c2c61f6269fd2249f8560af1522892 (repository-wide search, branch ref not guaranteed)
intended_files: prompt/coordination/clients/T4/work/20261110T1036Z-T4-scheduled-native-device-gate-b7q2.md; prompt/coordination/clients/T4/sessions/20261110T1036Z-T4-scheduled-native-device-gate-b7q2.md
experiment_key: android-inputsystem-device-presence-vs-native-pointer-capture-gate-source-audit-20261110
resource_key: none (source-only; no Unity/CI)
hypothesis: physical Android mouse can be absent from Unity Mouse.all, blocking requestPointerCapture before any callback, while game Legacy Input fallback for captured buttons/wheel already exists.
Safeguards: do not alter T5 resolution/UI or original .rgd; do not claim phone confirmation. Distinguish Android callback from actual gameplay. No duplicate CI.
