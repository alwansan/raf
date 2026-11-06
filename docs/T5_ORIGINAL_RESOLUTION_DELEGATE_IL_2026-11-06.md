# T5 DISPLAY-003 — authentic compiled Settings delegate target reachability

Session `20261106T1104Z-T5-chat-resolution-delegate-6a2f` • origin `chat` • only writable branch `feature/android-native-port`.

## Evidence and exact input

Source-only [CI 42208532103](https://github.com/alwansan/raf/actions/runs/42208532103) **SUCCESS** at immutable source `689d45d290b9ef3efd0e439b70dc60903495a058`, job `127861131183`. It compiled the independent .NET 9 / Mono.Cecil 0.11.5 analyzer and passed **9/9 Python negative/positive tests** and **5/5 synthetic Cecil IL topology assertions**. It privately checked immutable original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, actual `Raft_Data/Managed/Assembly-CSharp.dll`, **3,211,776 bytes** and SHA-256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Original DLL, IL, private field/method names and raw source were never uploaded or emitted.

The previous authenticated [T5 original IL site census 42204488410](https://github.com/alwansan/raf/actions/runs/42204488410) found two `ldftn/ldvirtftn` sites inside original `GraphicsSettingsBox`. The new probe resolves actual method definitions, not just reference instruction count, and traverses only **direct, statically resolvable same-type call/callvirt edges**, bounded to 256 methods with cycle protection and zero unresolved local call sites required. It never executes game callbacks.

## Verified original facts

| Exact bounded original IL category | Count |
|---|---:|
| GraphicsSettingsBox compiled methods | 42 |
| Delegate instruction sites (same type) | 2 |
| Validly resolved delegate instruction sites | 2 |
| **Unique method targets behind both references** | **1** |
| Delegate targets containing Int32 parameters | 0 |
| Original option population IL call sites / containing methods | 1 / 1 |
| Option-population methods containing same-type delegate site | 0 |
| Option-population methods reaching Apply/Screen.SetResolution by same-type direct calls | 0 / 0 |
| Delegate targets reaching Apply/Screen.SetResolution by same-type direct calls | 0 / 0 |
| Delegate target direct PlayerPrefs writes | 0 |
| Unique same-type resolved direct-call edges | 22 |
| Unresolved same-type direct calls / delegate sites | 0 / 0 |

**Discriminating result:** the two previously noticed delegate references are **not two distinct candidate target methods**; they resolve to one target with no Int32 parameter and no bounded statically resolvable path to either the original `ApplyCurrentResolutionAndFullscreenMode` or `Screen.SetResolution` entry methods. The distinct source method that populates options also has no same-type delegate instruction or direct same-type call path to those methods. This narrows the **direct same-type IL pathway**, but does **not** establish where the original UI event actually binds, whether a serialized UnityEvent or other class invokes a handler, what a custom Settings persistence layer saves, or whether Android has a lower rendered resolution option.

A **zero** in this census means *no observed call edge in the exact scoped definition*, never absence of an original feature across all assemblies/assets, native Unity code, reflection, callbacks or serialized UI. Passing this CI cannot be interpreted as working UI, corrected aspect/FPS or device proof.

## Source changes and continued bounded work

The new isolated artifacts are `android-port/Experiments/T5/ResolutionDelegateProbe/Program.cs` / `ResolutionDelegateProbe.csproj`, `scripts/t5_validate_resolution_delegate_probe.py`, `tests/test_t5_validate_resolution_delegate_probe.py` and `.github/workflows/raft-t5-original-resolution-delegates.yml`. The safe report gate rejects fake original bytes, missing/duplicate delegate targets, unresolved local IL, inflated subset counts, duplicate/unknown JSON fields, invalid Unicode/oversized/symlink reports and any claimed Android binding or device success. No original source, shaders, .meta, game assets, UI, Settings, touch, world/save, signed APK/OBB/XAPK, release or T1–T4 paths were changed. No expensive Unity game build was initiated.

The owner-confirmed native Raft world/save/re-enter test remains bound to artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source `e9c358e` only; WATER-001, RENDER-002, and full device acceptance remain open, game **NOT_READY 0/3**.

**Next experiment:** inspect the original SHA-pinned `GraphicsSettingsBox` three same-type `ApplyCurrentResolutionAndFullscreenMode` callers and typed Unity UI serialized onValueChanged bindings in the exact owner Settings scene/prefab, correlating only confirmed method metadata with real UI owner script identity. Require explicit proof of selection→handler→physical screen or render-buffer change and save/reload before implementing Android-only resolution settings. Maintain strict distinction among screen mode, app surface, render scale, refresh Hz, frame metrics, and scene/layout scaling.
