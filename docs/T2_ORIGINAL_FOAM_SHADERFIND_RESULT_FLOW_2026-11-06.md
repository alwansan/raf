# T2 — Original Foam Shader.Find return value → original managed Material(Shader) argument

**Date:** 2026-11-06 UTC · **owner:** T2 · **origin:** chat · **issue:** WATER-001 remains OPEN · **game:** NOT_READY.

## Authentic new source conclusion

SHA-pinned original Raft serialized Foam Shader `m_Name` is passed as the immediate literal argument to an **original typed** `UnityEngine.Shader.Find(System.String)` managed-IL call. This call's returned `UnityEngine.Shader` value is stored immediately into an **instance field whose type is UnityEngine.Shader** and whose real original `Assembly-CSharp.dll` `FieldDefinition` is resolved, not a mere string guess. Exactly **two** original managed `ldfld` instructions in **two methods** reference that same authenticated field symbol. In **one** method, that exact `ldfld` is immediately followed (no intervening IL side-effect instructions) by `newobj UnityEngine.Material::.ctor(UnityEngine.Shader)`.

**Typed source dataflow proven:**

`original Foam Shader.m_Name` → `ldstr` → `call UnityEngine.Shader.Find(System.String)` → `stfld <original resolved Shader field>` → `ldfld <same original resolved Shader field>` → `newobj UnityEngine.Material::.ctor(UnityEngine.Shader)`.

This is **one original code path**, not proof that this path runs on Android, that the source Shader.Find returns a non-null registered runtime Shader, that this Material is assigned to the water renderer, or that source CB0/texture/samplers/FFT/pixels render correctly.

## What was actually executed

- Original ZIP2 immutable commit: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Original Foam Shader object provider `Raft_Data/sharedassets0.assets` **115,978,112 bytes** SHA checked via original pinned manifest + Unity object's own raw-object identity. Original managed `Assembly-CSharp.dll` **3,211,776 bytes** independently SHA checked against the same immutable manifest. SHA checks precede literal extraction and IL scanning.
- Private source name recovered with pinned `UnityPy==1.25.4` and held only in private runner scratch, then consumed via separate `Mono.Cecil==0.11.5` net9 scanner. Exact, case-sensitive source string; exact typed method, original field `FieldDefinition.Resolve()` and same metadata token; direct `ldfld` to one-parameter Material constructor verified, with only bounded `nop` skipping.
- Code: `android-port/Experiments/T2/FoamShaderFindResultFlow/Program.cs`, `FoamShaderFindResultFlow.csproj`; safe assertion: `scripts/t2_foam_shaderfind_return_report.py`; **21** fail-closed synthetic aggregate tests `tests/test_t2_foam_shaderfind_return_report.py`; **6** source original name controls; typed Cecil selftest. Isolated workflow `.github/workflows/raft-t2-foam-original-shaderfind-resultflow.yml` with pinned ZIP2 and private source purge before public safe artifact upload.
- First [CI42280001282](https://github.com/alwansan/raf/actions/runs/42280001282) **SUCCESS** established original instance Shader field, two reads and one reader method with Material ctor, without claiming the argument link. During tightening, [CI42280404780](https://github.com/alwansan/raf/actions/runs/42280404780) **failed** at safe JSON schema stage because source added an extra aggregate before matching validator; source scan was not considered failed. After synchronizing validator [CI42280450929](https://github.com/alwansan/raf/actions/runs/42280450929) **SUCCESS** and proved the single direct original field → ctor argument.
- **Final [CI42280502421](https://github.com/alwansan/raf/actions/runs/42280502421) SUCCESS** at `4bc616aab744f00111581916b804699b47c87b1c`, job `128107906474`, **21** source-free negative assertions, **6** original-name negative tests and independent typed-Cecil selftest all PASS. The source original owner and DLL were SHA authenticated again; the direct flow evidence remains stable.
- Safe count-only artifact [13535172390](https://github.com/alwansan/raf/actions/runs/42280502421/artifacts/13535172390), **723-byte ZIP**, artifact ZIP SHA256 `ae85a4cbbfdf830e3a3f77d97faba7021bd99f2c30e2c1f9fe6026265314304d` (NOT proprietary original-source digest). Scratch original source, private shader literal, original managed DLL staging purged before artifact upload.

## Results by strictly bounded source-authentic counts

| Source IL evidence | Value |
|---|---:|
| Original compiled methods | 19,118 |
| Original IL instructions | 491,490 |
| All typed `Shader.Find(System.String)` calls | 81 |
| **Exact original Foam Shader name direct typed Find** | **1** |
| **Find result stored in exact original instance Shader field** | **1** |
| Same original Shader field loads | **2** |
| Distinct methods reading same field | **2** |
| Field-reader methods also constructing `Material(Shader)` | **1** |
| **Direct same-field load passed into `Material(Shader)`** | **1** |
| Exact original field identity successfully resolved | **1** |
| CB0 GPU upload, renderer binding, Unity runtime execution, Android pixels | **not verified** |

Counts and boundaries match pinned original SHA and are not estimates. The original field/method/class/string names, raw IL, local paths, PathIDs and GUIDs were neither exported nor logged.

## Evidence connections and next blocker

Separately completed original [473 scene-referenced MonoScript TypeDef subset CI42276583082](https://github.com/alwansan/raf/actions/runs/42276583082) proved 427 of 473 refer to a unique exact managed `Assembly-CSharp` TypeDef (one ambiguous, 45 other assembly). That scan did **not** yet prove whether this specific original Shader field declaring class or its use site is among the 427 scripts on the played scene, nor whether the resulting Material becomes the active Renderer material.

**Next:** Follow the newly proven `new Material(Shader)` returned value into original managed field/setters or renderer component assignment; only then join scene class/renderer source pointers and the exact original Foam ShaderLab, CB0, texture, sampler and runtime water effect. Prove source/Unity behavior separately from Android pixels and saved worlds.

No changes to Unity game assets, .meta/GUID, ShaderLab or original game source, FMOD/audio, Settings, touch or other agents' files. T2 trial vote `trial-20261106-r1` remains **«لا يحتاج»** because this source link is not yet an integrated Android visual fix. No APK/OBB/XAPK requested. WATER-001 OPEN and full game NOT_READY.
