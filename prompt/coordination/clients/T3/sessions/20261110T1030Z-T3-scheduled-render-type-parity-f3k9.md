# T3 session 20261110T1030Z-T3-scheduled-render-type-parity-f3k9
origin=scheduled
Baseline HEAD 6999eafe742d8c519e790a4df64ac786fd882ef2 (2026-11-10 10:23 UTC); branch feature/android-native-port only.
Owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; world save/reentry confirmed on Artifact 42058825739; white raft/hand and square smoke unresolved; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Mouse T4, Resolution/buttons T5; no overlap.
Prior T3 evidence: run 42782959918 succeeded for 12 existing synthetic render-state tests on 652a03ec; not actual source/export nor device proof. Scope file: clients/T3/work/20261110T1030Z-T3-scheduled-render-type-parity-f3k9.md committed 50711dca7f0be108e32637f799055bd1575ad500.
Change: Python True == 1 and False == 0 could mask mismatches in JSON summaries. Comparator now requires exact scalar type equality before value equality, commit 746ada6ba814c9672e185171fd6e0fb8cb1d3f87. Added 3 tests for bool/int alias, same integer and known mismatch alongside unknown, commit ef457271d66c4db86e0a4b494f91b39a1c16c948.
CI: run 42799736638 observed in_progress on 746ada6b, before regression-test commit. waiting_ci; do not claim pass. Check subsequent run on ef457271 and its conclusion next session. No Unity/APK built, no game assets modified, no actual paired original/export inputs.
Next: verify CI result; obtain authenticated same-material original/export render-state summaries from ZIP2 and run comparator. Do not use synthetic tests as evidence of corrected pixels. RENDER-002 OPEN NOT_READY 0/3.
