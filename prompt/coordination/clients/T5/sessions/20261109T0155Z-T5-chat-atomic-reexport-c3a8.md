# T5 chat session — paired evidence export safety

- **session_id:** `20261109T0155Z-T5-chat-atomic-reexport-c3a8`
- **origin:** `chat`
- **identity:** T5
- **base_sha:** `044296d60d7eb03d52334de305450aa10fdc76dd`; no branch force/reset, only `feature/android-native-port` edited.
- **resumed_from:** root `clients/T5/sessions/20261109T0142Z-T5-chat-media-4fa9.md` source-only green CI42547097683, and `prompt/coordination/clients/T5/sessions/20261109T0153Z-T5-scheduled-evidence-token-p6m2.md` (separate strict screenshot-marker validator, not modified).
- **CL evidence:** latest directory inspected `alwansan/CL:test/shared-20261108-232759-468049775`; synthetic T3 images EVIDENCE_READY need human/device game interpretation; T4 clicks/wheel remain device pending. Owner game save/reentry evidence limited to build artifact 42058825739. Full game NOT_READY 0/3.
- **baseline shared Mini:** v0.2.13-shared [CI42519487402](https://github.com/alwansan/raf/actions/runs/42519487402), artifact ZIP 13632379139, APK sha256 `6a41002cee345c48413ef56b0820211fb4ae73292229ec33ce830e82897194a7`; this APK does NOT contain the new export source fixes. T5 shared r4 NO_BUILD; no full game build, no new Mini build request.
- **coordination:** no active/queued branch Actions at initial review; T4 owned mouse bridge; T1 FFT and T3 PNG evidence independent; T5 scheduled concurrent scope is `scripts/t5_verify_shared_device_summary.py`, not our Java export adapter. Scope registered before edit in `prompt/coordination/work/INTEGRATION-001/T5-20261109T0155Z-T5-chat-atomic-reexport-c3a8.json`. `experiment_key=T5_export_two_file_publish_new_then_retire_previous_android29_source-v1`, `resource_key=apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/UnifiedLabActivity.java`.
- **intended/changed files:** `apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/UnifiedLabActivity.java` and `tests/test_t5_unified_saf_stream_contract.py`. No T1–T4 component, raw assets, testpack, package/signing, full-game Unity or shared build request modified.

## Proven problem and fix

Prior `export()` called `openOutputStream(logExport,"wt")` and `openOutputStream(summaryExport,"wt")` on previously **published** MediaStore URI records. An interrupted write could truncate complete prior evidence. The previous `writeMedia()` IS_PENDING+cleanup fix only protected new MediaStore insertions.

- **Source fix:** [db261619](https://github.com/alwansan/raf/commit/db261619408a8553d61ecfe211749231d27b4a45) always writes a fresh complete events log and summary through guarded `writeMedia`; only after both new writes return success does it replace `logExport/summaryExport` and delete their prior valid URIs. If the second write fails, it deletes the newly inserted event log and retains both previous URIs. Delete failure is logged and shows user a duplicate-old-file warning; it does not destroy new files.
- **Regression tests:** [f2609b07](https://github.com/alwansan/raf/commit/f2609b07d59cf3444ea65d6547f6bef38ea59a7b) source assertions reject in-place public URI overwrite, check both new writes precede retirement, check rollback and cleanup error reporting.
- **Source-only CI** [42548237907](https://github.com/alwansan/raf/actions/runs/42548237907) **SUCCESS** and [42548237886](https://github.com/alwansan/raf/actions/runs/42548237886) **SUCCESS** for source commit db261619. [42548284041](https://github.com/alwansan/raf/actions/runs/42548284041) (new regression commit f2609b07) **IN_PROGRESS** at initial checkpoint. Check latest run result before claiming the new tests passed.
- **Experiment:** `prompt/coordination/experiments/T5/20261109T0155Z-T5-chat-atomic-reexport-c3a8-paired-export.json`.

## Limitations

This is not a cross-file atomic visibility transaction: the two distinct newly published MediaStore URIs can briefly be visible at different moments, and failed deletion of old files leaves extra valid copies. Source tests/Android javac are not Android15 device fault injection. No game graphics, save, OBB SHA, or phone acceptance changed. `onStop`/private logging still use existing behavior and pair URIs are not persisted between app process restarts.

## Handoff

1. Inspect CI42548284041 (Python source regression, Java StreamSha256 and Gradle unified source compile); if failing, fix only owned scope and record actual errors.
2. Keep T5 shared Mini r4 NO_BUILD until new driver need and single-build coordination under `SHARED_BUILD_READINESS.md`; don't claim current installed v13 contains this change.
3. At a later legitimate shared Mini build, test interrupted provider writes and repeated exports on Android15; inspect uploaded `CL/test/shared-...` JSONL + summary, ensure complete files and only warn if old ones remain. Do not recast EVIDENCE_READY as game visual PASS.
