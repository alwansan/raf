# T3 scheduled — source-original DXBC RDEF cardinality diagnostic

- session_id: `20261106T1630Z-T3-scheduled-rdef-cardinality-c7e2`; origin: **scheduled**; issue: **RENDER-002 OPEN / NOT_READY**.
- resumed_from_sessions: `20261106T1625Z-T3-chat-particle108-nativeRDEF-7d2c`, `20261106T1532Z-T3-scheduled-particle108-causality-8f3a`.
- base_sha: `e9ef2627d8bc09e007c5d2d59da1385136e5778b`; scope work: `prompt/coordination/work/RENDER-002/20261106T1630Z-T3-scheduled-rdef-cardinality-c7e2.json` committed `4230b209b76ec4590cd7b54e84119ea34128e39d`.
- source commit `2fc26e0373cf1b6e77f64343b5ea29348f9fa4df`; test commit `7c5fb5987ec29c17a53bb83ccf538cdb401bd2c2`; observed final HEAD `7c5fb5987ec29c17a53bb83ccf538cdb401bd2c2`.

## Concrete change

Original CI [42249097396](https://github.com/alwansan/raf/actions/runs/42249097396) authenticated the source but returned `ORIGINAL_RDEF_ABSENT_OR_AMBIGUOUS` on at least one of eight stage containers. Parser formerly merged zero and multiple RDEF chunks into one exception. Source parser now fails closed with distinct `DXBC_ORIGINAL_RDEF_ABSENT` and `DXBC_ORIGINAL_RDEF_MULTIPLE`, and privacy-safe static classifications. Added synthetic duplicate-chunk test and updated missing-chunk and safe-reason tests. No original shader names, register numbers or bytecode are emitted.

## Evidence and limits

Changes are published as source/test commits above. **Tests not executed in this cycle**: GitHub connector can read/write but cannot execute Python; container has no DNS to clone repo. Original private-source workflow **not dispatched** because equivalent job without a changed source-stage question would waste resources. This change allows a future explicitly coordinated genuine original-source run to distinguish absent vs duplicate RDEF, but does not prove which is present, nor recover a graphics program. Owner's [5 Nov phone report](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md) independently confirms world/save/reopen on artifact 42058825739; white raft/hand, lighting and square smoke remain open.

No game assets, .shader, .meta, GUID, save, FMOD, Settings, input, resolution or native Unity package changed. No Actions cancelled. Stay in Chat preserved. Next: execute source-free Python regression (14 tests expected, not claimed), then coordinate one SHA-pinned original eight-stage run only after checking latest Actions; if ABSENT, inspect original DXBC declaration tokens rather than invent RDEF binding layout. If MULTIPLE, audit chunk offsets and identity without publishing private shader data.
