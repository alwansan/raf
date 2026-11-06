# T2 — original Foam Shader.Find typed managed-IL call source evidence

**6 November 2026 UTC · T2 · origin chat · WATER-001 OPEN · game NOT_READY**

## Why this is distinct from the active 473-script subset
The earlier original [55,328 MonoScript PPtr proof](T2_ORIGINAL_SCRIPT_TARGET_PROVENANCE_2026-11-06.md) and [original MonoScript managed TypeDef census](T2_ORIGINAL_MONOSCRIPT_MANAGED_CLASS_BRIDGE_2026-11-06.md) do not prove how original Foam Shader is loaded. A separately active T2 chat session `20261106T1900Z-T2-chat-scene-script-typed-6f9a` owns the 473 distinct script-to-TypeDef subset. This experiment uses **different files and resource key**, directly comparing the exact authenticated serialized original Shader name to compiled `UnityEngine.Shader.Find(System.String)` call sites without touching the other scope.

## Source provenance, tool and tests
- Immutable ZIP2 source commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original owner `Raft_Data/sharedassets0.assets`: **115,978,112 bytes SHA verified** by the original PINS and reconstructed object PathID/raw SHA. Managed `Assembly-CSharp.dll`: **3,211,776 bytes SHA verified** against the same immutable original manifest. Private literal extracted with `UnityPy==1.25.4`; read by a separate `Mono.Cecil==0.11.5` net9 typed-call scanner, never printed, hashed for publication, uploaded or committed.
- Source `scripts/t2_original_foam_shaderfind_name.py`; six source-free private-name validation tests `tests/test_t2_original_foam_shaderfind_name.py`; typed Cecil scanner `android-port/Experiments/T2/FoamShaderFindOriginal/Program.cs` and its source-free call-operand selftest. Isolated CI `.github/workflows/raft-t2-foam-original-shaderfind-il.yml` with `cancel-in-progress: false` and original-source purge before artifact upload.
- Immutable source implementation at [`9aed14b5fd8a266d2ca45e4319ce78f7eda990fc`](https://github.com/alwansan/raf/commit/9aed14b5fd8a266d2ca45e4319ce78f7eda990fc); final [CI42278043015](https://github.com/alwansan/raf/actions/runs/42278043015) **SUCCESS**, job `128099419262`, six Python controls PASS and typed Cecil synthetic negative controls PASS, all original SHA gates PASS. Only a finite count-and-boolean result was published.
- Safe artifact [13534805523](https://github.com/alwansan/raf/actions/runs/42278043015/artifacts/13534805523), 555B, artifact **ZIP** SHA256 `9ada181d534edf9b06c8731f943be2e9439c91a9358e6b7acc4e01847602c16e`. This digest is **not** the source DLL, shader or private name digest.

## Actual original IL findings

| Exact verified scope | Original count |
|---|---:|
| Original methods with compiled body scanned | 19,118 |
| IL instructions scanned | 491,490 |
| IL `ldstr` instructions scanned | 7,246 |
| Exact source-original Foam Shader serialized name `ldstr` occurrences | **1** |
| Methods containing that original literal | **1** |
| Calls with exact `UnityEngine.Shader Find(System.String)` typed metadata | 81 |
| Methods containing typed `Shader.Find` calls | 25 |
| Methods with both exact original literal and typed `Shader.Find` | **1** |
| **Direct `ldstr exact_original_name` argument to typed `Shader.Find`** | **1** |
| Such direct calls in methods that also `newobj Material(Shader)` | **0** |

**Positive result:** A source-original shader object name, independently authenticated from the original serialized provider, is used immediately as the stack argument of a statically typed original managed `UnityEngine.Shader.Find(System.String)` call. This is stronger than lexical name cooccurrence, and resolves one exact original shader-name-to-managed-call-site link.

**Negative bound:** No `newobj Material(Shader)` was seen **in that same direct-Shader.Find method**. This does not prove the shader is unused, since its return can be stored, passed to another method or be assigned to a field before later Material creation. Also no runtime execution, renderer binding, CB0 upload, FFT, Foam pixel, shader import or Adreno acceptance was proven. Do not invent missing Material links or treat 81 total Shader.Find calls as 81 Foam uses.

## Next engineering action
Privately follow the **return value** of this one original `Shader.Find` call to its immediate consumer (e.g. `stloc`/`stfld`/method argument), then across original managed field references to the actual water host class. Bring in the separate 473 scene-referenced script identity result once it finishes, and integrate exact Foam ShaderLab/CB0/Material only with proved identity, followed by Unity + phone verification. T2 trial round `trial-20261106-r1` remains `لا يحتاج`: the new evidence is original source proof, not an integrated Android rendering fix. No APK/OBB/XAPK request, no Game shader/material/meta GUID/assets, FMOD, Settings, input or other T agent scope changed.
