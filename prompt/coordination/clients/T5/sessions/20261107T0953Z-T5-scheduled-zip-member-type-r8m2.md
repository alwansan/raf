# T5 scheduled checkpoint — 20261107T0953Z-T5-scheduled-zip-member-type-r8m2

- origin: scheduled; issue: INTEGRATION-001; branch: feature/android-native-port.
- resumed_from_session: 20261107T0845Z-T5-scheduled-6f2a; initial HEAD: 8091829d02e5217c758a9e2c4c838ca17c0ce0d1.
- Owner device evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner confirms world/save/exit/reopen on source e9c358eda01785b65e4eb14f18723da426635628 only. CL screenshots and log session counts referenced therein; no new device capture.
- Scope: prompt/coordination/clients/T5/work/20261107T0953Z-T5-scheduled-zip-member-type-r8m2.md; source commit 49848916b4321e5fa5378dad5d4ad35438a74e3a; tests commit 3037e1c597ab4bc1918f1a7f4449a9d6f118d7a4; completed work commit 07fabb570ed4fbede05b832cc1e762efedd8963c.
- Finding: previous archive verifier validated ZIP paths, sizes, SHA and duplicate names but did not reject explicitly encoded Unix symlink or device member types. The hardened verifier now fails closed on those special types before reading metadata or transport parts. Five regression cases added; five isolated Python member-type assertions passed in the local runtime, **not** a full checkout test.
- Limits: GitHub DNS from container unavailable; full repository unittest not executed. No archive downloaded, no APK signature/OBB GUID or installed package match, no performance sample; no Unity/native CI launched. Release 403 remains independent; no Release attempted. T4 owns mouse; three right buttons and Resolution remain open.
- Build voting: trial-20261106-r1 T1/T2/T3/T5 = لا يحتاج, T4 = يحتاج, not unanimous; no new native request.
- Next: run python3 -m unittest tests.test_t5_retained_delivery_duplicate_json -v against branch checkout; inspect retained archive modes and verify APK/OBB hashes if accessible. Then prioritize actual right-side buttons and Resolution fixes with distinct file scope; coordinate with T4 for mouse.
- Readiness: NOT_READY 0/3; source-only hardening is not phone acceptance.
