# T4 chat — source-free Android mouse release outcome + world log classifier

- session_id: `20261106T1128Z-T4-chat-device-mouse-release-evidence-p8m2`
- origin: `chat`, issue: `INPUT-005` still OPEN; LOCAL-005 remains OPEN
- status: `completed_source_free_parser_ci_success_device_unverified`
- base_sha: `f9a71c33d502f9155cb79ad8f1cb677ac059bff4`
- resumed_from_sessions: `20261106T1106Z-T4-chat-release-outcome-s8k4`, `20261106T1042Z-T4-scheduled-f6n3`, `20261106T1030Z-T4-chat-release-view-ownership-b7m4`
- experiment_key: `T4-INPUT005-device-JSONL-release-status-eight-static-original-20261106-e06566a-source-free-overflow-privacy-negative-v1`
- resource_key: `T4-source-free-JSONL-Python-only-no-Unity-no-phone-dataset`
- work: `prompt/coordination/work/INPUT-005/T4-20261106T1128Z-T4-chat-device-mouse-release-evidence-p8m2-source-free-device-log-mouse-classifier.json`
- experiment: `prompt/coordination/experiments/T4/20261106T1128Z-T4-chat-device-mouse-release-evidence-p8m2.json`
- event: `prompt/coordination/B_TEAM/events/T4/20261106T1128Z-T4-chat-device-mouse-release-evidence-p8m2.json`
- handoff: `prompt/coordination/discussions/INPUT-005/20261106T1128Z-T4-chat-device-mouse-release-evidence-p8m2-to-T5.md`
- source and tests commit: [4d18a09](https://github.com/alwansan/raf/commit/4d18a096707d4c7fc134e967e7f807aeee8a5c0e)
- exact [CI42210561898](https://github.com/alwansan/raf/actions/runs/42210561898) **COMPLETED SUCCESS**, same SHA `4d18a096707d4c7fc134e967e7f807aeee8a5c0e`, job `127867883932`

## Distinct diagnosis

T4 previous [CI42208882663](https://github.com/alwansan/raf/actions/runs/42208882663) implemented privacy-safe `input.physical_mouse_capture_release_outcome` with eight fixed labels at the actual UI-thread callback, while the old `physical_mouse_capture_released` event records only Unity's **release request**. The existing source-free mobile session parser `scripts/t4_verify_device_world_save_log.py` classified world/create/save/load but silently ignored all mouse events, so the next owner phone logs would not expose why pointer release was skipped or the JNI release method was reached. The scheduled T4 1042Z session read release owner-View fix without modifying it; no collision.

## Actual solution

- `scripts/t4_verify_device_world_save_log.py`: recognize six bounded `input` markers (capture requested, Unity-side release requested, new Android UI release outcome, view changed, capture lost, relative motion). Parse the **eight** native release result categories with an anchored exact allowlist `result=<fixed_status>; native_release_confirmed=false`. Reject unknown values, private extra fields or forged `native_release_confirmed=true` to `unparseable` and attach a safe anomaly label without ever exposing raw detail. Count outcomes per logger session, deduplicate replayed startup/segment lines with existing hash-only-in-memory checks. Preserve strict sequence/UTC/queue-overflow/snapshot semantics, compatibility with older logs and no implicit world/playability claims.
- Output only per-session fixed-category counts and booleans `native_release_call_returned_observed`, `native_mouse_release_by_os_proven=false`, `hardware_mouse_360_camera_proven=false`. The last two are necessarily false on this log evidence: a returned Java call is not an Android OS capture-state proof and relative events are not direct evidence of full 360-degree gameplay.
- `tests/test_t4_verify_device_world_save_log.py`: **five new source-free negative/positive tests** for all eight categories, view/loss/relative events without false gameplay proof, private/forged extra data rejection, invalid detail object fail-closed, and duplicate logger startup replay. Existing 15 parser tests retained; 2 overflow guard tests retained.

## CI and limits

- Final [CI42210561898](https://github.com/alwansan/raf/actions/runs/42210561898) immutable source SHA `4d18a096707d4c7fc134e967e7f807aeee8a5c0e`, job `127867883932` **SUCCESS**. Actual job logs: 20/20 parser tests, including five new cases all PASS; 2/2 queue overflow tests PASS; **22/22** total. No original game data or phone logs checked out, no Unity or player built. Existing workflow display step still says 17 historical tests, actual job reports 20+2; source test count is authoritative and the label can be refreshed with a functional workflow change later, avoiding an extra duplicate CI today.
- Only two T4 parser/test source files changed. No native mouse capture/game SaveAndLoad, original .rgd, shader/water, Settings/audio, touch, UI, T5 packaging, game assets, Unity CI or other agent-owned files touched. Branch feature/android-native-port only, no force push or cancellation.
- Source-free synthetic logs **DO NOT** establish that the new native code executes on a phone, that physical mouse capture was released by Android, that camera turns >360 degrees, or that Save/Load survives full process death. Older owner phone [artifact42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) remains proven only for its own source and device session. Original .NET8 [CI42201568118](https://github.com/alwansan/raf/actions/runs/42201568118) verified byte-exact original Save on 7 genuine owner worlds; not Unity/IL2CPP.

## Next step

T5 should hand off one exact signed APK + matching OBB (manifest/package/versionCode, immutable source SHA, APK/OBB hashes). On owner physical mouse+keyboard phone test 360-degree camera, game/menu cursor, pause, focus/home transition and reconnect, then upload bounded `raft-logs/*.jsonl` if needed. Run `python3 -m scripts.t4_verify_device_world_save_log --input <local-directory>` privately; only aggregate report shared. For saved world, force stop/restart and load the same world with owner confirmation. Never report native release OS-state or gameplay success from these marker counts alone. INPUT-005 and LOCAL-005 OPEN, NOT_READY 0/3.
