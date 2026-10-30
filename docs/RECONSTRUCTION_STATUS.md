# Raft PC → Android native port: reconstruction state

Date: 2026-10-30. Evidence from verified CI runs on `feature/android-native-port`. All raw C# sources and extracted game scenes were kept TEMPORARILY on GitHub-hosted runners and not uploaded or committed.

## Checkpoints reached

| Gate | Observation | Verification |
|---|---|---|
| Exact Unity version | 2021.3.45f2, `globalgamemanagers` | https://github.com/alwansan/raf/actions/runs/41016548670 |
| Game assets exported | 243 raw files from limited non-LFS sample | https://github.com/alwansan/raf/actions/runs/41017866546 |
| Editor-scene recovery | **3 `.unity` scenes**, 22 `.meta` files among 64 files | https://github.com/alwansan/raf/actions/runs/41021307639 |
| Mono class metadata | 3,032 managed types, 19,512 methods | https://github.com/alwansan/raf/actions/runs/41021653681 |
| REA static native imports | 131 PartyWin32, 21 PartyXboxLiveWin32, 3 lz4unity P/Invoke declarations | https://github.com/alwansan/raf/actions/runs/41020808394 |
| REA system call graphs | `Raft_Network` 118 methods/920 edges; `SaveAndLoad` 48 methods/741 edges | https://github.com/alwansan/raf/actions/runs/41021754371 |
| ILSpy narrow C# recovery | `Raft_Network` and `SaveAndLoad` each decompiled successfully | https://github.com/alwansan/raf/actions/runs/41021894016 |
| ILSpy complete C# project export | **2,394 `.cs` files**, **251,725 lines**, **6,429,375 source bytes**, **1 `.csproj`** | https://github.com/alwansan/raf/actions/runs/41022023788 |
| Unity export with script processing | Three scene files but **zero `.cs` files**; exporter process returned success, integration gate failed as intended | https://github.com/alwansan/raf/actions/runs/41022158992 |

All completed Unity scene recovery is **structural only**: no successful Unity Editor import/compile, no Android APK, no verified scene GUID-script linkage, no gameplay functionality is claimed.

## Network and save coupling: immediate implementation priorities

1. `Raft_Network` is the game's main network orchestration class. Its symbols include `HostGame`, `TryToJoinGame`, `get_InSinglePlayerMode`, and `get_IsHost`. REA found 920 call edges in this class including **29** categorized as Steam/Party calls and **13** categorized as Unity network calls (target categories are heuristic).
2. `SaveAndLoad` contains `Save`, `Load`, `SaveGame`, `SaveUser`, `SaveWorld`, `SaveWorldAsync`, `RestoreUser`, `RestoreRGDGame`. Its `GetSettingsPath` and `Start` methods call `Steamworks.SteamUser.GetSteamID` and `UnityEngine.Application.persistentDataPath`. **Save location and identity are coupled to Steam**, so removing Steam requires stable local profile identity and careful save path transition.
3. `SteamManager.Awake` calls `Steamworks.SteamAPI.Init` and can call `UnityEngine.Application.Quit`. Offline Android startup needs an explicit platform bootstrap/fallback rather than merely deleting Steam DLLs.
4. `Unity.Netcode.Runtime` and `Unity.Networking.Transport` managed DLLs are present. Reuse *might* be feasible but is not proven; the original gameplay and Windows Party integration need decoupling first.

## Compiled game vs reconstructed project

- Binary DLL decompilation yielded source candidate text. This does not recover original project references, source-generated files, exact `.meta` GUIDs, serialized script links, original package versions, shaders, imported textures, or third-party plugin licenses automatically.
- AssetRipper produced a partial Unity project with scene YAML and project settings, but it did not automatically emit C# scripts from the tiny scenes even when the `Managed/` folder was included.
- The next independent gate is **script GUID/MonoBehaviour linkage analysis**, not blindly copying thousands of C# files into `Assets` and calling it build-ready.
- Beyond that: complete needed asset dependencies, import in Unity 2021.3.45f2, fix C# references, and Android ARM64 build verification.

## Safety, storage and cost

- Repo currently public; it contains commercial assets owned by third parties. Do not distribute original game files or reconstructed decompiled source without applicable permission.
- The 18 Git LFS pointers advertise 6.472 GiB of original payloads. No experiments in this series downloaded them. Avoid surprise LFS bandwidth use.
- Large dependencies need `df` prechecks; all added CI experiments implement this.
- Keep `main` and `zip` untouched; develop on `feature/android-native-port` only.
- No need for the user to upload ILSpy or AssetRipper as both tools installed and ran on GitHub Actions.

## Practical next experiments

1. Inspect how many `MonoBehaviour` script references appear in sampled `.unity` files and why AssetRipper didn't emit `.cs` files.
2. Audit missing Unity GUID/serialized references; select the first lowest-dependency scene to import.
3. Plan a clean platform identity adapter that replaces Steam ID for saves but preserves existing save data formats.
4. Decide on Unity Editor and legal license activation method before adding import/build CI.
5. Move toward offline single-player vertical slice; only then add phone-hosted LAN multiplayer.

## High-priority integration blocker observed in five scenes

[Completed serialized script reference audit](https://github.com/alwansan/raf/actions/runs/41022464657):

- Input samples: `level0`, `level1`, `level37`, `level38`, `level39`, their available non-LFS sharedasset streams, `globalgamemanagers`, `boot.config`, and `Managed/*.dll` assemblies.
- Exported **5 `.unity` scenes**, **982 `.meta` files**, **zero `.cs` files**.
- The exported scene YAML has **13,969** `MonoBehaviour:` records and **13,969** `m_Script:` fields.
- All parsable inline script references in this sample shared **one GUID value**; it was not among the exported `.meta` GUIDs. This may be an export placeholder or other limitation: **do not interpret this as evidence all source behaviours have one original script**.
- This proves structural Unity script linkage is **not** recovered by current AssetRipperCLI sample. ILSpy output cannot be copied over without reconstructing script identity, namespaces, serialized fields and appropriate `.meta` files/GUIDs.
- Next gate: determine whether use of official AssetRipper 2.0, complete script data, or a custom MonoScript mapping/export will preserve distinct source script identities; only then test Unity Editor import.
