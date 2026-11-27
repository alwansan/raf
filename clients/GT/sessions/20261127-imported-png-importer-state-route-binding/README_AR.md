# GT V9 — actual Swizzle omission, scope separation | 27 نوفمبر 2026

[45959834665](https://github.com/alwansan/raf/actions/runs/45959834665) actual V7 and separate V8 succeeded; V9 stopped on missing_png_exporter_policy_swizzle (2 textures). Both actual meta schemas omit Swizzle. Pinned TextureImporterExtensions.SetSwizzle only writes if Has_Swizzle(); absent is UNKNOWN, not RGBA equality. Artifact 15179794604 downloaded, CRC and all 22 member SHA256 verified; 15161 bytes SHA256 52ee13b55c7ab0c78e8a8cffa37aeab9f02898a6fd71bbd3d36825e3d03776b6, Git blob 73cdb806641780147f07d430231c77a86f918e1f; member hashes retained. New scoped receipt and explicit missing-swizzle counter: complete serialized-state flag and strict CLI remain false/exit 2 for absence; supported source and policy comparisons separate; explicit wrong-swizzle injection rejected, null invalid; other missing fields still fail. No claim of successful retry yet. A3 blocked; G0–G6 open; no original assets, Unity reimport or XAPK.

---

# GT V9 — focused retry in progress | 27 نوفمبر 2026

[c0ff25c](https://github.com/alwansan/raf/commit/c0ff25c6a08c5c4bcd0d5402f650c0aebec8351b) fixes only report log key suffix (.py.log), not gate conditions. [45959834665](https://github.com/alwansan/raf/actions/runs/45959834665) job 140374777770 in_progress; source regression step successful, guard [45959834608](https://github.com/alwansan/raf/actions/runs/45959834608) successful. Native and PNG actual proof not yet accepted for this retry. Preserve initial failure and its receipt hashes. Next: read exact retry result, verify ZIP, field schema/enum ABI and controls; no Unity reimport claim. A3 blocked; G0–G6 open; white/black fire not proven fixed; no XAPK. Only authorized branch, CL/lab read-only, BLACK out of scope.

---

# GT V9 — first CI failure retained | 27 نوفمبر 2026

[45959587458](https://github.com/alwansan/raf/actions/runs/45959587458) completed FAILURE, 233/233 tests (217 historical +16 V9) passed, exact public exporter compiled, actual native V7 route and 43 controls passed (route-join.json SHA256 identical to prior V7 receipt). Aggregation then failed KeyError test_gt_imported_png_route_importer.py: dictionary uses *.py.log filenames. V8 and V9 actual PNG steps skipped. No V9 actual PASS. Artifact 15179907603 ZIP downloaded/verified 10298 bytes, SHA256 c2813b61def79447dfbd71473f7f1ac8b95b03292aba105c36fcc04899371ae7, Git blob 7c0d9af0ccdd742f474bd9b0638b5513f488b81b, CRC and all 16 members verified; raw ZIP stays in Actions, exact member hashes and result in initial-failure-45959587458.json. Fix only log-key suffix; preserve all conditions. A3 blocked, no original assets or XAPK.

---

# GT — V9 actual public exporter CI pending | 27 نوفمبر 2026

Starting HEAD d477529faffbf82c8758d2e466943944a98757ba matched. [e81dde6](https://github.com/alwansan/raf/commit/e81dde6404b59a433c81d0568f7818f87d83126c) source gate and new unit tests, [080bb3e](https://github.com/alwansan/raf/commit/080bb3ec339c0fb5930e1ac156f41942adb9e5fd) typed distinct pre-export source state and 13 actual metadata mutation controls, [f26030a](https://github.com/alwansan/raf/commit/f26030acf76d972d10181af52380c935e0a7201a) focused workflow activation. [45959587458](https://github.com/alwansan/raf/actions/runs/45959587458) job 140373971293 source regression step successful, public build in progress at checkpoint; guard [45959587613](https://github.com/alwansan/raf/actions/runs/45959587613) success. Other jobs in this workflow skipped. No PASS V9 yet. No Unity editor, private assets or APK/XAPK fetched/started. Previous V8 ZIP 15179790908 downloaded and SHA256/size/CRC independently reverified (13784 bytes, SHA256 f867a4eea6f521717e83cda62b28b61cb879d6a9fc1e13d47f2a67f692207c73, 20 members; Git blob 0e5d050c95fb0de484ce1e87a2cdbc465d82ee44; raw ZIP still not in Git). Existing aggregate receipts and member hashes preserved.

V9 same owner typetree and exact texture trace, finite float32 sampler state, separate source-derived fields and exporter policies; actual generated enum ABI and meta schema must pass. No inference of Unity import, compression/runtime/GPU or lower mips. A3 blocked until authorized original source, G0–G6 open, no fix of white or black fire proved. CL/lab read-only, BLACK excluded, animation deferred, only branch feature/android-native-port no force push.

**Next:** Read actual job completion for exact activation head; verify schema, enum ABI, regression counts, 13 V8-pass/V9-reject controls; retain actual success or failure receipts, correct without weakening gate. A3 remains blocked.

---

# GT — V9 source-side implementation / PENDING | 27 نوفمبر 2026

Starting HEAD d477529faffbf82c8758d2e466943944a98757ba verified live; native V7 and PNG V8 run 45957439789, guard 45957440880 success. Artifact 15179790908 remains listed, 13784 bytes, recorded SHA256 f867a4eea6f521717e83cda62b28b61cb879d6a9fc1e13d47f2a67f692207c73; raw ZIP not rehashed in this session. No local checkout/diff found. Owner pinned restore 1a78eb2764d39550f59e2948ae5ed89033c8ab73 reviewed.

V9 opt-in --imported-png-importer-state implementation: capture source state in the same authenticated typetree as V8, exact GUID/fileID 2800000/type3 same-material route, strict modern six sampler fields and finite float32 bias; -100/-1 unknown, explicit source fields and separately compared pinned ImporterFactory policy. New authored unit controls. **PENDING, unexecuted**, not an actual public exporter or Unity proof. Numeric generated enum ABI and complete serialized key names must be independently confirmed by actual public exporter witness, not assumed. No original source or reimport, lower-mip, GPU, Android fidelity. A3 blocked pending authorized source, G0–G6 open, white/fire unresolved.

Next: extend C# authored pre-export source state with distinct typed color/readable/streaming/priority and assert enum ABI; actual V8-pass/V9-reject metadata drift controls; focused existing public exporter workflow, preserve 217 historical tests and 56 controls. Retain failures and receipts. No unauthorized originals/LFS, phone or XAPK; CL/lab read-only, BLACK excluded, animation deferred, only feature/android-native-port no force push.

---

