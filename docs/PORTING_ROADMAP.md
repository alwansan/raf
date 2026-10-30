# Raft → Android native port: evidence-led roadmap

> Status: discovery / prototype only. This is **not** a working Android port.
> Source baseline: `zip`. Development: `feature/android-native-port`.
> Never merge into `main` automatically. No publicly distributed proprietary game builds or assets without permission.

## 0. Evidence / verified repository inspection (2026-10-30)

- Repository: `alwansan/raf`, current source branch `zip`.
- 368 Git blobs in the recursive tree; regular Git blob bytes total 840,349,675 (~0.783 GiB).
- 18 actual Git LFS pointer files; their declared original total is 6,948,949,688 bytes (~6.472 GiB).
- **Approx. overall uncompressed payload** 7.255 GiB, plus Git object/history and build artifacts. LFS declaration is NOT proof that payloads are retrievable.
- `Raft/Raft_Data/Managed/Assembly-CSharp.dll` exists (3,211,776 bytes): Mono managed-code hypothesis.
- 40 `Raft/Raft_Data/level0..level39` serialized Unity scene files.
- 42 `*.assets`, 48 `*.resS`, audio banks, native Windows libraries.
- `Raft/Raft_Data/globalgamemanagers`, `boot.config`, and `app.info` exist.
- No `Assets/`, `ProjectSettings/`, or `Packages/` Unity **editor project** at repository root.
- Native dependencies seen: Steamworks.NET, Steam API (Windows), Microsoft Party/Xbox libraries (Windows), FMOD Studio, PlayFab, Unity Purchasing, Odin, MicroSplat, NewtonSoft JSON, custom DLLs. Their precise usages are unverified.
- Modified/third-party binaries in the distribution: OnlineFix64.dll, SteamOverlay64.dll, StubDRM64.dll. Treat them as **untrusted**; never run them in CI or transfer them to Android.
- Exact Unity version **2021.3.45f2** verified via GitHub Actions; managed metadata: 3032 types, 19512 methods, 16920 fields, 155 P/Invoke declarations. Binary completeness, source-code recovery fidelity, material/shader fidelity, LFS availability, and Unity build licensing remain **unverified**.

### Critical rights/billing checkpoint

The source repository is PUBLIC and contains commercial game resources. A personal port does not authorize publishing or distributing the source game's files or a game APK. Keep proprietary assets private / obtain appropriate permission before sharing builds. Merely changing visibility later does not retract previous downloads. Git LFS downloads consume the owner's bandwidth allowance and may be billable. Do not turn on LFS downloads in general-purpose CI jobs.

## 1. Acceptance criteria / scope

**Goal:** arm64-v8a, genuine Unity-compiled native Android APK, functional offline Raft single-player, on-device storage and touch controls, with a future independent host/client multiplayer implementation. Device for physical verification: POCO F5 Pro.

**Non-goal:** preserving original Steam matchmaking, authentication, Steam networking or Windows binaries.

Do not claim a full port until a reproducible APK actually runs on the test phone with working world loading, item interactions, persistence and verified acceptable frame times.

## 2. Stage-by-stage implementation (gated)

### G0 — Proof of inventory and data integrity (CURRENT)

1. Run `scripts/inspect_raft.py` in Actions using `actions/checkout` with `lfs:false`.
2. Read metadata, disk availability, LFS manifest and Unity version candidate from `globalgamemanagers`. Do **not** execute downloaded game DLL/EXE files.
3. Verify selected LFS objects exist using a narrow, cost-aware request **only after** disk and billing checks.
4. Record confirmed Unity editor engine version, Mono / IL2CPP status, file hashes, plugin manifest and original archive provenance.
5. Evaluate whether original clean retail game distribution is available: skip and quarantine OnlineFix-like binaries.

**Current result:** inventory JSON and exact engine version verified; Mono assembly metadata verified. LFS object retrieval and Unity asset round-trip still pending. If those fail: pause full asset recovery.

### G1 — Managed-code and content dependency map

1. Download only `Assembly-CSharp.dll` and minimal managed references for analysis; do not run game binaries.
2. Analyze with ILSpy/ILSpyCmd or dnlib/dnfile in a sandbox: assembly references, type names, entry points, namespaces, API calls, MonoBehaviour/ScriptableObject links.
3. Build dependency graph by feature: main menu, raft movement, ocean, procedural islands, player, input, inventory/crafting, AI, world save/load, Steam/network, audio, graphics.
4. Locate every Windows `DllImport` / Steamworks / Party / FMOD / PlayFab dependency; classify remove, wrap, platform substitute, or investigate.
5. Sample Unity scene / resources in AssetRipper first; validate GUID, Material, Mesh, Animator, audio / texture exports.

**Pass:** feature-level compatibility matrix, source recovery report and test export. Note: decompilation loses original project metadata and can require substantial repair.

### G2 — Recover a reproducibly compilable Unity EDITOR project

1. Determine exact engine version first. No arbitrary upgrade before initial import test.
2. Reconstruct `Assets/`, `ProjectSettings/`, `Packages/` using supported AssetRipper export and explicit references.
3. Separate generated/private assets from freely redistributable code.
4. Address missing `*.meta` GUIDs, script class/file alignment, serialization names, broken prefabs, missing materials, shader compilation, cross-scene references, missing packages and assemblies.
5. Create clean adapter layers for platform services and offline mode; avoid intrusive patches until import/compile errors are inventoried.
6. Validate a minimal test scene in Unity Editor (headless compile/import as possible).

**Pass:** Unity Editor imports and compiles the reconstructed project with a minimal scene; errors and unresolved components inventoried.

### G3 — Android vertical slice

1. Configure `arm64-v8a`, IL2CPP (if supported), Android input permissions, storage API, quality settings and package ID.
2. Replace Windows-only native plugins. Do not ship `steam_api64.dll`, `OnlineFix64.dll`, `UnityPlayer.dll`, Windows FMOD DLL, or Windows Party DLLs.
3. Replace Steam auth/session/friends and original network calls with an offline/local service interface.
4. Create Android-safe FMOD integration or fallback audio pathway subject to platform/plugin licensing.
5. Implement safe-area aware UI, touch movement/aim/interact, configurable sensitivity and controller support.
6. Optimize shaders (mobile URP/Built-in compatibility as determined), ocean reflection/refraction, CPU physics, terrain/foliage, instancing, LOD, texture ASTC/ETC2 and memory usage.
7. First playable slice: ocean + raft + player movement + interaction + save/reload; expand only after mobile tests pass.

**Pass:** Android arm64 APK starts, world renders and a complete offline game loop survives a device restart.

### G4 — Restore gameplay by subsystem

Suggested order: main menu/world create → raft water physics → player movement/swim → hook/loot → inventory and crafting → building → food/hunger/thirst → AI/shark → islands → story locations → quests/bosses → full save/load → polish.

For each subsystem: compile, integration test, device logs, CPU/GPU memory profiling and regression checks. Maintain a parity checklist against desktop behavior.

### G5 — New mobile multiplayer, not original Steam multiplayer

1. Start with solo/local-host architecture: host is authoritative owner of world simulation and saves.
2. Note the verified assembly reference to `Unity.Netcode.Runtime` plus many `AI_NetworkBehaviour_*` classes. First evaluate reuse of existing Unity Netcode game object synchronization by replacing its Windows/Steam/Party transport layer. Compare with Mirror (KCP/UDP) or LiteNetLib **only after** inspecting actual network call sites.
3. Phase A: LAN same Wi-Fi + manual IP/port join; optionally Android NSD/mDNS discovery.
4. Phase B: robust spawn/despawn, raft physics snapshots, tick/time sync, prediction/interpolation, inventory RPC with validation, persistence and graceful disconnect/reconnect.
5. Phase C: Internet over NAT only after LAN works; evaluate relay/ICE/signaling and operating costs. No guarantee universal direct P2P.
6. Never assume a mobile hotspot and Wi-Fi LAN behave identically on every phone.
7. Phone host needs thermal, CPU, background lifecycle and battery tests.

**Pass:** host + 1 client can collect resources, build, save, reconnect without item duplication; then expand concurrency.

### G6 — Performance and release gates

- Collect Unity Profiler traces where possible, Android `logcat`, FPS/frame time p95, RAM (PSS), thermal state, battery/power, scene load times, ANR and crashes.
- Use measured quality presets (low/medium/high), adaptive render scale and capped target frame rate. Do not promise 60 fps before real-device data.
- Build signed test APK in private CI; avoid distributing unlicensed third-party assets.
- APK is a build artifact only **after** Unity project compiles and includes valid Android assets.

## 3. Automation / GitHub Actions

1. **Already implemented** `.github/workflows/raft-inventory.yml`: safe no-LFS audit, disk checks, report artifact.
2. **Later** `static-managed-analysis.yml`: minimal managed DLL analysis (no execution).
3. **Later** `asset-probe.yml`: strict opt-in LFS path whitelist, max downloadable bytes, disk-budget check, no automatic full LFS retrieval.
4. **Later** `unity-import-validation.yml`: Unity Editor/import compatibility; requires version + license.
5. **Later** `android-build.yml`: GameCI `unity-builder`, Android target, user-provided valid Unity activation, optional smoke tests; upload APK artifact.
6. **Later** `android-debug-report.yml`: sanitize shared device logs, redact personal tokens, path information and account identifiers.

No job should execute `Raft.exe` or third-party patched DLLs. Do not cache or upload raw proprietary assets as public artifacts.

## 4. Tool chain (official projects; versions to pin after exact Unity version)

| Purpose | Tool | Install / download entry point | Status |
|---|---|---|---|
| Unity serialized asset analysis | AssetRipper official 2.0.0 | https://github.com/AssetRipper/AssetRipper/releases/download/2.0.0/AssetRipper_linux_x64.tar.xz | Download, checksum and --help **verified** in GitHub Actions; GUI/headless-web, not batch CLI |
| Mono metadata / C# decompilation | dnfile 0.18.0 / ILSpy | https://pypi.org/project/dnfile/ / https://github.com/icsharpcode/ILSpy/releases | dnfile metadata parser installed and tested; ILSpy decompiler not installed |
| .NET for ILSpy tooling | .NET SDK | https://dotnet.microsoft.com/download | Not installed |
| Editor rebuild / Android export | Unity Editor + Android module | https://unity.com/download | Not installed; determine exact version first |
| CI Unity Android build | GameCI unity-builder | https://game.ci/docs/github/builder/ | Planned, needs editor project and valid license |
| Future network | Mirror | https://github.com/MirrorNetworking/Mirror | Candidate, NOT selected yet |

Third-party AssetRipperCLI v1.0.1 (https://github.com/nowl-it/AssetRipperCLI/releases/download/v1.0.1/AssetRipper_linux_x64.zip) was independently downloaded, SHA-256 verified and --help tested in isolated GitHub Actions; includes --cli. Test real asset export before choosing it for main recovery. Avoid unnecessary forks: GitHub Actions can download released upstream tools and cache by pinned versions. Fork only if we demonstrably need to change upstream code or lock a fork-specific patch.

## 5. Space and storage policy

Before ANY download or extraction: inspect `df -h` / free bytes, verify archive size and checksum and reserve significant headroom for extracted Unity project, intermediate exports, Library cache and Android SDK. On GitHub Actions, never enable `lfs:true` blindly; limit downloads and monitor Git LFS usage to avoid unanticipated charges. Always clean temporary files. If download/install fails, identify exact file/version with a direct official download link for optional user upload.

## 6. Work rules and reporting

- Branch: `feature/android-native-port`; `zip` remains untouched, `main` untouched. No merge without explicit user instruction.
- Mark all facts as **verified**, **inferred** or **unverified**. Every completed stage should have checks and linkable logs.
- Never claim a Unity project exists merely because it contains compiled game data.
- Do not claim a successful build without a real APK.
- Primary test phone: POCO F5 Pro; emulator optional.
- Gate large Git LFS usage and third-party downloads by storage and cost checks.
