# T4 chat — original mouse-look routing before Android pointer-capture bridge

- session_id: 20261105T2050Z-T4-chat-original-mouse-routing-q9c4
- origin: chat
- status: active
- base_sha: c365d724bb7fe17484a6e6f033e1c7b24f7beb8d
- resumed_from_sessions: 20261105T2040Z-T4-scheduled-p4m8; 20261105T1935Z-T4-scheduled-v4c9
- issue_id: INPUT-005
- work: prompt/coordination/work/INPUT-005/T4-20261105T2050Z-T4-chat-original-mouse-routing-q9c4-camera-route.json
- experiment_key: T4-mouse-ILSpy-originalDLL-zip2-15964ea8-Unity2021-InputSystem1.7-source-routes-v1
- resource_key: original-zip2-15964ea8-Assembly-CSharp.dll-readonly-cpu
- intended_files: scripts/t4_original_mouse_routing.py, tests/test_t4_original_mouse_routing.py, .github/workflows/raft-t4-original-mouse-routing.yml, own experiment/event/session
- established evidence: owner phone run 42058825739 source e9c358ed confirmed playable world/save/reopen; physical Android pointer remains uncaptured; scheduled T4 2040Z performed read-only audit, no fix.
- current concurrent work: T5 UI right safe-area acc964d and 96f414 committed, platform and original-startup CI in_progress at 20:46Z. Avoid T5 files, touch, Unity native dispatch, release. Do not duplicate current Actions.
- plan: bounded original compiled mouse-input consumer evidence; test parser with synthetic controls; GitHub Actions reads pinned ZIP2 original DLL without LFS, outputs only safe aggregate (no original code/raw assets); no camera edits before route verified.

## Results

## Verified original compiled route result — 2026-11-05 20:56 UTC

- Origin chat; resume from scheduled 20261105T2040Z-T4-scheduled-p4m8; issue INPUT-005. Scope registration commit 36057ea09aaf3046301328a797a1f29d235a2071.
- Code commit fe9a9ae5264821304923d6bac04d21089f3a3df8 adds scripts/t4_original_mouse_routing.py, tests/test_t4_original_mouse_routing.py and dedicated isolated workflow.
- GitHub Actions https://github.com/alwansan/raf/actions/runs/42107935479 SUCCESS at immutable commit fe9a9ae5; job 127527607675, 7/7 source-free negative controls passed, original Assembly-CSharp.dll 3211776B and SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e verified.
- Private ILSpy 11.2.0.10050 enumerated 2395 C# files: 4 direct Input.GetAxis Mouse X and 4 Mouse Y syntax sites, all 8 in camera/player-named files; 0 MyInput.GetAxis Mouse X/Y, 0 Mouse.current.delta, 2 Cursor.lockState assignments, 30 total GetAxis-family syntax sites.
- Findings are lexical and file-name heuristic, NOT verified runtime camera call graph. Original private/decompiled game source was not published. Android pointer capture not implemented; no Unity/IL2CPP/device test or new native build; no touch, T5 UI, world/save, audio, Settings or original assets altered.
- A sole InputSystem virtual Mouse injection is insufficiently supported as a gameplay-camera fix. Design an Android API26+ View.requestPointerCapture relative mouse bridge to original legacy Input.GetAxis consumers, preserving pointer buttons and wheel, original menus, pause/focus loss and navigation.
- Session scope complete; INPUT-005 OPEN. Owner-confirmed world/save/reopen from phone artifact 42058825739 remains bounded and unchanged.

## Next

Implement and test Java/C# capture lifecycle and exact original legacy axis adaptation on a separate authorized scope. Verify Android API26 view focus, captured event relative motion, release menu/pause/focus loss/unplug, no duplicate touch/physical input, UI cursor, and phone world/save regression. Coordinate with T5 native builds; do not assume success from source-only CI.

