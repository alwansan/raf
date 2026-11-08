# T1 WATER-001 — unified GPU driver source audit

session_id: 20261108T1807Z-T1-scheduled-unified-driver-audit-9f31
origin: scheduled
status: source_audit_complete_device_pending
baseline: 506b9324a5f9c3e730a452e19a9d61775eaa94e8 (latest observed Actions source, NOT asserted HEAD)
resumed_from: clients/T1/sessions/20261108T1612Z-T1-scheduled-gpu-lab-handoff-a83e.md
experiment_key: t1-unified-t1-01-04-dispatch-source-audit-20261108
scope: read-only audit of apk-for-testing/unified/pack/team-testpack.json, UnifiedLabActivity.java and T1 evidence; no changes to T4/T5 host, Unity game, shader binaries or CL.

## Owner/device baseline
Read docs/DEVICE_FEEDBACK_42058825739_AR.md: owner entered, saved and reentered world from run 42058825739 Artifact; publishing failed. Water passes 23884/39132 and FFT kernel 3850/6026 for 220911-559/230108-327; these are different sessions, not GPU duration. Later 2026-11-08 report referenced in previous T1 handoff has 74359 invalid water passes, 11165 invalid FFT kernels; do not infer regression without equal windows.

## New independently checked source finding
The new unified pack schema v2 contains T1-01..T1-04, all driver=t1_compute, revision=1, mode=auto. The unified host explicitly validates these IDs and routes each one to MainActivity with auto_case_id and shared_session via startActivityForResult. Therefore the four cases are connected at host routing level, not merely listed in JSON. This does NOT yet establish MainActivity returns per-case verified GPU results, Android packaging, or an actual GLES31 dispatch on device. The host timeout shown at 18s is a warning only, not a forced PASS. The shared TEST_CENTER explicitly says no unified APK published. T1 historical mini APK artifact remains historical only.

## Build coordination / next decisive step
T1 vote should remain WAITING_MERGE until T5 verifies full driver result contract and build integration; no separate T1 APK, no duplicate CI, no full Raft build. Need shared APK on device and exported T1-01..04 per-case result, then original Unity GUID->FindKernel->Dispatch and paired first divergent FFT pass. Synthetic GLES success cannot establish original Unity kernel index 6 or water pixels. T4 physical mouse and T5 UI/Resolution remain separately assigned.

Evidence: https://github.com/alwansan/raf/blob/feature/android-native-port/apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/UnifiedLabActivity.java ; https://github.com/alwansan/raf/blob/feature/android-native-port/apk-for-testing/unified/pack/team-testpack.json ; https://github.com/alwansan/raf/actions/runs/42493143730 ; https://github.com/alwansan/raf/actions/runs/42497767712.
