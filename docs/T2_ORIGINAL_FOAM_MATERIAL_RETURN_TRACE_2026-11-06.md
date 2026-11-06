# T2 — authentic original Foam Material alias to a real serialized managed Material field

**2026-11-06 UTC · T2 · origin chat · WATER-001 OPEN · NOT_READY**

## Exact original source finding

The original Foam Shader object's true serialized name, SHA verified from original Unity source ZIP2, is passed directly into one typed original `UnityEngine.Shader.Find(System.String)` IL call. Its `UnityEngine.Shader` result is stored in a resolved original managed instance field, and one exact `ldfld` supplies the `Shader` argument for `newobj UnityEngine.Material::.ctor(UnityEngine.Shader)`.

**New in this cycle:** The next original IL opcode after construction is **`dup`**, so the constructor return cannot be interpreted by a one-instruction store/renderer probe. A conservative, maximum-48-instruction **straight-line stack-alias trace** (stop on branch, return, throw or unknown stack effect) followed both original alias copies. Actual source trace took **5** instructions and stopped with **0 ambiguous boundaries**, proving:
- **one typed instance-method call** consumes one original `Material` reference as its receiver;
- **one store of the other Material alias** to a uniquely resolved, exact original `Assembly-CSharp` `FieldDefinition` whose declared type is `UnityEngine.Material`;
- across the original managed assembly, that **same material field is read in 13 IL instructions across 4 methods**;
- among those **13 exact field loads**, **0** directly supply `Renderer.set_material(Material)` and **0** directly supply `Renderer.set_sharedMaterial(Material)`.

The narrow hypothesis `dup; ldstr; typed set_*(string); Material-store` is **not supported** by the genuine source (0 matching named-setter shape); it was not substituted with fake code. The generic, source-only alias trace then established the actual field destination. No assertion of missing renderer use is made: source consumers can pass Material through other typed APIs, local variables, draw/command-buffer paths or non-adjacent IL sequences. No original field/method/class names, raw IL, private path IDs, serialized assets, GUIDs or proprietary name hashes were exported.

### Exact verified safe original source counts

| Evidence | Count |
|---|---:|
| Original compiled method bodies | 19,118 |
| Original IL instructions | 491,490 |
| Original typed Shader.Find calls | 81 |
| Exact original Foam name → typed Shader.Find calls | 1 |
| Original Shader field direct → Material(Shader) constructor | 1 |
| Original Material constructor return duplicated (`dup`) | 1 |
| Straight-line Material alias instructions inspected | 5 |
| Ambiguous-flow/branch boundaries hit | 0 |
| Typed method calls on the authenticated Material alias | **1** |
| Exact original Material FieldDefinition stores from original alias | **1** |
| Exact original Material field IL reads | **13** |
| Distinct methods reading same original Material field | **4** |
| Exact-field load immediately used as `Renderer.set_material` argument | **0** |
| Exact-field load immediately used as `Renderer.set_sharedMaterial` argument | **0** |
| Runtime Material/Renderer binding, original CB0 upload, Android pixels | **not verified** |

## Reproducibility and source privacy

- Immutable original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original authentic Foam shader serialized owner `Raft_Data/sharedassets0.assets` **115,978,112 bytes** SHA checked via original source manifest + exact object identity. Independently SHA checked original `Assembly-CSharp.dll` **3,211,776 bytes** from immutable original manifest. Never reconstruct source from unpinned game files or leak private symbol names.
- `Mono.Cecil==0.11.5` net9 typed IL scanner `android-port/Experiments/T2/FoamShaderFindResultFlow/Program.cs`, with source-original `UnityPy==1.25.4` private `Shader.m_Name` staging, exact source original field token comparison, bounded forward IL stack effect validation and negative synthetic controls.
- Source-owned `scripts/t2_foam_shaderfind_return_report.py` rejects duplicate keys, wrong source SHA flags, unknown numeric output, false runtime success, partial/zero direct name-to-Shader.Find-to-Material proof, fabricated Material field/Renderer edges, unbounded stacks or counts. `tests/test_t2_foam_shaderfind_return_report.py` **44** synthetic tests and `tests/test_t2_original_foam_shaderfind_name.py` **6** tests. A source-free Cecil selftest includes valid/invalid typed Material duplication, store and branch rejection.
- Independent T2 workflow `.github/workflows/raft-t2-foam-original-shaderfind-resultflow.yml`, original source checkout pinned and purged before safe artifact upload. No original DLL, shader literal or raw data published.
- First [CI42282679089](https://github.com/alwansan/raf/actions/runs/42282679089) **SUCCESS** at `0c86c303a61247033f20ee2ffc9dca43779538fd`: 31+6 sourcefree tests, original `dup` result and 0 direct renderer setter.
- Next [CI42283382388](https://github.com/alwansan/raf/actions/runs/42283382388) **SUCCESS** at `2df87a5d63fc562ecc9159b0ff768d1aa96cb028`: 38+6 sourcefree controls, strict one-string typed setter candidate **not observed** (0); honest negative, no fabricated link.
- **Final [CI42284117891](https://github.com/alwansan/raf/actions/runs/42284117891) SUCCESS** at source commit `289b9711a1e26118a0af921c43b1a86112919328`, job `128120397510`. **44/44** source-free aggregate negative controls, **6/6** source original name controls and typed Cecil selftest PASS, original SHA staging PASS. It proved **1 exact Material field store**, then **13 original IL field loads in 4 methods**. Only safe count-and-bool source report artifact [13535764546](https://github.com/alwansan/raf/actions/runs/42284117891/artifacts/13535764546), artifact ZIP **1101 bytes**, ZIP SHA256 `da58031b87164cf7ca62876f2810c5adc76e827801df9bd9daee93f6ee837cf8` (not a proprietary original asset checksum).
- A native Unity build was already active at [CI42281310905](https://github.com/alwansan/raf/actions/runs/42281310905) and had not completed at this session's latest check. T2 neither initiated/cancelled it nor modified native build-request, original/game ShaderLab, scene, material, .meta/GUID, audio, Settings, touch or other T agents' files.

## Next actual engineering goal

Trace the **13 exact original Material field load sites** into typed `Graphics`, `CommandBuffer`, `Material` and other Unity APIs using private, bounded stack/dataflow (not only immediate `Renderer.set_material`). Join the Material field's original declaring managed TypeDef with the **427 true scene-referenced script classes** from [CI42276583082](https://github.com/alwansan/raf/actions/runs/42276583082) before claiming a playable water host; then recover runtime CB0/texture/sampler shader translation and finally verify actual Unity/Adreno drawing. Trial vote `trial-20261106-r1` T2 remains **لا يحتاج**: source IL evidence alone does not justify an independent new phone APK, and an unrelated native build was already running. WATER-001 OPEN, game NOT_READY.
