# T5 restore session — original graphics hydration consumer

- session_id: 20261105T0024Z-T5-hydration-preflight-a1
- resumed_from_session: 20261104T2357Z-T5-b12-fixture-7e2
- identity: T5 (not a B or T sibling)
- branch: feature/android-native-port; base HEAD: e500e0633f0fcda6149e7dffd607a42660435d41
- last T5 state at session start: paused; 0f3739e38f6b42c92100e75697a314988869cf63 last source commit; index CI41940609086 SUCCESS.
- retained verified original: ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385; 3 owners 337660952 bytes; CI41940032540 SUCCESS (not Unity/phone).
- latest T5 plan: prompt/coordination/work/ASSET-RESTORE-001/T5-20261105T0024Z-hydration-batch-preflight.json
- issue: ASSET-RESTORE-001; no fake GPU/world success; audio and Settings preserved, touch deferred.
- preliminary defect: hydrate_render_payloads.reuse_verified_staged_sources iterates and replaces pointer per owner. A linked/malformed *later* original source can leave an earlier original written to feature checkout. Add full-batch structural preflight before any output mutation without twice hashing 7GB. Keep streaming SHA check of every copied original.
- planned validation: two-owner negative synthetic that preserves pointer 1 when source 2 is unsafe or target 2 mismatches; positive 3-owner CI remains authenticity checkpoint.
- constraints: do not alter shared Unity workflow, native requests, private byte payload or other agents' work; track actual CI after push.
- session initially planning; final evidence to be appended and state set paused on completion.
