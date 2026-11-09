# T5 native run provenance watch
session_id: 20261109T2049Z-T5-scheduled-native-watch-b72e
origin: scheduled
baseline_sha: 70f4c256af7479efb1788b444051e757660ba38e
scope: inspect owner-direct full native #42696228231, no duplicate Unity run.
experiment_key: t5-native-run42696228231-provenance
resource_key: raft-native-engine-feature/android-native-port (occupied; observation only)
taken_over_from: clients/T5/sessions/20261109T2045Z-T5-chat-native-owner-rerun-5f28.md
intended_files: work/T5/20261109T2049Z-T5-scheduled-native-watch-b72e.md; clients/T5/sessions/20261109T2049Z-T5-scheduled-native-watch-b72e.md
evidence: #42695722354 T1 original FFT source preflight SUCCESS; #42696228231 native-request-gate SUCCESS and unity-license-preflight SUCCESS; reconstruct IN_PROGRESS restoring original graphics payloads at 2026-11-09 20:49 UTC. R5 Mini #42691609924 SUCCESS is distinct. T3 #42696430679 source-only semantic parser test FAILED, not evidence of Unity failure.
hypothesis: native reconstruct may succeed, while publish could still fail as #42296450023 did; actual APK/OBB fingerprints require signed package bytes.
collision_policy: do not edit T3/T4 code, launch Unity, change native request, or overwrite team readiness.
status: waiting_ci
next_step: inspect #42696228231 terminal jobs/artifacts, then verify manifest and OBB bytes if available; otherwise report precise missing evidence.
