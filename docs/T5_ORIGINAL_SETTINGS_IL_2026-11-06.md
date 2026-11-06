# T5 DISPLAY-003 — original compiled Settings resolution IL audit

Session: `20261106T1030Z-T5-chat-resolution-il-4b9e`, origin `chat`. **Source-only**, not a new Unity/Android build.

## Authentication and exact experiment

The [independent CI run 42204488410](https://github.com/alwansan/raf/actions/runs/42204488410) completed successfully, using Mono.Cecil 0.11.5 and .NET 9 on Ubuntu 24.04. Its original input was the **immutable ZIP2 managed Assembly-CSharp.dll** from `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385`; the isolated runner verified size **3,211,776 bytes** and SHA-256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`, as independently used by T5's previous original FileManager metadata oracle. The checked original file was never uploaded or modified.

Source `android-port/Experiments/T5/ResolutionILProbe/Program.cs` reads compiled ECMA-335 call instructions, not ILSpy text or guessed source. Its report permits only bounded numeric categories, not method/field names, IL bytes, private asset content or decompiled source. The companion `scripts/t5_validate_resolution_il_probe.py` requires exact schema, source attestation, expected original two API boundaries and false success/provenance flags.

## Actual original DLL results

| IL category | GraphicsSettingsBox | DynamicResolution |
|---|---:|---:|
| Compiled methods with a body | 42 | 7 |
| Call/newobj instruction sites | 257 | 14 |
| `Screen.SetResolution` | 1 | 0 |
| `Screen.resolutions` reads | 9 | 0 |
| `Screen.currentResolution` reads | 3 | 0 |
| Direct `PlayerPrefs.Get*/Set*/Save` | 0 | 0 |
| Direct `AddListener` calls | 0 | 0 |
| Dropdown-like population call categories | 1 | 0 |
| Own `ApplyCurrentResolutionAndFullscreenMode` calls | 3 | 0 |
| Direct member references to `DynamicResolution` | 0 | 64 |
| `ScalableBufferManager.ResizeBuffers` | 0 | 2 |
| Delegate target references within same type | 2 | 0 |

Results are unclassified aggregate **callsite counts**, not a complete interprocedural call graph. In particular, **zero direct AddListener does not prove no serialized/custom callback**; a Unity prefab or delegated event could wire a callback without a direct `AddListener` call in this class. Similarly, no direct `PlayerPrefs` call does **not** rule out the game's custom persistence. The original GraphicsSettingsBox contains no direct compiled member reference to DynamicResolution in the inspected type; an indirect or native connection remains unverified.

The exact original compiled IL includes one Screen.SetResolution call and two separate DynamicResolution.ResizeBuffers calls. This independently supports the older lexical source audit but does **not** prove the dropdown selection produces an Android render-scale change, that rendering is aspect-correct, or that a user selection persists across launches.

## Test result, guardrails and next step

- [CI 42204488410](https://github.com/alwansan/raf/actions/runs/42204488410) completed **SUCCESS** on source commit `bf64f38e5770664e9fc1bb75f2a6befa7d1d7081`. **8/8 Python adversarial tests**, **4/4 C# self-test assertions**, authentic original DLL metadata scan and two API site assertions completed.
- The negative controls reject fake Android success, extra private fields, missing input authenticity, wrong site counts, malformed/duplicate JSON fields and symlink/oversized report.
- This experiment did **not** edit Android Unity gameplay code, original shaders, materials, `.meta`/GUIDs, Settings UI, touch/gamepad, native build requests, packages, releases, T1–T4 source or private original bytes. No game APK or phone run.
- The owner-confirmed native world/save/exit/reopen on [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source `e9c358e`, remains an older-build observation and does not validate this probe or any future resolution control.
- **Next targeted investigation:** on the same SHA-pinned original binary, classify the **two** original same-type delegate targets' bounded direct calls and the resolution option-population method's calling chain; then inspect authenticated serialized UI callback owners before implementing any Android render-resolution selection or persistence. Maintain strict separation of physical screen mode, app surface, render scale, refresh Hz and measured FPS.
- Result classification: `SOURCE_VERIFIED_RESOLUTION_IL_PATH_INCOMPLETE_BINDING`. The general rendering/water/Adreno acceptance gates remain OPEN; full **NOT_READY 0/3**.
