# T5 chat — cross-client runtime compile-source staging parity

- **session_id:** 20261106T1710Z-T5-chat-crossclient-copy-parity-a6d9
- **origin:** chat
- **issue_id:** INTEGRATION-001
- **resumed_from_sessions:** 20261106T1702Z-T5-chat-offline-obb-compile-58cf, 20261106T1645Z-T5-chat-installed-obb-read-e7c4 (separate native OBB-probe scope), 20261106T1649Z-T5-scheduled-runtime-attribution-c82f (separate PERF scope).
- **base_sha:** ec89ec09e590fbb6a3b2174acc7ccf2e1fa0f239
- **reservation commit:** f2bd29e5fd3b989a314c223d67fc52869d5933b6, work path prompt/coordination/work/INTEGRATION-001/20261106T1710Z-T5-chat-crossclient-copy-parity-a6d9.json.
- **experiment_key:** T5-managed-runtime-copy-dictionary-T4-exact-two-file-lexical-pair-guards-source-v2
- **files touched:** scripts/verify_android_offline_candidate.py; tests/test_t5_offline_runtime_support_deps.py; this independent session, own work/experiment/event.
- **previous repro:** T4 physical mouse CI42258089066 fails a source-only literal assertion: previously contiguous 'AndroidPhysicalMouseCapture.cs', 'PhysicalMouseDeltaAccumulator.cs' lost adjacency when T5 refactored runtime copied sources. T4 immersive CI42258089028 fails similarly for 'AndroidImmersiveSystemBars.cs', 'AndroidSystemBarPolicy.cs'. Actual original-managed compile CI42258190836 already succeeds on the full T5 source copy set; no phone/device failure inferred.
- **source fixes:** 8b4ef8fc6a75e4238bfb8873e7aab685c4f1bfa3 restored both adjacent literal pairs inside single T5 list, preserving 17 source entries and preflight behavior. 905285215e6cbc5d72f480fa478bdbfc762cc775 added T5-owned regression asserting both existing T4 contracts. Concurrent branch advance caused initial session save 409; rechecked latest source blobs (both changes retained) and retried as a distinct new file.
- **coordination:** neither T4 runtime/tests nor any T1/T2/T3/other T5 scheduled work changed; Unity/OBB/graphics and private source untouched.
- **status:** waiting_ci
- **next_step:** confirm fresh T4 pointer and immersive CI alongside original-managed compile with exact source SHA; record outcomes and mark scoped work completed, NOT_READY 0/3 until actual Android/game acceptance.

## Final verified scoped result — 2026-11-06T17:12:37.067Z

**status: completed**, work reservation released. Read-only outputs validated against the following immutable source commits:

- T5 source-list compatibility commit `8b4ef8fc6a75e4238bfb8873e7aab685c4f1bfa3`: T4 physical mouse [CI42259099674](https://github.com/alwansan/raf/actions/runs/42259099674) **COMPLETED SUCCESS** and T4 immersive system bars [CI42259099680](https://github.com/alwansan/raf/actions/runs/42259099680) **COMPLETED SUCCESS**; prior two specific source-string test failures eliminated without editing T4-owned files.
- T5 test-guard commit `905285215e6cbc5d72f480fa478bdbfc762cc775`: original offline managed [CI42259133117](https://github.com/alwansan/raf/actions/runs/42259133117), job `128034148525`, **COMPLETED SUCCESS**; new T5 integration tests **5/5 PASS**, `originalSources=14`, local RPC identity harness PASS, `RAFT_OFFLINE_COMPILE exit=0 errorCodes={} affectedFiles=[]`. This follows the prior source compile fix [CI42258190836](https://github.com/alwansan/raf/actions/runs/42258190836).
- Own experiment: `prompt/coordination/experiments/T5/20261106T1710Z-T5-chat-crossclient-copy-parity-a6d9.json`; own event: `prompt/coordination/B_TEAM/events/T5/20261106T1710Z-T5-chat-crossclient-copy-parity-a6d9.json`.
- **Control:** no Unity Editor build, original ZIP2 raw assets, device install, audio/mouse gameplay, water pixels, shader recovery or signed delivery invoked in this round. `NOT_READY 0/3`; scoped completed means those THREE source CI validations passed, not a playable current SHA.
- **next_step:** keep `RUNTIME_COMPILE_SUPPORT_FILES` as an explicit native/managed parity interface; rerun T4 source-only tests if altering literal groupings. Check future exact installed OBB/Unity engine read logs and prioritize T1/T2/T3 P0 graphics integration; source CI can never substitute Android GPU or phone validation.
