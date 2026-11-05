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

## Actual verified real-world CL RGD execution — CI42086855402

[**GitHub Actions 42086855402**](https://github.com/alwansan/raf/actions/runs/42086855402) completed SUCCESS at immutable source cbbc296c95b53d13354661eef3bd5212456f5364 (job127454186223), original CLR DLL exact 3211776B and SHA `0a6f0527...`, **151** authentic managed siblings, user-owned original CL@5394407b blob identity & size verified before deserialization (no raw user game bytes, paths, types or field values published).

This experiment **actually deserialized three user-created .rgd files and invoked the original compiled SaveAndLoad.Load<T>** through reflection with authentic CLR root type, not simulated or purely synthetic:
- **small** new-world RGD 11255B: BinaryFormatter object created; original game CLR root class=true, actual original SaveAndLoad.Load<T> invoked=true, returned matching nonnull original class=true; categories NONE.
- **large_a** 310140B: same exact success and categories NONE.
- **large_b** 309863B: same exact success and categories NONE.
- Negative intentionally wrong-content source was rejected before formatter or report creation.
- The pinned direct source reference was ZIP2 commit15964ea8, managed sibling ref02e9fba7. CL names/user identifiers and original CLR runtime exception/string detail never appeared in logs. No raw game material staged in the public Git repo; test writes only safe bounded aggregate evidence.

**Interpretation:** unlike earlier original shipped seed Data.rgd, these are genuine APK86 CL user-generated world saves; all three are structurally loadable via original compiled CLR game method in the isolated .NET8 environment. A universal malformed NRBF/schema file is not a supported explanation for the APK86 symptoms in these exact three files. They do not show whether world state is complete or playable, local host callbacks were delivered, objects persisted, original user progress was preserved, Unity Mono/IL2CPP Android deserialization works, or full-process relaunch loads. 11255B new world is much smaller than two ~310KB saves, **not** proof of corruption or world completeness.

Source addition `android-port/Experiments/T4/ClWorldRgdRuntime/{Program.cs,ClWorldRgdRuntime.csproj}` commit08052de7ae2d4d5c5dba7a62809cc6748ce11dda, isolated exact-input workflow `.github/workflows/raft-t4-cl-real-world-rgd-readonly.yml` commit cbbc296c95b53d13354661eef3bd5212456f5364, no native source/serializer/Steam/Unity change. T5 handoff: `prompt/coordination/discussions/LOCAL-005/20261105T1838Z-T4-chat-cl-rgd-real-9p4s-to-T5.md`. LOCAL-005 OPEN NOT_READY 0/3.

**Next:** owner P0 demands actual Android runtime. Source guard for APK86 Steam StoreStats is already present and in build overlay (see native run42058825739 reconstruct SUCCESS), but **new build publication failed Release creation HTTP403**, artifact retained. Prioritize T5 authorized publication/recovery, owner phone offline HostGame->MainScene->OnWorldRecieved->SaveGame guard->originalCompletionAssigned->playable player/raft and full-exit same-world .rgd replay with first escaped exception trace. No duplicate native Unity build or fake flags.
