# T4 chat — actual user-generated CL save RGD against authentic original CLR loader

- session_id: 20261105T1838Z-T4-chat-cl-rgd-real-9p4s
- origin: chat
- issue_id: LOCAL-005
- status: active
- base_sha: 4c5b77b3499eb5ec5f82878409532975156d860f
- resumed_from_sessions: 20261105T181919Z-T4-chat-overflow-ci-9dzc8; 20261105T1736Z-T4-chat-rgd-return-local-stores-r6n8
- work: prompt/coordination/work/LOCAL-005/T4-20261105T1838Z-T4-chat-cl-rgd-real-9p4s-authenticated-cl-world-rgd.json
- experiment_key: T4-CL5394407b-7-world5-8-worldgh-and-sad-authentic-blob-sha-runtime-original-LoadT-v1
- resource_key: original-DLL-zip2-15964ea8-readonly-CPU
- CI: pending

## Owner P0 request; actual evidence
CL main 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29, 4-Nov APK86 session versionCode86. Original SaveAndLoad.SaveGame flow reaches SaveWorld and SaveUser after HostGame->MainScene->InternalAddPlayer, then uncaught DllNotFoundException steam_api64 at SteamUserStats.StoreStats. Current source already has authenticated conditional Android guard in scripts/instrument_android_runtime_operations.py, and native T5 run42058825739 reconstruct SUCCESS but Release publish failed HTTP403; not verified on device. Original shipped 2941B Data.rgd managed deserialized in CI42043768798, not a CL user-generated world. Current CL user-generated original-format .rgd paths actually exist: one small 11255B and two large ~310KB. Mere size/existence does not prove contents or Load<T> return.

## Scope
Test **real CL provided world RGD bytes**, not synthetic data, against the original game compiled CLR loader using pinned source and reproducible CI; preserve body/source privacy (no original bytes/source or game data artifact); no Unity or T5 native mutation, no duplicate scheduling. If CLR succeeds, infer only managed compatibility for these inputs, not reachable world/player readiness. If fails, classify safely, determine original vs Android differences. No success flags, .meta/GUID or serialization edits.

## Next
Publish code and isolated CI proof and report exact artifact/result for handoff to T5. Stop only this narrow scope; LOCAL-005 remains OPEN NOT_READY 0/3, phone must test offline playable world and genuine user world RGD across full process restart.
