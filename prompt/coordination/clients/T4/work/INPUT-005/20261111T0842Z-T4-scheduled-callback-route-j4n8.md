# T4 INPUT-005 captured-action boundary
session_id=20261111T0842Z-T4-scheduled-callback-route-j4n8
origin=scheduled
baseline_head=8a2a532c086e957443185ff687c06510803ce0f1
scope=read-only AndroidPhysicalMouseCapture.cs, PhysicalMouseMotionSource.cs; this work and session only
hypothesis=Android captured callback observations do not prove original Raft Legacy Input consumption.
source_evidence=OnCapturedPointerListener records non-MOVE action then returns false; TryCapturedFrame requires requested && nativeCaptured; GetMouseButton* prioritizes native Legacy Input, then fallback. No gameplay proof from counters.
owner_evidence=Artifact 42058825739 world enter/save/reopen confirmed; 8 Nov phone camera capture improved but three buttons and wheel failed. Preserve .rgd, keyboard, Settings, audio, touch.
experiment=ONE signed build and same-process JSONL with session/sequence/epoch; separately test left/right/middle/vertical/horizontal wheel in saved world and Raft cursor in menu; compare physical_mouse_captured_action_callbacks[_final] to physical_mouse_legacy_reader_evidence[_final] with scripts/t4_correlate_mouse_runtime_epochs.py; record gameplay effect independently. Missing callback => Android View delivery; callback without getter => Unity/original call-site; getter without gameplay effect => gameplay bindings.
CI=42974039265 success source-only; no duplicate run. shared_resource=none. status=waiting_device_evidence; INPUT-005 OPEN.
