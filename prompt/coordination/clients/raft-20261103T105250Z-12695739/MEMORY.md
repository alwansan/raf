# A8 continuation — DIAG-010 diagnostic log lifecycle

New identity raft-20261103T105250Z-12695739; resumed_from completed A8 raft-20261103T100412Z-b2521375. Registered 2026-11-03T10:53:12.398Z.

Live owner requirements, prompt/README, CONTINUE, STATUS, AGENTS, coordination and readiness reviewed; branch feature/android-native-port only. Old game release APK80 is separate from LogRaft; CL raft-log/lf Nov2 sessions remain read-only. Other active work concerns WATER-001 (A1), DISPLAY-003 (A2), PERF-007 CI memory counters (A4), HAPTICS-008 and LOCAL-005; diagnostics runtime and its C# harness are not claimed in current work plans. No Unity/APK/OBB/XAPK, no task/request changes.

Hypothesis: `PersistentDiagnosticLog.Write` checks `stopping` without a lifecycle lock, but `Dispose` can dispose `wake` after that check and before `wake.Set`, allowing `ObjectDisposedException` from background Unity logging during shutdown. Also current `raft-android-platform-tests.yml` does not run existing `android-port/Tests/Diagnostics/Diagnostics.csproj` despite its source. Proposed fix protects lifecycle of Write/Dispose with a fast independent monitor, add concurrent smoke test and CI step. No change to original game source/GUIDs/assets, nor claim of device acceptance.
