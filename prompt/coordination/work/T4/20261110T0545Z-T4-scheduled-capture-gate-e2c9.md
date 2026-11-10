# T4 INPUT-005 capture eligibility telemetry
session_id: 20261110T0545Z-T4-scheduled-capture-gate-e2c9
origin: scheduled
issue_id: INPUT-005
status: active
intended_files: android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs; prompt/coordination/clients/T4/sessions/20261110T0545Z-T4-scheduled-capture-gate-e2c9.md
experiment_key: t4-android-capture-gate-transition-observation-v1-unity2021-inputsystem-physicalmousepresent
resource_key: none (source-only, no CI dispatch)
updated_at: 2026-11-10T05:45:00Z
hypothesis: Capture may be skipped when authored lock intent exists but Unity InputSystem Mouse.all lacks a physical mouse. Add bounded transition-only diagnostics without changing gating, keyboard, touch, .rgd or capture semantics.
source: docs/DEVICE_FEEDBACK_42058825739_AR.md; clients/T4/sessions/20261110T0439Z-T4-scheduled-device-presence-g5k2.md
verification: inspect exact current source and perform static checks; no on-device claim.
