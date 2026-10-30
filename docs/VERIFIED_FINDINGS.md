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
