# T2 — authentic original Foam Material field to typed Graphics API source proof

**2026-11-06 UTC · WATER-001 OPEN · T2 · session `20261106T2044Z-T2-chat-field-consumer-trace-d4a6` · game NOT_READY**

## What this adds to original Raft water reconstruction

Earlier SHA-original source [CI42284117891](https://github.com/alwansan/raf/actions/runs/42284117891) proved an exact original `Shader.Find(OriginalFoamName)` → `new Material(Shader)` → unique original managed `Material` field store. It found 13 exact field loads over 4 methods but no *immediately adjacent* `Renderer.set_material` calls. Adjacency alone was insufficient to determine whether the original material was actually passed to drawing APIs.

This independent follow-up implements a **bounded forward typed-IL stack identity trace from every exact original Material FieldDefinition load**. It tracks a Material reference through duplicate opcodes, a declared Material local, bounded intervening stack operations and fully typed Mono.Cecil method calls. A call counts only when the *actual tainted stack value* is supplied as the `UnityEngine.Material` parameter or receiver. Calls whose Material argument is merely present elsewhere in a method are not counted. Only 32 instructions per site are permitted; branches, returns, throws, unresolved calls and unknown stack effects stop the trace. It never publishes original private identifiers, method bodies, original IL, GUIDs, private shader bytes or original material strings.

### Source-authenticated results

| SHA-original check | Verified count |
|---|---:|
| Compiled methods / original IL instructions inspected in existing source scanner | 19,118 / 491,490 |
| Exact original `Foam Shader.Find` matches | 1 |
| Exact original `Material(Shader)` → Material FieldDefinition stores | 1 |
| Exact original Material field loads | **13** |
| Exact field load sites inspected by new bounded API trace | **13 / 13** |
| Following IL instructions analyzed across these sites | **98** |
| Load sites supplying a typed `Material/Object` instance receiver | **9** |
| Load sites supplying a typed `UnityEngine.Material` API parameter | **2** |
| Of these, real typed `UnityEngine.Graphics` parameter sites | **2** |
| Typed `UnityEngine.Rendering.CommandBuffer` parameter sites | 0 |
| Typed `UnityEngine.Renderer` parameter sites | 0 |
| Other typed `Material` parameter sites | 0 |
| Per-site source trace bounds / ambiguous control-flow boundaries encountered | **0** |
| Source original Unity 2021 material draw runtime / Adreno water pixels | **not verified** |

This distinguishes **actual source type-correct Graphics argument flow** from proximity or name-only source scans. It establishes an original compiled **Graphics API consumer** of the dynamically constructed Foam Material, but **does not identify which private Graphics method was called in this public report, prove source path executed at runtime, match an Android shader import, verify any CB0 upload or prove water pixels**. Do not turn the positive source count into a phone-readiness or finished-water claim. A site with zero counted APIs can consume the value through a path not covered by the narrow bounded proof.

## Reproduction and safety

- Public source branch code commit [`589cdf6160176f913c90e69d9105d7255d00b835`](https://github.com/alwansan/raf/commit/589cdf6160176f913c90e69d9105d7255d00b835) modifies only the already T2-owned `android-port/Experiments/T2/FoamShaderFindResultFlow/Program.cs`, `scripts/t2_foam_shaderfind_return_report.py`, `tests/test_t2_foam_shaderfind_return_report.py`.
- Full [GitHub Actions **42291227491 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42291227491) at exact code SHA (job `128144861565`). **53/53** strict source-free aggregate synthetic Python tests, **6/6** original-name synthetic Python controls, C# Mono.Cecil `--selftest` including genuine Material-parameter stack-position, nonadjacent typed local pass-through, counterfeit signature rejection and branch stop, all PASS.
- ZIP2 source commit **`15964ea8f246b6e076ce26b60931ee2e1a9a2385`**, original source Shader owner **115978112B**, and original managed assembly **3211776B**, independently SHA authenticated using pinned manifest before inspecting private source in ephemeral Actions only. `UnityPy==1.25.4` plus `Mono.Cecil==0.11.5`, isolated .NET 9; source and private source-name scratch purged before publication.
- Source-only safe JSON artifact [`13539837293`](https://github.com/alwansan/raf/actions/runs/42291227491/artifacts/13539837293), **1216B** ZIP, artifact digest `sha256:039b502d19d067980352e014acae9243b7145e1249517bfa8681d08e9259d037`. JSON contains bounded counts and explicit false runtime flags only.
- Exact CI workflow is pre-existing T2-owned `.github/workflows/raft-t2-foam-original-shaderfind-resultflow.yml`, push paths scoped to T2 files, `cancel-in-progress: false`. No native Unity package job dispatched, no original source exported, no game scene/shader/asset/.meta/GUID modified.
- Parallel T2 scheduled source installer collision guard stays untouched. T1 FFT, T3 colors, T4 physical input and T5 delivery paths untouched. The [older native job 42281310905](https://github.com/alwansan/raf/actions/runs/42281310905) failed separately before actual water import at T4 Editor mouse type; it cannot establish Foam pixels.

## Next engineering work

**T2:** Recover the exact private, typed original `Graphics` method's Material argument role and material-to-renderer effect inside the already SHA-pinned private experiment without publishing names/IL, then join the hosting MonoScript class to the 427 source-proven scene script classes. **T5:** in a future properly authorized native export, use the [strict original Foam GUID/Material preflight](T2_FOAM_EXPORT_GUID_MATERIAL_PREFLIGHT_2026-11-06.md), safely install SHA-original two-pass private candidate retaining original .meta/GUID before Unity import, and verify source recompilation and runtime/phone pixels. Spectrum, Depth Copy, FFT, texture/CB0 state must also meet their own contracts.

T2 trial build vote **`trial-20261106-r1: لا يحتاج`** unchanged: no substantial runnable Android water ShaderLab/CB0 code landed in this cycle. No new XAPK or claims of READY. Overall WATER-001 OPEN.
