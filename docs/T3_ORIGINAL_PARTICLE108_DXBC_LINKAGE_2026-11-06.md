# T3 — authentic original 108-use Particle Shader48 has four complete D3D11 VS/FS variant pairs

**Result: immutable source stage-linkage VERIFIED, not a restored Unity Shader or Android GPU pixel test. `RENDER-002` remains OPEN / NOT_READY.**

## Real source execution

- [GitHub Actions run 42139137265](https://github.com/alwansan/raf/actions/runs/42139137265) **COMPLETED SUCCESS** at exact stage/workflow SHA `927bf1d096f8c5500f237794b91fc71c90a946ab`; **117/117** strict source-free tests passed: 23+13+9+7+7+9+11+5+11+22. No Unity Editor, native ARM64, Vulkan shader compilation or Android APK job was run.
- Original PC Raft sources from immutable ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; all six original scenes and four original Shader/Material owners independently SHA/size verified before use (269,007,288 serialized owner bytes). Separate exact external resource provider again full-SHA verified and three original Texture2D28 byte ranges read; no game binaries uploaded.
- Selected uniquely from the original six-scene ParticleSystemRenderer→Material21→Shader48 source graph by **108** source particle renderer material slots on **54** distinct particle renderers (0 other renderer class slots), not shader name, vendor file, PathID or GUID. The selected one-Pass original Shader48 parsed state has ColorMask partial (previous channel-authenticated `RGB`), alpha-dependent blending and ZWrite OFF.
- `UnityPy 1.23.0` parsed exactly this one source Shader48. The correct original D3D11 compressed graphics platform (Unity platform 4) was decoded with independent multi-segment records; `w1_recover_depth_passes.linked_program` authenticated exact serialized Shader pass `m_BlobIndex`, private program-table entry bounds, one DXBC container per entry and correct shader stage identity, **not** by guessing stage from filename.

## Actual source-only program availability

| Exact original selected source Shader48 fact | Genuine count |
|---|---:|
| Original Shader48 SubShaders | 1 |
| Original passes | 1 normal Pass |
| D3D11 program table records | 16 |
| Source vertex stage variant records linked to genuine D3D11 | **4** |
| Source fragment stage variant records linked to genuine D3D11 | **4** |
| Distinct genuine linked D3D11 stage programs | **8** |
| Identical original vertex/fragment shader keyword permutation pairs | **4** |
| Linked stage variant records carrying keywords | **6** |
| Unpaired vertex permutations | **0** |
| Unpaired fragment permutations | **0** |
| Original Pass with at least one linked vertex/fragment pair | **1 / 1** |

**New diagnostic conclusion:** AssetRipper's source-authenticated selected Shader48 exported to a marked `//DummyShaderTextExporter` with a deceptively complete one-Pass/`CGPROGRAM` block in [real CI42136474867](https://github.com/alwansan/raf/actions/runs/42136474867). The underlying immutable PC Shader source **does contain a valid original D3D11 program linkage for four matched vertex/fragment keyword permutations**. The dummy text therefore reflects a bounded plain AssetRipper export shortcoming, not absence of executable original D3D11 source records.

**What is NOT proved:** D3D11 code has not been translated to Vulkan SPIR-V / Unity HLSL, validated for stage IO, pixel sampling/fragment alpha, shader import or actual native Adreno compilation. Successful source stage-linkage does not establish that this original 108-use shader is the exact fire/smoke emitter seen on the user's phone. The full T5 post-vendor Unity project might also replace this dummy independently; verify it before any production rewrite.

## Guardrails

- New `scripts/t3_original_particle108_dxbc_feasibility.py`: exact original source graph SHA/one Shader48 selection; fail-closed original parsed fixed-function one-Pass state check; strict records/stage validator; verify serialized permutation key equality without publishing source program hashes, names, IDs, GUIDs or binary blobs. `NO_D3D11` would be explicit if platform absent, not guessed from a dummy file.
- New `tests/test_t3_original_particle108_dxbc_feasibility.py`: nine source-free guards for rank/provenance, real linked pair, keyword-preserving permutation pairing, unpaired variant, no D3D11 platform, wrong stage, duplicate permutation, missing fragment and malformed table. Isolated SHA-source `.github/workflows/raft-t3-original-renderer-shader-impact.yml` reran on genuine files with all guards.
- No `.shader`, `.meta`, game texture, Material21, prefab/scene, original shader program, user saved world, Unity Android APK/OBB, sound, Settings, touch or water/FFT file was changed. No other team's CI cancelled; only safe numeric JSON output published.

## Next distinct experiment

On a **disposable exact original source** runner, translate a bounded first matched pair (or four private pairs) through verified `vkd3d-compiler` DXBC→Vulkan1.1 SPIR-V→`spirv-val`, examine `spirv-cross` fragment/vertex resource and IO bindings privately and emit only semantic categories. Preserve exact four serialized keyword permutations and ShaderLab fixed-function blend/mask. If translatable, author a per-stage ShaderLab prototype in a disposable source-only test, then separately verify native full pipeline and Android device screenshot before touching production shaders. Coordinate with T5 native source→export GUID and exact phone emitter identification.

**Project gate: RENDER-002 OPEN / NOT_READY.**
