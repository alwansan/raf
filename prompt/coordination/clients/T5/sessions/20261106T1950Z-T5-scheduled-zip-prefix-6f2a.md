# T5 scheduled — ZIP file/ancestor extraction collision gate

- session_id: 20261106T1950Z-T5-scheduled-zip-prefix-6f2a; origin: scheduled; owner: T5; issue: INTEGRATION-001; status: waiting_ci.
- resumed_from: 20261106T1751Z-T5-scheduled-lifecycle-7c4e and 20261106T1938Z-T5-chat-export-texture-gate-58c1; prior T5 original signed APK/OBB verification and owner device report docs/DEVICE_FEEDBACK_42058825739_AR.md.
- baseline HEAD: 3699074104512a7278b6c9712b18c1c2663632a3; scope reservation ec5639692fc4e119cab7b083fe50fc7c59608a30.
- hypothesis: individually safe distinct ZIP member names can still create an impossible extraction layout when a regular file is also a directory prefix of another member. Existing structural verifier checked traversal/duplicates/local headers but not this collision.
- implementation: 22ce377a97b61e3530682abbd86b5b2fb2aba529 adds a non-decompressing prefix check to scripts/t5_verify_apk_obb_pair.py; 791751b42764ae89087376caf1adb9bca4db013a adds OBB and APK negative synthetic cases plus a valid explicit directory positive case to tests/test_t5_verify_apk_obb_pair.py.
- validation: GitHub Actions run https://github.com/alwansan/raf/actions/runs/42283255333 is PENDING at checkpoint. No PASS claim; no Unity/native build or device run. Local container has no GitHub DNS; CI is authoritative next check.
- scope: independent T5 APK/OBB structural verifier; no overlap with T4 mouse, T1/T2 water, T3 shader, or T5 chat native texture export. No raw game resources, secrets, .meta, GUID or .rgd touched.
- owner device evidence: world entry/save/reopen only for artifact 42058825739, not the new source SHA. Actual signed APK/OBB integrity, Unity OBB mount, LogRaft performance and display fixes remain separate; NOT_READY 0/3.
- next: inspect run 42283255333 and tests; if red fix exact assertion; if green report structural-only confidence and inspect current signed output vs delivery manifest without launching duplicate native build. Trial r1 T4 needs; others do not, so no 5/5 build request.
