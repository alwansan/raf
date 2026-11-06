# T5 DISPLAY-003 — original Resolution caller's typed parameter and Dropdown API

- **Session**: `20261106T1221Z-T5-chat-resolution-param-5df2`, `origin=chat`. Writing branch `feature/android-native-port` only.
- **Actual original CI**: [42217714507](https://github.com/alwansan/raf/actions/runs/42217714507) job `127891776765`, exact source `82a8d38962f97bdae7ff9be030a44af72331e03a`, **COMPLETED SUCCESS**. **9/9 Python adversarial unittest methods** and **8/8 C# Cecil categorical fixture assertions** passed, plus verified actual original source inventory and fail-closed gate.
- **Input**: immutable ZIP2 provider `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, source `Raft/Raft_Data/Managed/Assembly-CSharp.dll`, exactly **3,211,776 bytes**, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Analysis tool Mono.Cecil 0.11.5 / .NET 9 / ubuntu-24.04. Original binary, private type identities, tokens, IL and decompiled source stayed private in the runner; no uploaded raw content.
- **Previous proof**: [42210936332](https://github.com/alwansan/raf/actions/runs/42210936332) proved exactly 3 `GraphicsSettingsBox.ApplyCurrentResolutionAndFullscreenMode` direct sites across 3 unique containing methods, one has 1 non-int/bool parameter and eight Dropdown API calls; [42208532103](https://github.com/alwansan/raf/actions/runs/42208532103) proved the 2 delegate sites resolve to a single non-resolution target.

## Original compiled IL: unique one-parameter caller

| Authenticated category | Exact result |
|---|---:|
| `GraphicsSettingsBox` compiled method bodies | 42 |
| Direct Apply callsites / distinct owners | 3 / 3 |
| Zero-parameter caller methods | 2 |
| Single-parameter caller methods | 1 |
| **Single argument type category** | **custom_reference_type** |
| Single-parameter caller access | private |
| Single-parameter caller static / virtual | false / false |
| Single-parameter caller return type | void |
| Direct Dropdown API calls / Dropdown-typed field reference sites | 8 / 8 |
| Direct Dropdown value reads (`get_value`) | 0 |
| Direct Dropdown value writes (`set_value` or `SetValueWithoutNotify`) | 4 |
| Direct `RefreshShownValue` calls | 1 |
| Direct Dropdown `get_onValueChanged` | 0 |
| Direct `AddListener` calls (within caller **and whole `GraphicsSettingsBox` class**) | 0 |
| Direct `PlayerPrefs` writes / `Screen.SetResolution` / `ScalableBufferManager.ResizeBuffers` in caller | 0 / 0 / 0 |

The custom reference type category intentionally does not publish the proprietary parameter identity. It is not a standard `int`, `bool`, `UnityEngine.Resolution`, `UnityEngine.UI.Dropdown` or `TMPro.TMP_Dropdown` argument. These categories come from compiled IL type references, not from source spellings or an inferred field name. In this class the complete direct instruction census found **zero** compiled `get_onValueChanged` and `AddListener` calls, but that **does not** exclude serialized UnityEvent bindings, custom event wrappers, indirect invocations in other classes or native Unity behaviors.

**Interpretation**: a private instance method receiving a custom object and performing four direct Dropdown value-setting calls, one shown-value refresh and zero direct value getters is **consistent with UI synchronization/display** rather than the usual one-`int` value-change handler. This narrows the candidate, **not proof** of its runtime purpose, the user selection callback, or preference save/reload.

## Decision and next actionable test

- Do **not** add a second Resolution UI or change working Settings/landscape. In the latest owner status Settings was functioning; there is no new phone regression linked to this test.
- An actionable source-only follow-up would identify the single custom reference type's **role** (e.g. configuration object vs runtime screen mode) without revealing private symbols, and correlate it to typed original serialized UI event/prefab binding; prove selection→handler→saved graphics setting separately. Stronger proof requires genuine signed Android-device testing.
- This cycle did not build Unity/IL2CPP, package APK/OBB, modify original C#/assets/shaders/.meta/GUIDs, touch any T1/T2/T3/T4 files, or run an on-device performance test. Owner's world/save/re-entry still belongs to [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) only. Original water FFT/shaders/color and device acceptance remain **OPEN, overall NOT_READY 0/3**.
- **T5 role priority after this boundary**: resume high-impact original game integration/Android package performance and water/shader evidence in coordination with T1–T3; do not continue adding low-value metadata censuses to already working Settings unless a real blocker changes the hypothesis.
