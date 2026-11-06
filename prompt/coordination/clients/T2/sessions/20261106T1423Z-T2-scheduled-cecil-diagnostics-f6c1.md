# T2 scheduled — 20261106T1423Z-T2-scheduled-cecil-diagnostics-f6c1

origin: scheduled
status: blocked_compiler; no Unity/native build requested
source_ref: feature/android-native-port

## Evidence
Owner phone run 42058825739 is a bounded successful world/save/reopen from artifact, independent of water failures. Original report docs/DEVICE_FEEDBACK_42058825739_AR.md: water pass errors 23884/39132, FFT kernel errors 3850/6026 in two sessions; no new device result claimed.

Original Foam managed-name run 42224754004 (source SHA 8094f937da92aa5357604f7dc3a2f3f57a1195e2) is completed FAILURE, same compile stage as 42224703030. 11/11 source-free Python tests passed; dotnet publish failed with compiler codes CS0136:1 and CS1929:1. Source authentication, private Shader typetree and CB0 managed setter correlation steps were SKIPPED. No safe artifact was produced. Job 127915313223, log read directly. Do not treat source-free tests as original source proof.

## Independent source investigation
Read android-port/Experiments/T2/FoamCb0ManagedLiterals/Program.cs and MaterialStoreValueTrace.cs. In MaterialStoreValueTrace.cs the same C# pattern identifier `field` occurs in the adjacent `ldfld` and `ldsfld` branches (approx lines 189 and 200), a candidate for CS0136; verify with unsuppressed compiler diagnostics before editing. The workflow currently suppresses full compiler log and emits only safe code counts. CS1929 location remains unknown. Avoid blind changes and coordinate with active T2 chat ownership of this scanner.

## Next action
Run a source-free isolated dotnet compile diagnostic with safe output limited to compiler error code, repository file basename and line number (no original game source, strings or private symbols); resolve both compiler errors in one non-overlapping patch, run scanner selftest, then re-run original authenticated ZIP2 evidence only once after checking active Actions. CB0 upload/Material identity and ShaderLab readiness remain unproven; WATER-001 OPEN. Preserve T3 FX, T4 mouse, T5 Resolution, FMOD, Settings, touch and original game assets.
