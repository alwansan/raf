# T4 INPUT-005 — capture routing acceptance guard
session_id: 20261111T0335Z-T4-scheduled-input-acceptance-n7q3
origin: scheduled
baseline_sha: 2b80f4c1febdf3f3aff6b4bb96986aa9914b7014
scope: tests/test_t4_mouse_capture_routing_guard.py and this work file; no gameplay/Settings/Resolution files.
experiment_key: T4-INPUT-005-ROUTING-GUARD-20261111
shared_resource: none; source-only test, no Unity or APK build.
hypothesis: a future edit could silently remove the captured callback action path or route touch/keyboard through the physical mouse bridge despite existing source-only tests.
owner evidence: artifact 42058825739 proved world/create/save/reopen on device only; 8 Nov CL shows camera mouse movement but buttons and wheel fail. No claim of current device acceptance.
prior work: docs/T4_ANDROID_CAPTURED_LEGACY_BUTTON_WHEEL_BRIDGE_2026-11-08.md and T4 session 20261111T0238Z-T4-scheduled-capture-path-k9q4.md. Existing AndroidPhysicalMouseCapture already stages real callback actions and exposes Legacy wrappers; avoid duplicate implementation.
plan: add deterministic source routing guard asserting non-MOVE events remain unconsumed, physical capture requires authored lock and real mouse, three buttons/wheel wrappers exist, original Unity native-first fallback retained, and focus/pause release hooks remain. Run locally; no CI duplication.
limits: structural checks cannot prove callbacks or gameplay on device; request T5 shared mini driver only when needed, preserve keyboard, .rgd, sound and Settings.
