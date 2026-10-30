# Unity Editor C# reconstruction and dependency diagnosis

**Target:** Raft Windows Unity Mono 2021.3.45f2 → native Android ARM64 singleplayer.
**Branch:** `feature/android-native-port`; do not merge into `main` or `zip`.

## Evidence through October 30, 2026

1. [Run 41057568426](https://github.com/alwansan/raf/actions/runs/41057568426) verified ILSpy `-lv CSharp9_0` produces 2,394 C# files and removes C#12 primary constructors from `Spray.Particle` / `Voxelize.Int3`.
2. [Run 41057547888](https://github.com/alwansan/raf/actions/runs/41057547888) successfully launched Unity Editor with GameCI and working Unity entitlement but exposed **2,220** C# compiler diagnostics after syntax fixes. Error codes (occurrences, not unique affected types): CS0246=1,657, CS0115=376, CS0538=76, CS1721=21, CS0308=18, CS0616=17, CS0208=17, CS0234=16, plus smaller groups.
3. Most frequently missing original-game helper types included `Message_NetworkBehaviour` (126 occurrences), `IRaycastable` (95), `Interval_Float` (54), `SceneEvent` (51), `RGDType` (41), `SerializableBehaviour` (34), `EntityType` (34), `ChunkPointType` (31) and `QuestType` (29). This suggests missing **non-MonoScript class/enum/interface sources**, rather than only external managed package references.
4. [Run 41058797120](https://github.com/alwansan/raf/actions/runs/41058797120) verified `scripts/supplement_ilspy_gameplay.py`: appended **614 unique absent C# helper type files** from original ILSpy decompilation, without overwriting any existing `.cs` or `.cs.meta`. Five synthetic safety tests passed, and script GUID reference linkage retained 13,969/13,969 in the sample. [Full Editor run 41058926410](https://github.com/alwansan/raf/actions/runs/41058926410) adds these types and must be evaluated before claiming the missing type errors are fixed.
5. Confirmed external original Managed dependencies in [audit 41058831995](https://github.com/alwansan/raf/actions/runs/41058831995): `FMODUnity.dll` exports FMOD and FMOD.Studio types, `PlayFab.dll` exports PlayFab ClientModels/Json/EventsModels. `PlayFab_o.dll` overlaps `PlayFab.dll`; **do not import both**. Other original assemblies include Unity.Netcode.Runtime, Unity.Networking.Transport and UnityEngine.UI.
6. [Run 41059197129](https://github.com/alwansan/raf/actions/runs/41059197129) verified `scripts/stage_raft_managed_dlls.py` stages a conservative **9 DLL allowlist**, 3,081,216 bytes, with five synthetic safety tests. It explicitly excludes core `UnityEngine.CoreModule.dll`, `mscorlib.dll`, `System.*` and `Assembly-CSharp.dll`. **This does not establish editor or Android compatibility.** Any managed plugin load conflicts must be audited.

## Important integration constraints

- Preserve script GUIDs and keep source export/ILSpy code in disposable Unity project directories only; never commit or upload game decompilation.
- Distinguish **C# type compilation**, Unity Editor import, and actual Android IL2CPP/runtime ability; they are different milestones.
- Importing original Windows-targeted FMOD/Steam/PlayFab managed libraries may fix compilation but still leave native Android binaries and/or Steam hooks missing. Treat as a diagnostic bridge, not the final game networking or audio implementation.
- Do not import `PlayFab.dll` and `PlayFab_o.dll` together; their definitions overlap.
- Unity Editor license is already configured in the user's GitHub **Environment `UNITY_LICENSE`**. Preflight and Editor launch authenticated in earlier runs.
- Avoid repeated unbounded Git LFS usage: the currently required three game resource files total 337,660,952 bytes per uncached full run.
- Never infer a functional game from nonzero numbers of recovered scripts, scenes, and DLLs. Test actual Unity Editor compilation and Android gameplay.

## October 30 follow-up: Unity C# CS1704 (run 41059708964)

- [Unity run 41059708964](https://github.com/alwansan/raf/actions/runs/41059708964) completed unsuccessfully after license preflight and project reconstruction succeeded. The compiler reported `CS1704`: duplicate `UnityEngine.UI` assembly. Unity itself referenced `Library/Bee/.../UnityEngine.UI.ref.dll` while the temporary project separately staged `Assets/Plugins/RaftManagedReferences/UnityEngine.UI.dll`.
- Removed the original Windows `UnityEngine.UI.dll` from the staging allowlist. Unity's Editor-provided UGUI module is retained; the gameplay project's original UI C# source was not deleted. The list is now eight managed dependencies. Added a regression assertion and updated the smoke workflow to expect eight DLLs.
- The gated Android Unity workflow now listens for managed staging script/test changes so the next compiler evaluation is automatic: [new compile run 41062047785](https://github.com/alwansan/raf/actions/runs/41062047785).
- **This is a targeted compiler-collision fix, not evidence of Android compatibility or APK creation.** Inspect the next Unity Editor errors separately; never claim an Android build is functional before test.
