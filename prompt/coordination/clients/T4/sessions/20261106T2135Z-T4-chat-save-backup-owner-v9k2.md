# T4 chat — Safe backup-root ownership on local save source staging

- **session_id:** `20261106T2135Z-T4-chat-save-backup-owner-v9k2`; **origin:** `chat`; **issue:** LOCAL-005; **status:** active.
- **resumed_from_sessions:** `20261106T2052Z-T4-chat-save-stage-stale-q6r2` and `20261106T2035Z-T4-scheduled-native-failure-h7q2`.
- **base_sha:** `e2cbadb6acc4d927ec2e61e4b7e012e049235146` during scope check; reserved work at [1d608192](https://github.com/alwansan/raf/commit/1d608192634db991e246b812f84ead1ec422810c).
- **intended_files:** `scripts/adapt_original_save_paths.py`, `tests/test_adapt_original_save_paths.py`; active work `prompt/coordination/work/LOCAL-005/T4-20261106T2135Z-T4-chat-save-backup-owner-v9k2-postpromote-owner-delete.json`.
- **hypothesis:** another writer can rename the adapter's just-published backup root and replace the path with a foreign directory; stale-source cleanup and post-write rollback currently delete by pathname, risking deletion of a foreign owner's directory.
- **plan:** deterministic RED source-only collision test; pin original staged directory device+inode before promotion, check same directory before own cleanup, keep foreign root untouched when ownership differs; run original save path CI including SHA-pinned original private ZIP2 probes.
- **non-overlap:** separate from T4 completed post-backup *source/meta drift* check 5d374392/CI42292421337 (16/16). Full native build [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) active on `a1737bd7` at start; do not cancel, re-dispatch, or modify native request/workflow.
- **limits:** no changes to original game DLL, .rgd serialization, .meta/GUID, mouse, UI, sound, Settings, or native build. Source-only guard does not prove device saving.

## Checkpoints
- Scope reserved. Await test-only RED and source-fix GREEN evidence; preserve any unexpected failure.
