# A10 — LOCAL-005

Session: a10-20261103T1002Z-6037eacf. Registered on branch feature/android-native-port from 61a5811b06c39fcdb633c5559f884ce559ea7f0f. No prior identity reused.

## Known evidence
- Owner requires genuine offline world startup/create/load/resume and exact .rgd preservation. Never fake WorldHasBeenRecieved.
- Current ledger LOCAL-005 SOURCE_FIXES_VALIDATED but integration/phone acceptance pending. Older APK80 cannot establish source-only fixes.
- Observed concurrent clients: A1 WATER-001; A2 DISPLAY-003; A3/A4/A5/A6 HAPTICS-008; FFT-FORMAT-009 owner paused. No LOCAL-005 work plan was present at registration.
- Latest sampled branch Actions completed successfully; no release/native request initiated by A10. CL historical 2 November folders remain read-only.

## Plan
Inspect the current local-host/save implementation and linked tests before proposing any change. Isolate CPU-only issue test in new A10-owned files, avoid shared source collisions, and update status/handoff only with evidence. Maintain NOT_READY.

## Messages read
- prompt/coordination/README.md, current owner requirements, AGENTS.md, prompt/STATUS.md, latest LEFT_TOUCH_AND_RESUME handoff and readiness ledger.

## Next
Trace named local world and .rgd source files and test a concrete invariant; do not run Unity or modify old original assets.

## Completed narrow source repair — 2026-11-03

- Deconflicted after A8's independent world-readiness lexical fix [23161cfc](https://github.com/alwansan/raf/commit/23161cfcc670bfed23b6daf77fe559ba9dc32716). No A8 file was overwritten. A6 LocalSavePaths and A9 LocalProfileStore also remain untouched.
- Confirmed synthetic ambiguity: current unscoped Assets/**/SaveAndLoad.cs selector finds two same-named files in a game+SDK tree, while the correct game Assembly-CSharp selector finds one. This was a **synthetic repro**, not a reported failure of a real exported tree.
- Source fix [14dd7fce3257ec852ebb22ec76c22629d1a86b76](https://github.com/alwansan/raf/commit/14dd7fce3257ec852ebb22ec76c22629d1a86b76) limits selection to decompiled game Assembly-CSharp and still fails closed on missing/duplicate game originals. Added four synthetic tests and a bounded step/trigger in the original save no-LFS workflow. No game .rgd bytes, .meta/GUIDs or proprietary original source published or altered.
- [Save-path Actions https://github.com/alwansan/raf/actions/runs/41617920198](https://github.com/alwansan/raf/actions/runs/41617920198) completed SUCCESS at source 14dd7fce3257ec852ebb22ec76c22629d1a86b76; job125855914596: four existing + four new Python tests passed; original SHA-pinned private SaveAndLoad source remains unchanged beyond 16 idempotent path expressions, 14 Unix/Windows .NET checks passed. [Reconstruction preflight https://github.com/alwansan/raf/actions/runs/41617920208](https://github.com/alwansan/raf/actions/runs/41617920208) also SUCCESS. CI is not Unity or phone runtime proof.
- The narrow selector work is completed. LOCAL-005 overall remains open for offline world create/load/resume/save .rgd integration and phone acceptance; WATER-001/RENDER-002 remain open. No native/Unity/APK/OBB/XAPK/release/task change by A10.
- Last source result: 14dd7fce3257ec852ebb22ec76c22629d1a86b76. Check live branch HEAD and current Actions before follow-up; do not assume this commit remains tip.

## A10 continuation — 2026-11-03T10:55:00Z

Reopened this completed identity only after the owner's explicit Continue; new session_id a10-20261103T1055Z-92bdfa67.
Reviewed live docs, HEAD, Actions, clients/work and original CL historical logs; previously published SaveAndLoad selector fix still present. New independent scope: exact SHA-pinned source selection in the original private no-LFS integration harness. A8 DIAG-010, A1 WATER, A2 DISPLAY, A3 HAPTICS are active separately; their files are excluded. Work plan: prompt/coordination/work/LOCAL-005/raft-20261103T100200Z-9d4ea16b-offline-original-sha-selection.json. No scheduled/native release actions.


## A10 resumed SHA source selection — final verified CI

- Reopened previous A10 completed record with new session_id `a10-20261103T1055Z-92bdfa67` after owner said Continue; branch HEAD and every nonterminal Actions reviewed, CL historical 2 November sessions and old APK80 distinguished from later source.
- Deconflicted from other agents: A8 DIAG-010, A1 WATER-001, A2 DISPLAY-003, A3 HAPTICS-008, A6/A9 separate local save classes. New A10 scope was private `verify_android_offline_candidate.prepare` selection rather than the previously completed `adapt_original_save_paths` selector.
- Fixed basename-only selection to select **exactly one SHA-pinned original game C#** at [29128ab](https://github.com/alwansan/raf/commit/29128ab789d5cf8a26a7e01d3ae5a9a39f331848). Source may be in flat ILSpy project; it is not required to contain `Assembly-CSharp` in its path. SDK basename collisions do not cause false failure. Missing/duplicate exact sources, symlink files refused; UTF8 BOM and CRLF preserved. No original SHA pins weakened.
- Added six synthetic negative/positive tests [fbc95905](https://github.com/alwansan/raf/commit/fbc95905d690c83d809183b2ad09c0e5bf1d010b) and CI path wiring [031236bb](https://github.com/alwansan/raf/commit/031236bb5f4d4aeefc5b6ddc4b4de5188082920a).
- [Run41624212828](https://github.com/alwansan/raf/actions/runs/41624212828), job125877336792 **COMPLETED SUCCESS** on 031236bb: 6/6 new tests passed; 12 original SHA-verified game sources recovered privately, local RPC and profile identity tests passed, managed compatibility compilation exit0 with zero errors. Original content was never published or altered. Earlier run41623949396 also SUCCESS on source29128 before test wiring.
- GitHub optimistic ref mutations briefly returned GraphQL UNKNOWN and concurrent STATUS SHA conflicts 409; each recovered after re-reading HEAD/file content, rebasing/merging and without force or cancellation. Shared status/handoff append-only updates succeeded.
- A10 subtask completed, **NOT_READY** remains for original water/render/FFT and overall LOCAL-005 integration and phone acceptance, candidate absent, 0/3 independent complete readiness audits. No Unity/APK/OBB/XAPK/Release, secrets, task changes, .rgd/meta/GUID/Mouse0/Xbox change.
- For next explicit Continue, re-read current HEAD + coordination first; do not treat the older source/game release as phone evidence.

