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

## Updated diagnosis: script-GUID blocker SOLVED in sample (supersedes previous section)

Evidence: [UnityPy 3,827 MonoScript records](https://github.com/alwansan/raf/actions/runs/41023529350) and [successful script-linked export](https://github.com/alwansan/raf/actions/runs/41023760680).

The previous section documented a missing-GUID state **before the dependency was included**. The original sample omitted **`globalgamemanagers.assets`**, a 0.72 MiB file tracked by regular Git containing 3,827 original `MonoScript` records. The prior `deadbeef` GUID was an AssetRipper export placeholder, not evidence that all original scripts shared one identity.

After including this file and `Managed/*.dll`, the five sample scenes exported with 3,810 source-stub `.cs` files and 3,810 corresponding `.cs.meta` files. All 13,969 `m_Script` references in those five scenes had a matching exported `.cs.meta` GUID (296 distinct GUIDs), with **zero** placeholder uses. This **verifies script GUID linkage in the sample**, but not runtime behavior, compiler correctness, prefab completeness, or the remaining game world.

The next gate is `--script-content-level Level0` C# recovery and comparison with ILSpy, before attempting a Unity 2021.3.45f2 Editor import.

## Level0 code fidelity and safe C# overlay

[Level0 AssetRipper run](https://github.com/alwansan/raf/actions/runs/41023910696) produced 3,810 script sources and retained all 13,969 scene GUID links, but individual gameplay class outputs like `SaveAndLoad.cs` were only ~2.6 KiB, compared to ~48.7 KiB of ILSpy-decompiled source. Therefore the AssetRipper source files are **not yet verified as full game logic**. A new CI-only overlay tool `scripts/overlay_ilspy_gameplay.py` combines source from ILSpy with GUID-preserving Unity meta files using conservative unique class filename matching. The merged code is confined to an ephemeral GitHub runner, pending count and consistency checks; no original game C# was added to the public repository.

## Implementation progress: ILSpy source overlay proven in limited Unity export

Confirmed [namespace-checked CI](https://github.com/alwansan/raf/actions/runs/41024417472): **1,568** strictly matched `Assembly-CSharp` source files replaced AssetRipper script templates with C# from ILSpy, while **13,969/13,969** five-scene script GUIDs remained linked. 85 apparent filename matches were intentionally rejected because their namespaces disagreed; scripts from third-party assemblies are not overwritten. Main classes `Raft_Network`, `SaveAndLoad`, `GameManager`, and `SteamManager` all had substantive ILSpy source substituted. [Six synthetic safety tests](https://github.com/alwansan/raf/actions/runs/41024504209) passed.

**Do not assume** this produces a compilable game or fully functional logic. Work remaining: resolve excluded/unmatched classes, editor import errors, platform/Steam/Party integration, real dependencies in 18 LFS files, shaders/mobile assets and Android-specific runtime. Never publish game source/assets publicly.

## Broad scene coverage update — all 40 levels

[All-scene GUID test succeeded](https://github.com/alwansan/raf/actions/runs/41024647631): the 40 `levelN` game files each generated Unity `.unity` scenes and all **64,642** scene script reference GUIDs matched exported script metadata (517 distinct script GUID values; zero deadbeef placeholder). The missing global MonoScript registry is resolved **for script IDs**. This does not validate non-script asset references or shaders. Existing ILSpy source overlay in five-scene samples (1,568 strictly matched classes) still needs full-project compile validation.

## Remaining critical blocker: missing mesh and non-script links

[Successful 40-scene deep GUID classification](https://github.com/alwansan/raf/actions/runs/41025306987) confirms that **none** of the 393,450 `deadbeef` placeholder uses is an `m_Script` reference, so the script-GUID linkage milestone remains intact. However **198,114** are `m_Mesh` fields, **191,091** are list/sequence elements whose parent is not proven, and smaller counts belong to SpeedTree wind assets, animator controllers, avatars, sprites, etc. Unity built-in e/f GUID references are normal and not missing game files. One nonbuiltin GUID has a single unresolved reference in a Varuna Point scene.

**Current immediate gate:** restore mesh / material / terrain / prefab dependencies sufficiently for Unity Editor import. Do not claim complete reconstruction from the repaired script links. Audit missing files from LFS by exact path, transfer budget and type; inspect Unity built-in primitive mesh references separately. This does **not** justify unrestricted downloading of the 6.472 GiB LFS payload.

## New broad mesh recovery gate

[Regular Git assets export](https://github.com/alwansan/raf/actions/runs/41025868800) reduced `deadbeef` placeholders from 393,450 to **199,156** (-49.4%) across 40 scenes, including mesh refs from 198,114 to **94,152** (-52.5%); 64,642/64,642 script links still matched. No LFS transfers were needed. An independent [all-scene UnityPy source Mesh PPtr audit](https://github.com/alwansan/raf/actions/runs/41026113254) found **85,525** mesh pointer uses targeting the missing `resources.assets` LFS object, **42,137** targeting regular Git `sharedassets30.assets`, and **5,423** targeting missing `sharedassets0.assets`. Pointer uses are not distinct meshes or validated runtime recovery.

See [MESH_RECOVERY_FINDINGS.md](MESH_RECOVERY_FINDINGS.md). A safe **manual-only** Git LFS pilot can fetch `resources.assets` (106.4 MiB) first, verifying declared size and sha256 and checking the export delta. It deliberately will not auto-run on push, because GitHub LFS bandwidth costs cannot be inspected in this context.
