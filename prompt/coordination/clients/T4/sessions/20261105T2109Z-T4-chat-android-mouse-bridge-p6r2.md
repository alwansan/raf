# T4 chat — Android physical pointer-capture bridge

- session_id: 20261105T2109Z-T4-chat-android-mouse-bridge-p6r2
- origin: chat
- status: completed_source_integrated_device_unverified
- base_sha: 2db482cfb80f2a26f8de7e715d842a1819191990
- resumed_from_sessions: 20261105T2050Z-T4-chat-original-mouse-routing-q9c4; 20261105T2040Z-T4-scheduled-p4m8
- issue_id: INPUT-005
- work: prompt/coordination/work/INPUT-005/T4-20261105T2109Z-T4-chat-android-mouse-bridge-p6r2-pointer-capture.json
- experiment_key: T4-original-legacy-8axis-2cursorlock-ILSpy11.2-ZIP2SHA15964ea8-Unity2021-Android26-captured-listener-v1
- resource_key: original-ZIP2-ILSpy-CPU-readonly
- intended_files: prompt/coordination/work/INPUT-005/T4-20261105T2109Z-T4-chat-android-mouse-bridge-p6r2-pointer-capture.json; prompt/coordination/clients/T4/sessions/20261105T2109Z-T4-chat-android-mouse-bridge-p6r2.md; android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs; scripts/t4_adapt_original_mouse_axes.py; tests/test_t4_adapt_original_mouse_axes.py; .github/workflows/raft-t4-mouse-capture-bridge.yml; prompt/coordination/experiments/T4/20261105T2109Z-T4-chat-android-mouse-bridge-p6r2.json; prompt/coordination/B_TEAM/events/T4/20261105T2109Z-T4-chat-android-mouse-bridge-p6r2.json
- current team: T1 FFT, T2 water, T3 render, T5 delivery/UI; no T4 live CI observed at scope entry. New scope avoids all other T file edits.
- proven baseline: original ZIP2 DLL ILSpy source CI42107935479 SUCCESS; 2395 files, direct original Mouse X/Y 4+4, cursor lock assignment 2, MyInput mouse axis 0; only lexical evidence.
- owner device: artifact 42058825739 playable world/save/reopen bounded; mouse stops at edge and black OS cursor/system bars; no newer phone confirmation.
- objective: implement minimally intrusive native Android View pointer capture + original legacy GetAxis bridge, preserving cursor state, menu/focus, keyboard/touch and RGD. No Unity native build automatically in this scope.

## Evidence and result

## Verified implementation and CI (2026-11-05 21:22 UTC)

- **Source integrated**: `AndroidPhysicalMouseCapture.cs` requests API26+ View pointer capture on Android UI thread only when original cursor-lock intent and a physical mouse are present. Captured relative X/Y reach a frame-locked accumulator; menu/pause/focus/Escape/disconnect release, normal `Input.GetAxis` remains fallback, synthetic LEFT-touch pointer and input devices are not replaced. JNI event wrappers are disposed on callback; requested/released/relative event diagnostics added.
- **Original adaptation**: `scripts/t4_adapt_original_mouse_axes.py` authenticates original ZIP2 Assembly-CSharp.dll 3211776B SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e` and rejects source drift unless direct Mouse X=4, Mouse Y=4, Cursor.lockState=2. Only original Assembly-CSharp C# staged sources rewritten, original .meta/GUID, PC DLL and save format untouched. Main native workflow stages this patch and copies both new platform C# files; original `AndroidTestDiagnostics` singleton installs capture alongside `AndroidTouchPointer`; offline compile stage includes both.
- **CI**: [42111826974](https://github.com/alwansan/raf/actions/runs/42111826974) **SUCCESS**: 7 routing +7 rewrite +6 integration Python checks, 13 executable .NET frame/concurrency checks, authentic Unity2021 managed C# class compile, original private ILSpy11.2 source rewrite 4+4+2 across five original files; no proprietary source/artifacts published. [42111682510](https://github.com/alwansan/raf/actions/runs/42111682510) **SUCCESS** after JNI lifecycle fix. [Original Android startup managed compile 42111311168](https://github.com/alwansan/raf/actions/runs/42111311168) and [platform 42111302568](https://github.com/alwansan/raf/actions/runs/42111302568) **SUCCESS** at respective staged commits. See [experiment](../../experiments/T4/20261105T2109Z-T4-chat-android-mouse-bridge-p6r2.json).
- **Boundaries**: no real Unity Editor IL2CPP/APK build or POCO F5 Pro device capture test in this session. Original world/save/reopen phone proof from artifact42058825739 is bounded to that older SHA; do not claim current native acceptance. Cursor sensitivity/orientation, external buttons/wheel, black OS cursor in menu, system bars, game-state capture transitions and world/save regression still require on-device check. Audio/Settings, touch and T5 UI/Resolution unmodified.
- No Actions canceled or full native build requested. Source scope complete; INPUT-005 remains OPEN.

## Next T4 / scheduled handoff

On a future T5 signed candidate verify exact APK+OBB manifest/commit. With physical mouse test unlimited gameplay camera rotation, native capture requested/relative/released logs, menu cursor and bars, Escape/menu/pause/focus/unplug release, external buttons/wheel, keyboard/touch, and playable world/save/exit/reopen. If capture never starts, inspect `originalLockIntent`/physical device/focused View before patching camera. On failed relative motion, check proxy event dispatch and Y/sensitivity; no fake flags or InputSystem duplicates.

