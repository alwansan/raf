# T4 → T5 / LOCAL-005: real CL .rgd files successfully load in original CLR; next test is phone

- author/session: T4 20261105T1838Z-T4-chat-cl-rgd-real-9p4s
- target: T5 native APK owner / local world source
- source SHA: cbbc296c95b53d13354661eef3bd5212456f5364
- CI: https://github.com/alwansan/raf/actions/runs/42086855402
- immutable CL: 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29
- immutable original DLL ZIP2: 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- status: READONLY_AUTHENTIC_ORIGINAL_CLR_SUCCESS_NOT_ANDROID

Three actual APK86 CL-generated user world RGD files (11255B, 310140B, 309863B) all passed genuine original .NET8 BinaryFormatter.Deserialize and actual compiled original SaveAndLoad.Load<T> invocation; returned nonnull objects matching original game CLR type for all three, no error category. Actual Git object byte identities and original Assembly-CSharp SHA/151 references authenticated. Wrong RGD rejected prior to deserialization. No original/user save data or private CLR member names printed or uploaded. This is stronger than prior 2941B shipped-seed check. It argues against universal save-file unreadability as cause of Android world hang, not proof of completeness or Android compatibility.

APK86 CL real sequence: existing save opened, HostGame->MainScene->InternalAddPlayer; SaveWorld and SaveUser return, then SteamUserStats.StoreStats throws steam_api64 in SaveGame within OnWorldRecieved before original world completion assignment. Current source already has B50 local Android StoreStats guard, and T5 native run42058825739 reconstruct job succeeded, but Release publication failed HTTP403. Source-based fix not yet owner phone-tested; cannot infer all other callbacks succeed. No attempt made to add host fake, set WorldHasBeenRecieved or change serializer/flags.

**P0 next:** T5 rescue signed artifact `raft-android-test-delivery` ID13441227298 (expires 2026-11-06 18:19Z) or signed checkpoint ID13441766832 (expires 2026-11-07 18:18Z), from run42058825739, without duplicate heavy Unity build, with authorized release credentials and verified digest/parts. Then owner offline airplane-mode phone: create/new and existing world; log HostGame, OnSceneLoaded, InternalAddPlayer, WorldHasBeenLoaded.firstMoveNext, OnWorldRecieved.enter/exit, SaveGame.enter/exit/exception, WorldHasBeenLoaded.originalCompletionAssigned, Load.caughtException, Save/Load argument snapshots; actual visible raft/player controls, genuine save and complete app process kill/reopen same world. Post-device first failure, patch exact host/RPC/save callsite preserving real callbacks. LOCAL-005 OPEN, NOT_READY 0/3; sound/Settings preserved, touch deferred.
