# T3: original compiled DXBC vertex/fragment semantic and mask linkage — 2026-11-05

**Issue:** RENDER-002 OPEN. **Evidence:** [CI42071059741](https://github.com/alwansan/raf/actions/runs/42071059741) **SUCCESS** (authenticated real PC Raft source), public safe artifact `t3-original-921-DXBC-semantic-safe-42071059741` id `13436566216`, seven-day retention. This is original compiled signature evidence, **not** DXBC→SPIR-V named semantic binding, ShaderLab reconstruction, Android Vulkan or device pixel proof.

## Exact immutable input and bounded scope

- ZIP2 original source repo SHA: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; SHA-verified six original scenes and four original Shader/Material owner files (269,007,288 verified bytes, no LFS); original Shader48 selected by **921 Renderer→Material slots** in six scenes.
- Genuine source Shader48: four normal original Passes, 33 exact linked compiled permutation pairs and eight unmatched source vertex permutations. This experiment selects **one identical-key, same-player-bucket D3D11 compiled Vertex/Fragment variant pair per Pass**; thus 4 matched pairs and 8 original programs. Other 29 matched variants and eight unmatched vertex variants remain untested here.
- All eight original program DXBC containers passed bounded magic/version/size/chunk-offset checks. Each had original `ISGN` and `OSGN` program signature chunks (8 of each); no `ISG1`, `OSG1`, `OSG5` encountered in this exact original scope.
- Private semantic name/index/system-value register/component-type and mask fields were decoded from genuine compiled binaries. Joining happens **inside the private job only**. The public report retains no original semantic strings, program code, hashes, original object IDs or per-program inventory.

## Findings: original DXBC stage semantic compatibility

| Safe aggregate (four exact authentic V/F Pass pairs) | Measured |
|---|---:|
| Compiled original D3D11 programs examined | 8 |
| Fragment user input semantic records | 22 |
| Vertex user output semantic records | 22 |
| Fragment semantics paired with a matching original Vertex semantic name+index | **22/22** |
| Fragment user semantics lacking a matching Vertex semantic | **0** |
| Missing declared component lanes on paired Vertex output masks | **0** |
| Paired semantic component-type mismatches | **0** |
| Unused original Vertex user semantic records | **0** |
| Declared Fragment user input component-mask lanes | 75 |
| Declared Vertex user output component-mask lanes | 75 |
| Authenticated original stage register component lanes (VS / FS) | 75 / 75 |
| DXBC signature system-value entries (input / output combined) | 4 / 4 |

**Supported conclusion:** The **declared original D3D11 semantic name+index, component-type and component masks** are compatible in all four sampled source Vertex/Fragment pairs. It is therefore not justified to blame a missing original DXBC VS→PS semantic in this scope for white materials. This is stronger than comparing compiler-generated SPIR-V labels but does not demonstrate **Vulkan/SPIR-V semantic mapping, interpolation, read/written masks, execution values, texture sampling or final pixels**.

An independently verified earlier [CI42068915602](https://github.com/alwansan/raf/actions/runs/42068915602) showed 4/4 per original and HLSL-derived roundtrip SPIR-V V/F typed Location+Component structural candidates with 0 missing or type-mismatched lanes, **75 aggregate Vertex-output scalar lanes but 44 aggregate Fragment-input scalar lanes**. This is a distinct reflection accounting measure; it does not establish which original DXBC semantic identities correspond to which SPIR-V Locations. An important next experiment should check original DXBC fragment **used/read-mask** bits separately from declared signature masks, rather than assuming the difference 75→44 is loss or guessing name/location mappings.

## Implementation, tests and failures

- New source-safe parser: [scripts/t3_original_921_dxbc_semantic_join.py](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/t3_original_921_dxbc_semantic_join.py). Uses original source selector and exact Pass pairing from `t3_original_top_shader_fourpass_translation.py`, uses original SHA owner fingerprint and a preexisting `t3_dxbc_signature_contract.py` (scheduled T3 credit preserved) to guard user register lane collisions. Does not alter that scheduled helper.
- `ISGN/OSGN` (24-byte records), `OSG5` (28), and `ISG1/OSG1` (32) layouts are based on the real vkd3d DXBC serializer/parser behavior and LLVM documentation, with bounded offsets, name termination, stream/min-precision, duplicate and malicious row rejection. Any unsupported layout fails to an INCONCLUSIVE status rather than declaring graphics fixed.
- New 21 synthetic tests in `tests/test_t3_original_921_dxbc_semantic_join.py` and six inherited scheduled tests. [CI42070932298](https://github.com/alwansan/raf/actions/runs/42070932298) **SUCCESS 27/27** (source-free). Genuine CI42071059741 also passed its security tests before SHA original extraction.
- The real input was triggered via an exact scoped file marker in `.github/t3-dxbc-semantic-requests/20261105T1701Z-T3-chat-original-dxbc-semantic-join-6d9f.json`, with three SHA-pinned source script blob IDs and marker-only commit guard. Successful CI source SHA `f0a02d6e634e3f93ea34f82343f51e5223f07ef0`.

## Limits and next action

Do not infer true shader-color restoration or remove vendor dummy assets: the original authored shader source is not recovered; these are compiled DXBC signatures. The mapping from true original VS/FS semantic names/index/register/used-mask to SPIR-V reflection Location/Component/Builtin and derived HLSL is still unknown. Only 4/33 original pairs and 8/41 source variants are in scope; no interpolation, pixel, Vulkan device, texture or sRGB data compared. No .meta/GUID, prefab, scene, original source assets, FMOD/Settings, controller/touch or save file was changed by T3.

**Next specific question:** Compare genuine **input used_mask vs declared mask** and its aggregate per-pass cardinality with the prior same-selected original SPIR-V Fragment Input 44 lanes. Investigate only if mismatch is proven, and keep private semantic name bytes in disposable CI runner. Mark RENDER-002 **OPEN / NOT_READY 0/3**, with no new APK or phone test.
