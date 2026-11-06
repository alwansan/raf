# T5 DISPLAY-003 — exact original compiled Resolution Apply caller inventory

**Session:** `20261106T1130Z-T5-chat-applycallers-c6e1`, `origin=chat`. **Branch:** only `feature/android-native-port`. **Result:** source-verified exact original caller provenance; callback/persistence and Android resolution remain unverified.

## Verified experiment / source boundaries

- [GitHub Actions run 42210936332](https://github.com/alwansan/raf/actions/runs/42210936332), job `127869109940`, **COMPLETED SUCCESS** on exact source `14f8ca279b35a9032267f9e8fb59ac54bbb4feb6`. Raw job evidence: **10/10 source-free Python regressions**, **5/5 compiled C# synthetic Cecil checks**, original managed binary SHA/size authentication, and exact original caller evidence validator all passed.
- The only original input was `Raft/Raft_Data/Managed/Assembly-CSharp.dll` from immutable ZIP2 Git source commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, exact length **3,211,776 bytes**, SHA-256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`; compiled Mono.Cecil 0.11.5, .NET 9, Ubuntu 24.04.
- Original binary, IL bytes, proprietary method/field names, tokens and source code were **never uploaded or copied into public repo**. Safe output contains bounded counts and typed categories only; no stage decompilation or original game modification.
- This checks the **three prior source-confirmed direct `ApplyCurrentResolutionAndFullscreenMode` call sites** by distinct *containing methods*, and separately scans external class methods for direct compiled call instructions to that entry point. This is a static IL census, not a complete runtime callback graph.

## Exact original compiled results

| Direct compiled IL evidence | Result |
|---|---:|
| Original `GraphicsSettingsBox` compiled methods with bodies | 42 |
| `ApplyCurrentResolutionAndFullscreenMode` method definitions | 1 |
| Direct call sites to `ApplyCurrentResolutionAndFullscreenMode` from its own class | **3** |
| **Distinct containing methods for those three call sites** | **3** |
| Direct original `Screen.SetResolution` call sites inside the Apply method | **1** |
| Direct original `ScalableBufferManager.ResizeBuffers` sites inside the Apply method | **0** |
| Call sites directly targeting the Apply method from **other source types** in the original assembly | **0** |
| Original option-population API sites / unique containing methods in GraphicsSettingsBox | **1 / 1** |
| Apply caller methods which directly populate options | **0** |
| Apply caller methods with a direct original `PlayerPrefs` write | **0** |
| Apply caller methods matching recognized Unity lifecycle names | **0** |

**Per-caller metadata (no original private identifiers):**

- Two of the three distinct caller methods have **zero explicit parameters**, **zero direct Dropdown API calls**, and each has exactly one same-class Apply call.
- The third distinct caller method has **one parameter** (not a direct `System.Int32` or `System.Boolean` signature), **8 direct Dropdown API call sites** and **8 dropdown-typed field references**, with one direct Apply call. These are **call sites, not eight separate Dropdown widgets**. It has no observed direct `PlayerPrefs` write, no direct `Screen.get_resolutions`/`get_currentResolution` read, and no direct option-population API site within the bounded original caller definition.
- No direct call to Apply from the other managed types in this exact source assembly was found. A serialized Unity callback, message dispatch, reflection, native code, or a call to other public entrypoints within `GraphicsSettingsBox` could still reach one of these caller methods.

**Discriminating conclusion:** the original Apply entry point is called from **three distinct same-class methods** rather than three sites in one method. One method has substantial Dropdown usage, but its parameter shape is not the expected single `int` or `bool` callback; neither that finding nor any zero direct `PlayerPrefs` count authenticates what user selection is saved or how an Android render-scale change would be implemented. Previously tested same-type delegate targets do not statically reach Apply [CI42208532103](https://github.com/alwansan/raf/actions/runs/42208532103); the candidate callback must still be located using **serialized UI bindings or typed cross-class entrypoints** before code changes.

## Controls, limits, and next independent action

- The new isolated code resides in `android-port/Experiments/T5/ResolutionApplyProbe/`, `scripts/t5_validate_resolution_apply_callers.py`, `tests/test_t5_validate_resolution_apply_callers.py`, `.github/workflows/raft-t5-original-resolution-apply-callers.yml`. The static gate pins original **42 methods, 3 Apply call sites, 1 SetResolution, zero direct ResizeBuffers and 1 option API site**, checks per-caller sites sum to three and detects conflation of 3 sites vs 3 unique methods, rejects source spoofing, malformed counts/fields, duplicate JSON, linked/oversized files and false Android/phone claims.
- This task has **not** changed game runtime source, original scripts, scenes, shaders, materials, `.meta` GUIDs, three diagnostic UI buttons, original Settings, T4 mouse/world, T1–T3 water/effects, signed package or release. No Unity or phone execution.
- Owner's previous device-confirmed world/save/reentry belongs only to signed [native run 42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source `e9c358eda01785b65e4eb14f18723da426635628`. Water/FFT/color/shader and full Android acceptance remain **OPEN; NOT_READY 0/3**.
- **Next:** inspect the authenticated serialized UI callback owner of the relevant dropdown in original `level0`/`level1` or prefabs, and the third caller's single original parameter **type category** in private Cecil without exposing private tokens. Trace selection→concrete method→persisted preference→render buffer vs physical display. Only then consider a scoped Android-only Settings modification and device test.
