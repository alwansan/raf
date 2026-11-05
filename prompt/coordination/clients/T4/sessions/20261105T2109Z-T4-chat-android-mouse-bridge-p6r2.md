# T4 chat — Android physical pointer-capture bridge

- session_id: 20261105T2109Z-T4-chat-android-mouse-bridge-p6r2
- origin: chat
- status: active
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

Pending implementation/testing.
