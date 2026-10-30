# Raft Android port — verified research findings (2026-10-30)

**Source**: `alwansan/raf`, `zip`; work branch: `feature/android-native-port`.
This document tracks only evidence obtained from repository metadata or successful read-only GitHub Actions jobs. It is not proof of Android compatibility.

## Job 1: inventory — SUCCESS

https://github.com/alwansan/raf/actions/runs/41016548670

| Item | Confirmed observation |
|---|---|
| Unity engine version embedded in `Raft_Data/globalgamemanagers` | **2021.3.45f2** |
| File count from `Raft/` checkout | 366 |
| LFS pointers in checkout | 18 |
| Total LFS original bytes claimed | 6,948,949,688 (6.472 GiB) |
| Free bytes on Actions runner during this run | 92,860,522,496 (86.5 GiB) |
| `Raft_Data/Managed/Assembly-CSharp.dll` | Present |
| `Raft_Data/globalgamemanagers`, `boot.config` | Present |
| Unity Editor `Assets/`, `ProjectSettings/` folders | Not present |

The 368 count from the Git tree includes 2 root-level files in addition to 366 game files. LFS pointers are not their original payload bytes. No full LFS objects were downloaded in this job.

## Job 2: managed assembly metadata — SUCCESS

https://github.com/alwansan/raf/actions/runs/41016883723

Static parser: `dnfile==0.18.0`, installed successfully on GitHub Actions. This inspects metadata, does not load/execute DLLs, and does not decompile/reproduce proprietary source code.

| Item | Observed |
|---|---:|
| Managed type definitions (excluding `<Module>`) | 3032 |
| Method definitions | 19512 |
| Field definitions | 16920 |
| P/Invoke declarations | 155 |

**Key referenced assemblies:** `Unity.Netcode.Runtime`, `Unity.InputSystem`, `UnityEngine.InputLegacyModule`, `FMODUnity`, `PlayFab`, `com.rlabrecque.steamworks.net`, TextMeshPro, Unity UI, Analytics, Unity Services RemoteConfig, terrain/physics, and many core modules.

**Native module references declared in assembly:** `PartyWin32`, `PartyXboxLiveWin32`, `lz4unity`.

**Interpretation:** multiple Windows-specific network/native integrations are present, so a simple change of Unity build target is not enough. Importantly, Unity Netcode is **already referenced**; evaluate reuse or refactoring before deciding to add a different framework like Mirror. A referenced assembly alone is not proof that it implements all multiplayer behavior.

**Keyword-based type matches (overlap possible; NOT subsystem size):**

| Search group | Matching type names |
|---|---:|
| Player | 118 |
| Raft | 127 |
| Ocean | 248 |
| World / islands | 112 |
| Survival | 22 |
| Items / crafting | 185 |
| Building | 25 |
| AI | 297 |
| Multiplayer / network | 162 |
| Save/load | 36 |
| UI/input | 111 |
| Audio | 58 |
| Platform | 269 |

These are rough case-insensitive keyword matches, not mutually exclusive categories, and do not constitute verified working features.

## Current blockers

1. No source Unity editor project `Assets/Packages/ProjectSettings`; recovery and repair required.
2. LFS objects declared but availability not checked; downloads have possible bandwidth costs.
3. Windows native DLLs and modified executable-related files must be quarantined, not run or ported directly.
4. Gameplay dependencies may be tightly coupled to Steam/Party and Unity Netcode.
5. Need specific tests of AssetRipper output, GUID restoration, Shader/material compatibility, mobile FMOD and license/build setup.
6. Existing repository is PUBLIC with third-party commercial game assets; do not distribute proprietary content or released APK publicly without rights.

## Next engineering experiment

- Read network/host/save class **metadata** from the managed-audit artifact to choose networking architecture.
- Attempt a tightly scoped read-only sample asset export after checking free storage and exact LFS target size (not wholesale downloads).
- Prepare Unity 2021.3.45f2 import validation only after restoring a minimal, legally usable editor project.
- Do NOT confuse a metadata scan with a complete port.

## Job 3: representative class names and native imports — SUCCESS

https://github.com/alwansan/raf/actions/runs/41016983283

- Multiplayer-related type names observed: `AI_NetworkBehavior_Shark`, `AI_NetworkBehaviour`, `AI_NetworkBehaviour_Animal`, `AI_NetworkBehaviour_Bear`, `AI_NetworkBehaviour_Boss_Varuna`, `AI_NetworkBehaviour_Hyena`, `RequestWorldAsClient` (compiler-generated state machine), `SendResultOnceNetworkIsEstablished`.
- Raft examples: `Anchor`, `Anchor_Stationary`, `Anchor_Throwable`, `Block_Foundation`, `EngineControls`, `FoundationArmor`.
- Save/load examples: `SaveWorldAsync` and `SaveUserAsync` async state machines, `AsyncLoaderManager`, `FastMessageDeserializer`.
- Among the first 150 of 155 P/Invoke declarations: `PartyWin32` (126), `PartyXboxLiveWin32` (21), `lz4unity` (3). Five declarations omitted from the truncated histogram; totals are **not** module totals for all 155.
- **Engineering implication:** investigate replacing the Party native transport while keeping underlying Unity network gameplay components before contemplating a full networking framework migration.

## Tool installation check

- `dnfile==0.18.0`: pip installation **succeeded** on GitHub Actions in Job 2.
- AssetRipper 2.0.0 official binary smoke-test workflow: `.github/workflows/assetripper-tool-smoke.yml`; installation/execution result pending at writing.
- Unity Editor and Android Build Support: not installed (editor project still missing); original game version `2021.3.45f2` available on https://unity.com/releases/editor/whats-new/2021.3.45f2 .

## Tools / automation follow-up (2026-10-30)

- Official AssetRipper v2.0.0 Linux x64: downloaded (~29.4 MiB), SHA-256 verified, executable located as `AssetRipper.GUI.Free`, `--help` succeeds. It exposes web/headless options, not a batch `--cli` command. https://github.com/alwansan/raf/actions/runs/41017427416
- Third-party `nowl-it/AssetRipperCLI` v1.0.1 Linux x64: downloaded (~127 MiB), SHA-256 verified, executable starts and help includes `--cli`. https://github.com/alwansan/raf/actions/runs/41017535607
- AssetRipper sample resource probe (non-LFS only): https://github.com/alwansan/raf/actions/runs/41017638608 (outcome pending at this documentation update).
- These tests execute third-party AssetRipper tools in an isolated CI runner with read-only GitHub permission; **they do not execute Raft.exe or its patched DLLs**. No full game files or proprietary outputs are uploaded.

## Job 4: first real AssetRipper non-LFS sample export — SUCCESS

https://github.com/alwansan/raf/actions/runs/41017866546

- Input selected from this repository: `sharedassets37.assets`, `sharedassets37.assets.resS`, `globalgamemanagers`, copied to an isolated temporary sample.
- No LFS objects were downloaded; before the download the runner storage was checked.
- Tool: checksum-verified `nowl-it/AssetRipperCLI` v1.0.1, CLI with `--mode primary --disable-script-import --ignore-streaming-assets`.
- Export command exit code: **0**; actual resulting file count: **243**; exported output directory approx. **11 MiB**.
- Tool reported individual failures on several built-in UI sprites during export, so this is **partial extraction**, not proof that every game scene/material/script can be reconstructed.
- Neither extracted game assets nor source files were committed or uploaded to workflow artifacts.
- The prior test run 41017638608 exited 0 but printed `Too many arguments were supplied`; that was a false-positive workflow result. The script was corrected to omit extra `true` words for boolean flags and to check the output directory is nonempty. The successful, validated run is **41017866546**.

**Result:** G1 small-sample Unity asset extraction viability is now verified; next gated step is a narrow project-format export and editor import check, before large LFS downloads.

## Job 5: tiny Unity-project mode export — PARTIAL technical success

https://github.com/alwansan/raf/actions/runs/41018053143

- Pinned AssetRipperCLI `--mode unity` exit code **0** and printed `Successfully exported` for Unity **2021.3.45f2**.
- Output: **20 files / ~128 KiB**. Actual directories included `ExportedProject/Packages` and `ExportedProject/ProjectSettings`.
- In this tiny sample, an `Assets/` directory was **not generated**. No scene or prefab recovery is claimed.
- The importer explicitly warned that various companion sharedassets files and `resources.assets` were missing from the intentionally limited sample. Those missing dependencies include files stored via LFS pointers.
- **Interpretation:** restoration of project settings works, but the sample by itself is not a valid/playable Unity project; an Editor import/compile test has NOT happened.
- No exported Unity files were uploaded or committed.

**Next gate:** dependency-aware, license/cost-conscious wider source export, using selected non-LFS assets first. Full Git LFS download is not justified until project scaffolding and Unity/Android licensing are established.

## Job 6: REA 6.8.0 managed artifact analysis — SUCCESS

https://github.com/alwansan/raf/actions/runs/41020338080

- Node 24.22.2 installed via actions/setup-node on Ubuntu runner.
- Official `rea-agents@6.8.0` fetched and installed using npm (**176 packages**).
- Git LFS explicitly disabled. Reported free runner storage after install: approx. **86 GiB** (ephemeral).
- Parsed `Raft/Raft_Data/Managed/Assembly-CSharp.dll` using `rea inspect-managed-artifact <path> --format json`.
- Exit code 0, local JSON evidence size **2,189,390 bytes**.
- Importantly, tool only parsed static data; it did not execute the game DLL, recover an editor project or compile for Android.
- Earlier job attempts failed on `--detail` being an unsupported REA 6.8 CLI flag. Removed it and re-ran successfully.

## Job 7: REA targeted native imports and network methods — SUCCESS

https://github.com/alwansan/raf/actions/runs/41020491527

- `rea inspect-managed-native-boundaries` succeeded and returned 155 P/Invoke import rows and 271 native implementation rows.
- Selected `AI_NetworkBehaviour` using `rea inspect-managed-members --type AI_NetworkBehaviour --format json`: 1 type, 9 fields, 14 methods, 27 call edges, 19 field accesses, 3 user strings.
- Result files were private temporary runner data, with only counts and structure logged; no decompiled game source or extracted game resources were published.
- This supports targeted network-internals research. Actual class semantics and replacement feasibility remain **unverified** until call-site analysis and a compiling Unity project exist.

## Job 8: exact Windows platform P/Invoke scope and network method names — SUCCESS

https://github.com/alwansan/raf/actions/runs/41020808394

REA parsed all 155 `ImplMap` P/Invoke rows in `Assembly-CSharp.dll`:

- `PartyWin32`: **131** import declarations
- `PartyXboxLiveWin32`: **21** import declarations
- `lz4unity`: **3** import declarations

REA also reported 271 native implementation rows. This includes metadata categories that **must not** be assumed to mean extra Windows DLL dependencies.

The selected 14 `AI_NetworkBehaviour` methods include `UpdateHost`, `UpdateRemoteclient`, `Initialize`, `OnRestoreStart`, `OnRestoreFinished`, `Create_SaveData`, `SetNetworkIndexes` and lifecycle methods. This is strong **structural evidence** of separate host vs remote client update paths and save/restore hooks, but not proof that networking transport can be swapped without changes.

See [network migration plan](NETWORK_COMPATIBILITY.md) for tests and migration gates.

## Job 9: selected Unity scene project restoration — SUCCESS (partial scenes)

https://github.com/alwansan/raf/actions/runs/41021307639

- Selected **3** small non-LFS scenes: `level37`, `level38`, `level39`, with their matching `sharedassets37-39.assets`, available `.resS` streams and `globalgamemanagers`.
- Pinned SHA-256 verified `nowl-it/AssetRipperCLI` v1.0.1 invoked in `--mode unity` with script import disabled.
- **64** exported files, including **3** real `.unity` scene files and **22** `.meta` files. Package manifest and Unity project settings generated. Total output bytes **37,076,315** (~35.4 MiB).
- Exit code 0, and CI explicitly checked that Unity scene files exist. This **upgrades earlier evidence** (only 20 settings files) to **genuine serialized Unity editor-scene recovery**.
- No Unity Editor import or compilation yet; incomplete asset dependencies are expected. Three exported scenes do **not** establish a game-ready Unity project.
- No Git LFS payload download, no extracted game data uploaded to artifacts or committed.

## Job 10: Mono gameplay type architecture inventory — SUCCESS

https://github.com/alwansan/raf/actions/runs/41021653681

- 3,032 managed type names and 19,512 method definitions were mapped using `dnfile==0.18.0`, without assembly execution.
- Name-based candidate matches (not exclusive, not an execution path): network 367 (363 non-compiler generated), save 40 (20 non-generated), raft 161, platform 269, input 58.
- Exact relevant types exist: `Raft_Network`, `SaveAndLoad`, `GameManager`, `SteamManager`.
- `SaveAndLoad`: 48 method definitions. Sample names: `Save`, `Load`, `SaveGame`, `SaveUser`, `GetSettingsPath`.
- `SteamManager`: 9 method definitions including `Awake`, `OnEnable` and `Update`.
- `GameManager`: 13 method definitions including `OnWorldRecieved`, `Start` and `OnApplicationQuit`.
- This is a *symbol* inventory; next trace selected call edges and assess network/Steam dependencies before attempting offline bootstrap.
- Reports are created only on ephemeral runners; no proprietary decompiled source published.


## Jobs 11–12: script processing and GUID reference blocker

- [Script processing pilot](https://github.com/alwansan/raf/actions/runs/41022158992): the CLI exporter itself exited with code 0 and generated 3 Unity scenes but **0 C# files**. A strict job assertion therefore correctly marked the project script-integration experiment **FAILED**.
- [Startup and late-scene references](https://github.com/alwansan/raf/actions/runs/41022464657): 5 scenes, 982 `.meta` files, 0 C# files, and 13,969 serialized MonoBehaviour/m_Script occurrences. Regex over serialized script references found one GUID value with 13,969 uses and no matching exported `.meta`. This is an **export result**, not a reliable original script identity count.
- The successful ILSpy export of **2,394 source files** remains independent of the Unity scenes. Do not claim a playable/restored editor project until real scripts, GUID identities, missing resources, and actual Unity compile/import are verified.

## Job 13: identify missing MonoScript registry without Git LFS — SUCCESS

https://github.com/alwansan/raf/actions/runs/41023529350

The previous five-scene export with 13,969 `deadbeef` placeholders lacked a crucial **ordinary Git** game file: `Raft_Data/globalgamemanagers.assets` (~0.72 MiB). UnityPy 1.25.4 enumerated **3,827 MonoScript** objects in this file (the 10 preceding tested files contained none). Example fields include script class, namespace, assembly name and path ID. Scene external dependencies refer to `globalgamemanagers.assets`; e.g. `level0`'s first external is that file. This is a confirmed explanation for previous unresolved identities.

Additional cross-check: [diagnostic run](https://github.com/alwansan/raf/actions/runs/41022996726) confirmed **all 13,969** previous unresolved scene references used the exact placeholder GUID `0000000deadbeef15deadf00d0000000` with Unity script `fileID: 11500000`. This was not an original GUID identity.

## Job 14: Unity project script metadata linkage — SUCCESS (sample)

https://github.com/alwansan/raf/actions/runs/41023760680

AssetRipperCLI 1.0.1 Unity editor project export, **including** `globalgamemanagers.assets`, its regular `.resS`, five sample levels, limited sharedassets and `Managed/*.dll`, recovered:

| Metric | Result |
|---|---:|
| Unity scene files | 5 |
| .cs files | **3,810** |
| .cs.meta files | **3,810** |
| Unique script GUID values referenced in 5 scenes | **296** |
| Scene `m_Script` refs matching exported script .meta GUIDs | **13,969 / 13,969** |
| Placeholder `deadbeef` GUID uses | **0** |

The earlier workflow run 41023682679 failed as it correctly refused the `sharedassets0.assets` Git LFS pointer; next workflow was changed to skip that unavailable LFS input. No large LFS payload was fetched. **Script linkage is valid for these five exported scenes only.** It is not an Editor compilation or scene runtime test; other materials, textures, shaders, DLLs and gameplay behavior may still be missing. Source export used `--script-content-level Level1` (stubs, not proof of recovered gameplay logic).

Next: test script `Level0` export for fuller code, then Unity Editor import/compile gates.

## Job 15: AssetRipper Level0 mode with restored script mapping — PASS, but code fidelity not established

https://github.com/alwansan/raf/actions/runs/41023910696

With `globalgamemanagers.assets` and ordinary managed DLLs supplied, AssetRipperCLI v1.0.1 `--script-content-level Level0` produced:
- 5 scenes, **3,810** `.cs` files and **3,810** `.cs.meta` files;
- **13,969/13,969** GUID references matched, **0** deadbeef placeholders;
- Aggregate **10,219,604** C# bytes and **244,584** lines.
- However emitted `Raft_Network.cs` and `SaveAndLoad.cs` were only **2,644** and **2,643** bytes. ILSpy's focused decompilation of these types was **60,704** and **48,675** bytes respectively. Thus **do not treat Level0 AssetRipper output as verified complete gameplay logic**. Likely script templates/stubs for those types; source contents not distributed.

New trial `.github/workflows/raft-code-overlay-probe.yml` uses the **real ILSpy Mono source**, maps only unambiguous classes from Assembly-CSharp and retains AssetRipper's `.cs.meta` identities. It fails safely if it cannot pair classes, and does not publish raw source or assets.

## Job 16: real CSharp overlay into GUID-preserving Unity scenes — SUCCESS

[Initial successful merge](https://github.com/alwansan/raf/actions/runs/41024183424) replaced **1,653** unambiguous filename matches with ILSpy sources, while retaining all **13,969/13,969** exported scene `m_Script` GUID links.

[Namespace-hardened merge](https://github.com/alwansan/raf/actions/runs/41024417472) narrowed that to **1,568** safe C# overwrites in the five-scene sample, skipping **85** cases where namespaces disagreed. Target scripts that belong to assemblies other than `Assembly-CSharp` were never replaced. Concrete core-file evidence:
- `Raft_Network.cs` from ~2,644-byte AssetRipper script template to **60,704-byte ILSpy decompiled source**.
- `SaveAndLoad.cs` from ~2,643-byte template to **48,675-byte ILSpy source**.
- `GameManager.cs` from ~2,643-byte template to **8,347-byte ILSpy source**.
- `SteamManager.cs` from ~2,644-byte template to **3,074-byte ILSpy source**.

The standalone reusable `scripts/overlay_ilspy_gameplay.py` copies source **only** in an ephemeral local project while preserving the `.cs.meta` file and GUID. [Six synthetic safety tests and full overlay CI](https://github.com/alwansan/raf/actions/runs/41024504209) passed, checking dry run, correct GUID preservation, namespace mismatch, duplicated filenames, other-assembly exclusion, and missing-meta behavior.

All counts measure source file integration only. Not a successful Unity Editor import, compilation, Android build, or complete gameplay recovery. The remaining **221** Assembly-CSharp candidate source files (1789-1568) require separate analysis, as do external plugins and missing LFS assets. Source remains in GitHub-hosted temporary runner only.

A broader `raft-all-scene-links.yml` experiment checks whether the same linking approach works across all 40 scene levels without fetching any LFS file.

## Job 17: all 40 Raft Unity scene files linked to script meta files — SUCCESS

https://github.com/alwansan/raf/actions/runs/41024647631

This wider **read-only no-LFS** experiment staged `level0` through `level39`, `globalgamemanagers.assets`, managed DLLs, and companion configuration, without downloading `sharedassets0.assets` or any LFS resource.

- Exporter exit code **0** and **40 / 40 Unity `.unity` scenes** generated.
- **3,810** C# script templates and **3,810** associated `.cs.meta` files generated.
- **517** distinct script GUIDs used across all 40 exported scenes.
- **64,642 of 64,642** serialized `m_Script` GUID references have matching exported `.cs.meta` files.
- **0** `0000000deadbeef15deadf00d0000000` placeholder GUID uses.
- This **proves exported script identity linkage** for all 40 level files in this sample. It does NOT imply materials, shaders, textures, prefabs, non-script GUIDs, required LFS assets, Unity Editor import/compile or actual Android gameplay work.

A second [all-scene non-script resource GUID audit](https://github.com/alwansan/raf/actions/workflows/raft-all-scene-links.yml) checks remaining asset references and duplicate GUIDs. Full resource availability remains a distinct gate.

## Job 18: classify non-script Unity scene GUID placeholders — SUCCESS

https://github.com/alwansan/raf/actions/runs/41025306987

All 40 Unity YAML scenes were inspected in temporary project output, not published. Previous generic [asset GUID audit](https://github.com/alwansan/raf/actions/runs/41025036274) showed 1,256 unique nonzero GUIDs, 1,252 matching exported `.meta`, 4 unmatched, **no duplicate .meta GUIDs**. Those four are:

- `0000000deadbeef15deadf00d0000000`: **393,450 occurrences** — AssetRipper placeholder sentinel for unresolved **non-script** objects.
- `0000000000000000e000000000000000`: **665 occurrences**, Unity editor's `unity default resources` built-in GUID.
- `0000000000000000f000000000000000`: **25 occurrences**, `unity_builtin_extra` built-in GUID.
- `1c09af679308f504fb0d83c7e727df29`: **1 occurrence**, detected in `54#Landmark_VarunaPoint#.unity`; requires investigation, cannot classify from filename alone.

**None of the 393,450 deadbeef placeholder instances are serialized `m_Script` fields**. Highest property groups of deadbeef:
- `m_Mesh` **198,114**
- list/sequence element **191,091** (parent list not resolved by this shallow parser; do not label these meshes/materials without further evidence)
- `m_SpeedTreeWindAsset` **2,572**
- `m_Controller` **1,189**
- `m_Avatar` **155**
- `sprite` **120**

Other categories had much smaller counts.

**Interpretation:** all game script identities in the exported scenes are repaired, but **mesh and other non-script Unity references are not**. Counting 1,252/1,256 unique GUIDs as 'asset completeness 99%' would be misleading because the one deadbeef placeholder stands for many independent unresolved assets. Full fidelity requires restoring appropriate resource dependencies, validating Unity engine built-ins/primitive meshes, and possibly fixing exporter PPtr handling.

This run did not use Git LFS and did not publish game content. Script analysis source: `scripts/audit_guid_ref_fields.py`.

## Jobs 19–20: reduce missing mesh placeholders and identify original sources

- [All ordinary Git assets export, successful](https://github.com/alwansan/raf/actions/runs/41025868800): 114 files staged, 17 LFS pointers deliberately skipped. All 40 scenes and 64,642/64,642 script links retained. Total `deadbeef` references reduced **393,450 → 199,156** (49.4% reduction); `m_Mesh` references **198,114 → 94,152** (52.5% reduction). This is structural serialized reference reduction, not confirmed Editor import or gameplay.
- [Original Unity MeshFilter/MeshCollider/SkinnedMeshRenderer source pointer audit, successful](https://github.com/alwansan/raf/actions/runs/41026113254): 40 level files and 3 additional source asset files inspected. Parsed 174,314 MeshFilter, 24,895 MeshCollider, 249 SkinnedMeshRenderer components. Mesh source references most frequently pointed to `resources.assets` (85,525 uses), `sharedassets30.assets` (42,137), `sharedassets34.assets` (19,892), and `sharedassets0.assets` (5,423). Counts are component pointer uses, not distinct missing models. `resources.assets` and `sharedassets0.assets` are LFS objects; others have `.assets` present but may lack LFS `.resS` streams.
- Next gated test: [manual-only selected LFS resources/mesh evaluation](https://github.com/alwansan/raf/actions/workflows/raft-opt-in-lfs-mesh-probe.yml) and the full [mesh evidence report](MESH_RECOVERY_FINDINGS.md). Git LFS quota/billing cannot be validated by this CI code, so no LFS auto-download.

## Jobs 21–23: targeted LFS recovery eliminates all known exported scene GUID placeholders

- [resources.assets alone](https://github.com/alwansan/raf/actions/runs/41027328691): downloaded precisely 111,533,516 bytes, checksum verified; unresolved placeholders 199,156→**37,111** and m_Mesh 94,152→**8,631**.
- [resources.assets + sharedassets0.assets](https://github.com/alwansan/raf/actions/runs/41028211970): downloaded precisely 227,511,628 bytes combined (not incrementally cached); unresolved placeholders →**6,697** and mesh →**3,233**. All remaining exported placeholders concentrated in one Utopia scene.
- [all three, plus sharedassets36.assets](https://github.com/alwansan/raf/actions/runs/41028697081): download 337,660,952 bytes total, all three checked by LFS pointer file size/SHA256. **Zero** remaining `deadbeef` GUID references and **zero** `m_Mesh` deadbeef in **40** exported Unity scenes; **64,642/64,642** script links matched. Export counts: 8,389 assets, 888 prefabs, 1,536 materials, 679 animation clips, 179 controllers, 140 shaders.
- Partial UI/geometry resource streams `.resS` remain excluded, potentially containing irreplaceable texture/vertex data. Zero placeholders is a structural export result; Unity Editor import, shaders, visuals, C# runtime and Android APK are **not tested**.
- The current working branch also has [six tested overlay unit tests](https://github.com/alwansan/raf/actions/runs/41024504209) and code overlay method for injecting ILSpy's actual source in `.cs` files without modifying GUID metadata.
- [net8 diagnostic C# compilation](https://github.com/alwansan/raf/actions/runs/41028495873): after *diagnostic-only* `SYSLIB0011` suppression, the ILSpy `Assembly-CSharp` source compiles with game Managed refs into a **3,578,880-byte** DLL, exit code 0. This is not a Unity Editor binary.
- [netstandard2.1 diagnostic](https://github.com/alwansan/raf/actions/runs/41028896726): DID NOT compile (many type/reference errors such as CS0518, CS0731, CS1069). Different .NET compatibility surface and C# SDK defaults mean this does not prove Unity 2021 Editor build failure. Need proper Unity scripting assemblies and assemblies/profile configuration for definitive compile result.

## Jobs 24–28: integrated Unity project candidate, new Android platform code, Editor licensing gate

- [Run 41029351916 — integrated project passed structural checks](https://github.com/alwansan/raf/actions/runs/41029351916): AssetRipperCLI three selected LFS asset containers and original MonoScript metadata; ILSpy complete CSharp gameplay source merged by strict name+namespace. 40 scenes, 3,811 CSharp files and metadata companions, 64,642/64,642 script GUID matches, zero unresolved deadbeef GUID references, 1,568 safe gameplay overlays. Unity Editor import/compilation **not done**. Candidate kept in runner TEMP, never published.
- [Run 41029669318 — new Raft Android platform adapter passed](https://github.com/alwansan/raf/actions/runs/41029669318): `RaftAndroid.Platform` compiles for netstandard2.1 and has **7/7 passing** .NET smoke tests. Original code handles stable local identity and isolated save directories for solo mode, with no Steam/network dependency. Not connected yet to original game.
- [Run 41030164120 — Unity Editor Android build gate deferred](https://github.com/alwansan/raf/actions/runs/41030164120): GitHub preflight job PASS but Unity job SKIPPED because required `UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD` secrets were absent. No Unity Editor invocation or APK build. Do not describe run as actual Unity import.
- [Run 41029055235 — Mesh stream source sample](https://github.com/alwansan/raf/actions/runs/41029055235): 724 Mesh samples, 278 require external `.resS`, 17 MB of referenced stream segments in the sample. Missing stream content could damage geometry even with valid script/resource GUIDs.
- [Run 41028495873 — .NET 8 diagnostic compile PASS](https://github.com/alwansan/raf/actions/runs/41028495873) produced 3,578,880-byte DLL (legacy SYSLIB0011 obsolete diagnostics suppressed in test). [netstandard2.1 compile attempt FAILED](https://github.com/alwansan/raf/actions/runs/41028896726). [net472 compile attempt FAILED](https://github.com/alwansan/raf/actions/runs/41030084316) with 28 CS1069, 6 CS0308 and 4 CS0103 errors. These are compatibility diagnostics, not the Unity Editor build gate.

**Latest approved LFS scope** is restored to `config/mesh-lfs-scope.txt = NO` to avoid repeated transfers after successful three-file experiment. GitHub LFS may charge for downloads; don't re-fetch casually. No original game APK distributed.
