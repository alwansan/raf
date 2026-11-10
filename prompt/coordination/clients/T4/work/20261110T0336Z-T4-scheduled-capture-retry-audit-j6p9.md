# T4 INPUT-005 independent capture retry audit
session_id: 20261110T0336Z-T4-scheduled-capture-retry-audit-j6p9
origin: scheduled
issue_id: INPUT-005
base_sha: 887d74f3a53fc00c70de1a179c0097d19119ed4b
status: active
intended_files: AndroidPhysicalMouseCapture.cs (read-only audit), prompt/coordination/clients/T4/work/20261110T0336Z-T4-scheduled-capture-retry-audit-j6p9.md, corresponding session checkpoint
experiment_key: T4-pointer-capture-focus-retry-static-audit@887d74f3
resource_key: none (no Unity/CI)
updated_at: 2026-11-10T03:36:00Z
hypothesis: capture can remain unavailable if Android focused View changes after request; verify request/probe/release and whether retry actually installs listener on new View.
Scope boundary: no change to T5 Resolution/HUD, keyboard, touch, .rgd, sound, Settings or heavy CI. Device result remains unverified.
