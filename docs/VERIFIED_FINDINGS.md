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
