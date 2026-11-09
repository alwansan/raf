# T5 runtime staging manifest repair — 2026-11-09T23:52Z
session_id: 20261109T2352Z-T5-scheduled-6e4b
origin: scheduled
baseline_sha: 643a6d747a9b642cd8f5891a5ffab3ca9ba8da13
scope: scripts/verify_android_offline_candidate.py only, plus independent session and this work record.
experiment_key: T5-INTEGRATION-001-native-only-T1-trace-parity
shared_resource: none; source-only; no Unity build dispatched.
Evidence: CI 42715257589 fails managed_only=0 native_only=1 in parity suite. Native copy loop includes T1FftDirectDispatchTrace.cs; original-managed manifest does not. The native source has UNITY_ANDROID && !UNITY_EDITOR guard and uses existing AndroidRuntimeLog. Hypothesis: add authentic source to original-managed static manifest, preserving parity, not weakening verifier.
Conflict policy: read HEAD before update; expected blob SHA; no force. T4 owns mouse files. Phone success only artifact 42058825739.
Next: update manifest, test parity, inspect CI result.
