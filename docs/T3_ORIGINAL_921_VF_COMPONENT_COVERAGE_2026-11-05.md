# T3 — Original Shader48 four-pass vertex/fragment component coverage (2026-11-05)

**Issue:** RENDER-002 OPEN. **Status:** authenticated source-only structural result; **NOT** original DXBC semantic, ShaderLab, Unity/Vulkan pixel or phone acceptance.

## Question / exact provenance

Original six Raft scenes, four serialized Shader/Material owners and the high-use original Shader48 were validated against ZIP2 source commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385` (four owners total 269,007,288 verified bytes, no LFS). Its original Material graph showed **921 Renderer Material-slot uses**. The inherited source link analysis found **33 exactly linked original vertex/fragment variant pairs** across four normal Passes with eight unmatched original vertex variants; this experiment translated only **one exact matched variant pair per Pass**.

The original and derived HLSL SPIR-V stages were reflected in disposable private runner storage. The bridge `scripts/t3_original_921_vf_component_bridge.py` reconciles private SPIRV-Cross located type/Location records with the previously source-authenticated safe reflection via a multiset check; adds `Component` only when present and validated; forbids unknown multi-dimensional array/decorated layouts; drops private generated names/IDs. An independent component classifier `scripts/t3_vf_spirv_component_coverage.py` rejects overlap/type mismatch and never claims semantic/interpolation/pixel proof.

## Proof / repeatability

- [Successful real original CI42068915602](https://github.com/alwansan/raf/actions/runs/42068915602), runner source request commit `df1d56d385e6961d8d3442caf8d9a1cc43f190da`, **completed success**.
- Source-free bridge+classifier [CI42067757782](https://github.com/alwansan/raf/actions/runs/42067757782) succeeded 17+17 synthetic tests; source-free checks inside genuine CI also succeeded.
- Genuine CI safe summary artifact: `t3-921-original-VF-component-counts-42068915602`, id `13435221320`, 7-day retention. No original DXBC/SPIR-V/HLSL/source names/hashes were uploaded.
- Original authenticated 6 scene files, 4 owners. **4 original Passes / 8 genuine D3D11 stages**, all original/derived SPIR-V reflections complete. Compiler-generated names from prior authentic [CI42062573338](https://github.com/alwansan/raf/actions/runs/42062573338) were **0/34** inputs and **0/29** outputs retained after HLSL roundtrip. Those labels cannot be used as source semantic evidence.

| Safe aggregate across four original Passes | Source SPIR-V | Derived HLSL roundtrip SPIR-V |
|---|---:|---:|
| Vertex→Fragment pairs measured | 4 | 4 |
| `STRUCTURAL_CANDIDATE_ONLY` | 4 | 4 |
| `STRUCTURAL_DEFICIT` | 0 | 0 |
| `INCONCLUSIVE_UNSUPPORTED_TYPE` | 0 | 0 |
| Vertex output records | 22 | 22 |
| Fragment input records | 14 | 14 |
| Vertex output scalar components | 75 | 75 |
| Fragment input scalar components | 44 | 44 |
| Fragment components without vertex counterpart | 0 | 0 |
| Fragment components with mismatched scalar family | 0 | 0 |
| Vertex components not used by Fragment | 31 | 31 |
| Unsupported types within selected interface | 0 | 0 |

**Conclusive within the sampled programs:** Neither the original compiled SPIR-V interface nor its HLSL-generated roundtrip has a Location+Component scalar-family deficit from paired vertex outputs to fragment inputs. Thus a basic inter-stage component loss is **not demonstrated for these four matched source permutations**. Count equality does **not** show identical semantic values, interpolation, rasterization, binding side effects, color, or pixels. Aggregate counts may conceal changes not represented by that safe measurement.

## Corrected infrastructure failures retained

- [CI42068542470](https://github.com/alwansan/raf/actions/runs/42068542470) rejected at YAML parse due to an unquoted colon inside the job `if` expression. Fixed `b6027ff6e7bb26897692d0d9b23b93c9afa7e303`, later source-free CI passed.
- [CI42068710185](https://github.com/alwansan/raf/actions/runs/42068710185) was rejected at the explicit marker-only commit guard because a one-commit shallow checkout couldn't compare to its parent. No private source was read. Fixed `fetch-depth: 2` at `b3e6caeffdb4cfc592cf05526f5c0ae9b6aedbc5`; marker retry yielded successful original CI42068915602.
- Work registration and branch write use HEAD-safe GitHub Contents API commits. All other agents' source/workflows remain unchanged. T5 native [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) and T1 FFT [42066983894](https://github.com/alwansan/raf/actions/runs/42066983894) were not cancelled.

## Rejected assumptions and handoff

Source-free Python contract passing cannot establish game pixels. Typed SPIR-V Location/Component compatibility cannot establish original compiled DXBC semantic name/index/register/mask mapping, interpolation qualifiers, texture/sampler/CB bindings, shader keyword permutations or numerical equality. One sampled matched pair per Pass does not cover the other 29 matched original pairs nor eight unpaired vertex permutations.

**Next useful step:** join the separate scheduled T3 DXBC signature reader's source-authenticated register/mask/system-value evidence to private SPIR-V builtin/Location/Component mappings for the same exact eight compiled programs. Do not equate compiler-generated reflection names to original semantics; enforce format/offset/size parity and publish safe aggregate only. In parallel, inspect authentic ShaderLab Pass states and material/texture/sRGB bindings before changing a shader or blaming the white pixels. Actual device test and three immutable readiness reviews remain outstanding; RENDER-002 OPEN.
