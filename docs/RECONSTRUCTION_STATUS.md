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

## Key milestone: ZERO exported scene GUID placeholders with 3 LFS files

See [successful CI](https://github.com/alwansan/raf/actions/runs/41028697081). A targeted three-LFS-object export of `resources.assets`, `sharedassets0.assets`, and `sharedassets36.assets` restored all known serialized `deadbeef` references in the **40** exported Unity scenes from **393,450 to 0**, including mesh references **198,114 to 0**. Script GUID linkage remains **64,642/64,642**, and the export includes 8,389 assets, 888 prefabs, 1,536 materials, 679 animations and 179 controllers. This is a **serialized project reconstruction success**, not visual fidelity, Unity Editor compile, standalone runtime, or Android APK proof. The LFS `.resS` streams and platform plugin replacements remain unverified.

Further CSharp recovery: [net8 diagnostic compile succeeded](https://github.com/alwansan/raf/actions/runs/41028495873) (3,578,880-byte output, legacy BinaryFormatter obsolete diagnostic suppressed only for this test); [netstandard2.1 diagnostic failed](https://github.com/alwansan/raf/actions/runs/41028896726) with framework reference mismatches. Editor compilation for Unity 2021.3.45f2 is still the definitive target.

## Integrated project candidate and original Android platform work

- [Full integrated reconstruction job — PASSED](https://github.com/alwansan/raf/actions/runs/41029351916): three selected LFS asset containers + regular Git serialized data + Unity `globalgamemanagers.assets` registry + all 40 original levels + full Mono DLL inventory + ILSpy decompiled `Assembly-CSharp.dll` overlay. Reported **40** Unity scene files, **3,811** script `.cs` files and corresponding script `.meta`, **64,642/64,642** scene script GUID matches, **0 deadbeef** placeholders, **1,568** real gameplay C# overlays, **85** namespace mismatches safely excluded. Candidate remained on private temporary GitHub runner, not committed/published.
- The built project remains **UNTESTED in Unity Editor**; missing large `.resS` assets, plugin/platform compatibility and original serialization semantics may break import or runtime.
- [Standalone Android local platform code — compiled and smoke tested](https://github.com/alwansan/raf/actions/runs/41029669318). Files in `android-port/Runtime/Platform` introduce `LocalProfileStore`, `LocalSavePaths`, `OfflineSession` and an optional compile-guarded `UnityOfflinePlatformBootstrap`. Seven test cases passed with zero failures under .NET 8 while the library itself compiles against netstandard2.1. This is **new original code**, not patched into the original game's `SteamManager` or `Raft_Network` yet.
- [Gated real Unity Editor / Android build experiment](https://github.com/alwansan/raf/actions/runs/41030164120) **did not run the Editor**. Preflight confirmed Unity activation credentials are not supplied via repo secrets, so its resource-heavy second job was correctly skipped before downloading LFS or Unity Docker. Unity account/license setup is a real external prerequisite not solvable by reconstructing the project alone.
- [net8 temporary diagnostic compilation](https://github.com/alwansan/raf/actions/runs/41028495873) passed with legacy BinaryFormatter diagnostic suppression only. [net472 compatibility audit](https://github.com/alwansan/raf/actions/runs/41030084316) had 38 code errors: CS1069 type-forwarded `Queue<T>`/`Stack<T>`, CS0308 generics and CS0103 `MathF`; [netstandard2.1 audit](https://github.com/alwansan/raf/actions/runs/41028896726) had extensive framework reference errors. Only actual Unity 2021 Editor compilation can settle original project compatibility.
- [Original Mesh m_StreamData sample](https://github.com/alwansan/raf/actions/runs/41029055235): inspected 724 Mesh instances from available regular Git files, **278** referred to external `.resS` streams, proving that eliminating GUID placeholders does not restore all geometry streams. The ~6.47 GiB LFS collection must be prioritized by actual import/visual failures rather than blindly fetched.

## October 30: first genuine GameCI Editor pipeline reached, then versioning blocker fixed

User supplied a GitHub **Environment** named `UNITY_LICENSE` with three environment secrets (`UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD`). They were **not** repository-level secrets. We fixed `.github/workflows/raft-unity-editor-android-import.yml` to set `environment: UNITY_LICENSE` on **both** the preflight and builder jobs, preserving secret values in GitHub's encrypted environment and never logging them.

[Run 41050543549](https://github.com/alwansan/raf/actions/runs/41050543549): secret presence gate passed, all three selected Git LFS assets downloaded and integrity-checked, the integrated Unity candidate exported/validated (40 scenes, 3,811 CSharp files/meta, 64,642/64,642 script GUID links, 1,568 real CSharp source overlays, 0 deadbeef GUIDs), and 2.5 GiB of generated candidate content was staged. **Unity Editor was not launched**, because GameCI's default `Semantic` versioning rejected the deliberately uncommitted generated candidate and Python caches: `Branch is dirty. Refusing to base semantic version on uncommitted changes`.

Fix committed: `game-ci/unity-builder@v4` inputs now specify `versioning: None` and `androidVersionCode: 1`. The `None` strategy is [officially supported by GameCI](https://game.ci/docs/github/builder/), and avoids Git-based semantic version calculation of ephemeral generated files. We did **not** relax permissions or blindly set `allowDirtyBuild` in the source repository.

[New run 41051377781](https://github.com/alwansan/raf/actions/runs/41051377781) passed identity secret preflight, all 14 pre-Editor project preparation steps, and reached the `Unity Editor 2021.3.45f2 Android import and compile` job step. Until that step completes, **do not assert license activation has succeeded, an Editor import passed, or an APK exists**.

The owner need not move or rename the three Environment secrets: the real problem was the missing `environment:` binding in our CI workflow.

## First actual Unity 2021.3.45f2 Editor import — reached compiler (2026-10-30)

[Run 41051377781](https://github.com/alwansan/raf/actions/runs/41051377781) **successfully launched the real Unity Editor inside GameCI**, authenticated its Unity entitlement, began AssetDatabase project import and reached the CSharp compiler. The previous Git dirty versioning issue was fixed with GameCI's documented `versioning: None` option. Unity Editor aborted compilation with **395 compiler diagnostics** originating from exactly **79** invalid generated script class names in AssetRipper's third-party assembly stubs (`Assets/Scripts/Unity.Collections`, `Unity.Mathematics`, `Unity.InputSystem`, Unity purchasing). Their filenames contain dots after the type name, and the generated declarations incorrectly use them as CSharp identifier characters: e.g. `public class HeapString.gen : MonoBehaviour`, `public class bool2.gen : MonoBehaviour`. **This was not a Unity activation failure**; the 79 bad class declarations are generated templates, not 79 broken gameplay implementations. The repeated diagnostic codes were CS1514, CS1513, CS1022, CS8803 and CS1002 (79 occurrences each). No APK produced.

Created `scripts/repair_assetripper_stub_classnames.py` and `tests/test_repair_assetripper_stubs.py`: repairs **only** invalid generated MonoBehaviour placeholder class+file names, gives them deterministic collision-resistant replacement identifiers, and **preserves each existing `.cs.meta` GUID bytes unchanged**. It refuses ambiguous or non-template source files and never edits ILSpy real game source. The small no-LFS [probe 41053145166](https://github.com/alwansan/raf/actions/runs/41053145166) repaired **all 79/79 candidate stubs**, with **6/6 synthetic tests passing** and no remaining invalid script names.

[Run 41053260808](https://github.com/alwansan/raf/actions/runs/41053260808) integrates this repair step **after ILSpy source overlays** and **before Unity import**. This is another actual Editor import/build attempt; inspect its result before claiming Editor compilation succeeded.

## 2026-10-30 Unity Editor compiler progress: 395 errors reduced to two; targeted next test

[Unity full import run 41053260808](https://github.com/alwansan/raf/actions/runs/41053260808) confirmed **all 79 malformed AssetRipper-generated class-name errors were removed**, reducing Unity's reported C# compilation errors to just **two CS0101** duplicate type declarations in `Unity.Timeline`: `UnityEngine.Timeline.AnimationPlayableAsset` and `UnityEngine.Timeline.AnimationTrack`.

The [tiny no-LFS diagnostic run 41054850504](https://github.com/alwansan/raf/actions/runs/41054850504) showed these two source files were **2,734** and **2,726** bytes respectively, each an AssetRipper-generated placeholder declaring a bogus `MonoBehaviour` rather than the game's original Timeline runtime implementation. The separate [static declaration scan 41054587098](https://github.com/alwansan/raf/actions/runs/41054587098) saw one local declaration for each in the limited export, so an external compiled package or compilation input may be part of the collision; the precise root cause is **not yet proven**.

Extended `scripts/repair_assetripper_stub_classnames.py` with an explicit **opt-in diagnostic-only** `--repair-timeline` flag that only disambiguates these two known template paths. It keeps `.cs.meta` file content byte-for-byte, including their serialized GUIDs. **Important:** renaming generated placeholder MonoBehaviour types is not a correct functional replacement for Unity Timeline TrackAsset / PlayableAsset types; it is strictly a safe compilation unblocker. Actual timeline clip serialization, playback and animation functionality still need validation/recovery. The no-LFS [test run 41055063167](https://github.com/alwansan/raf/actions/runs/41055063167) passed this test after fixture correction and repaired **81 generated placeholders** (79 malformed name templates plus these 2 collisions). (Check more recent run logs for final outcomes; do not assume an APK.)

[Real Editor build run 41055289637](https://github.com/alwansan/raf/actions/runs/41055289637) includes the Timeline collision repair and is undergoing Unity 2021 Android import/compilation. Real editor result pending at time of this record.

## Unity 2021 compile iteration (October 30, after Timeline collision fix)

[Run 41055289637](https://github.com/alwansan/raf/actions/runs/41055289637) successfully eliminated the last **two Unity.Timeline CS0101** errors by disambiguating two generated placeholders in the disposable Unity project with the GUID-preserving `--repair-timeline` option. The Editor then moved to the project's main `Assembly-CSharp` and reported **636** syntax diagnostics (313× CS1514, 312× CS1513, seven CS0106 and a few others), concentrated in decompiled CSharp source files with **C#10 file-scoped `namespace Foo;` declarations**, which Unity 2021's CSharp compiler does not accept. This demonstrates progress into original game-code compilation rather than a license or asset linkage failure.

[No-LFS ILSpy overlay CI 41056215010](https://github.com/alwansan/raf/actions/runs/41056215010) ran `scripts/normalize_csharp_namespaces.py` **after** ILSpy code overlay and converted **311** files; the remaining **3,499** exported CSharp sources already passed the namespace format check, and a repeat check showed zero remaining file-scoped namespace cases. Tests passed and generated `.cs.meta` script identities were not touched.

[Next full Android Unity Editor run 41056359011](https://github.com/alwansan/raf/actions/runs/41056359011) includes all three sequential fixes: recovered source overlay, CSharp namespace compatibility normalization, and two Timeline placeholder disambiguations alongside 79 malformed third-party stub names. This is still an **import/compiler diagnostic**. An APK does not exist unless full Unity Android build step passes; even then, runtime/visual testing and legal distribution requirements remain separate.

## ILSpy 11 CSharp9 output now pinned at the decompiler — 2026-10-30

[Unity 2021 compile run 41056359011](https://github.com/alwansan/raf/actions/runs/41056359011): after post-ILSpy file-scoped namespace rewriting, compiler errors fell **636 → 16** and were confined to `Assembly-CSharp/UltimateWater/Spray.cs` and `Assembly-CSharp/Voxelize.cs`. The 16 remaining errors came from **C#12 primary-constructor syntax** in two nested structs (`Particle(...)`, `Int3(...)`), introduced by ILSpy 11's default `Latest` language output. These are decompiler-format compatibility problems, not proof of corrupt original Mono IL.

The upstream official ILSpy CLI provides [`-lv|--languageversion CSharp9_0`](https://github.com/icsharpcode/ILSpy/blob/master/ICSharpCode.ILSpyCmd/README.md). Instead of patching emitted C#12 code manually, the [no-LFS CI run 41057399641](https://github.com/alwansan/raf/actions/runs/41057399641) pinned ILSpy to **CSharp9_0** during full project decompilation, retained **1,568** namespace- and name-matched source overlays, and showed **zero** later namespace-syntax conversions were necessary across 3,810 CSharp files. The output's two suspect struct declarations no longer used C#12 primary constructor syntax.

[Next real Editor Android build run 41057547888](https://github.com/alwansan/raf/actions/runs/41057547888) uses the CSharp9_0 decompiler option and previous stub/GUID repairs. Its actual Editor and build outcome must be checked in GitHub Actions; **no APK is considered available until a successful build and verified output are observed**.
