# T5 scheduled — APK/OBB delivery JSON ambiguity hardening

- session_id: 20261107T1051Z-T5-scheduled-json-pair-v4k8
- origin: scheduled
- base_sha: 2e026ea817116051dd5298e8984f43cb69a40ce6
- resumed_from_sessions: 20261107T0953Z-T5-scheduled-zip-member-type-r8m2; 20261107T0845Z-T5-scheduled-6f2a
- owner feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md (5 Nov), phone world/save/reopen confirmed only on artifact 42058825739.
- scope: prompt/coordination/work/INTEGRATION-001/T5-20261107T1051Z-T5-scheduled-json-pair-v4k8.json; scripts/t5_verify_apk_obb_pair.py; tests/test_t5_verify_apk_obb_pair.py. Independent of T4 physical mouse and T1–T3 rendering.
- finding: APK/OBB local verifier used default json.loads (last duplicate key wins), unlike previously hardened retained archive verifier. This could accept ambiguous package/version/part metadata.
- code: 8ee7bd64ef99c3893c2138d2503bceb776bcd7ad introduces object_pairs_hook fail-closed on duplicate JSON keys at any depth.
- tests: 477c62f9834ba9863f1fb14ef0a2aae4fc5e478f adds three top-level/nested/transport adversarial controls.
- CI: https://github.com/alwansan/raf/actions/runs/42365731144 was in_progress at review and is pinned to 8ee7bd64 (BEFORE test commit). It cannot prove the added tests. Await a post-477c62f run; do not duplicate equivalent CI while in flight.
- limits: no signed APK/OBB downloaded or matched, no device/Unity/LogRaft measurement, no resolution or three-button UI change. Source-only patch pending test proof. Preserve owner-reported world/save/reopen and NOT_READY 0/3.
- next: inspect final CI for source patch and a new run containing 477c62f; if green, assess full pair against authenticated retained archive and check T5 UI/Resolution scopes before editing. Avoid redundant Unity and other clients' runs.
