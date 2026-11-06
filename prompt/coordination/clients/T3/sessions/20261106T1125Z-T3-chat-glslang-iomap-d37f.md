# T3 chat — authentic Particle108 glslang HLSL IO options test

- session_id: `20261106T1125Z-T3-chat-glslang-iomap-d37f`; origin: `chat`; status: `completed` **source-level experiment only**; RENDER-002 remains **OPEN / NOT_READY**.
- base_sha: `b34c69cd52c9369cf42766a477d90ea973288757`.
- resumed_from: T3 chat `20261106T1108Z-T3-chat-hlsl-width-origin-73ac`, T3 scheduled `20261106T1026Z-T3-scheduled-91ac`. Own current work registered active before source writes; T3 scheduled identity-gate files, T1 FFT, T2 Foam, T4 input/world, and T5 integration remain untouched.
- scope: isolated 4-pair original Particle108 `glslangValidator` output Location mapping options in ephemeral GitHub Actions, not Unity gameplay assets.
- workflow: `.github/workflows/raft-t3-particle108-glslang-io-map.yml`
- original run: https://github.com/alwansan/raf/actions/runs/42210538214 — job `127867804070` **completed SUCCESS**.
- original immutable ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; four SHA-pinned original owners and six SHA-pinned original scenes verified in CI.

## New code and tests

Registered [session work](../../../work/RENDER-002/20261106T1125Z-T3-chat-glslang-iomap-d37f.json) before edits; added `scripts/t3_particle108_glslang_io_map_experiment.py` (commit `6719010af3d28f165d916a866c58b47aa09bec97`), `tests/test_t3_particle108_glslang_io_map_experiment.py` (commit `dff3d607b694a0c6fb6ecad7c24a6e4eb2e243d8`), and dedicated `.github/workflows/raft-t3-particle108-glslang-io-map.yml` (commit `991c0040fd58717062fb12dcad56da65720a0760`). **8/8 source-free tests pass**. Tool allows only known compiler flag tuples, keeps HLSL, source DXBC/SPIR-V and names private, requires per-stage `spirv-val --target-env vulkan1.1` and exact owner/scene SHA before counting pairs. No original Unity shader, material, texture, mesh, .meta, GUID, input, world, .rgd, audio, Settings, water/FFT, APK/OBB/XAPK modifications.

## SHA-authentic result

Previous source/HLSL baseline [42209509708](https://github.com/alwansan/raf/actions/runs/42209509708) established generated HLSL original Vertex/Fragment semantics **4/4 stage pairs compatible**, 14 Fragment user inputs matched 16 Vertex user outputs with 0 missing names/types; original SPIR-V **4/4**; separately rebuilt SPIR-V **2/4**. The apparent narrowing at same *numeric* Location was NOT original HLSL field-width loss because all 16 source→HLSL exact-name/types match; source/HLSL/roundtrip output type multisets agree 4/4.

New [42210538214](https://github.com/alwansan/raf/actions/runs/42210538214) original four-pair private HLSL recompile:
| glslang flag set | valid Vulkan SPIR-V stages | VSFS pairs linked | fragment missing Location | fragment type mismatch at present Location |
|---|---:|---:|---:|---:|
| baseline | 8/8 | 2/4 | 0 | 2 |
| `--hlsl-iomap` | 8/8 | 2/4 | 0 | 2 |
| `--auto-map-locations` | 8/8 | 2/4 | 0 | 2 |
| both | 8/8 | 2/4 | 0 | 2 |

**These compiler-only flags do not resolve the observed 2 stage-interface mismatches**, despite producing 8/8 Vulkan-valid modules each. No game shader patch authorized by this data. Source authored semantic→roundtrip numeric Location identity and Adreno pixels remain unproven.

## Next handoff

Test paired generated HLSL VS+FS link with glslang stage-link/semantic-aware pipeline (check exact tool flag support), or build an unambiguous direct recovered-HLSL semantic to compiled SPIR-V Location crosswalk within private CI. Only then consider disposable corrected SPIR-V and validate 4/4 stage contracts and spirv-val. Avoid guessing numeric original semantic identity, editing original Unity shaders blindly, fake readiness flags, and confusing source translation with APK/device acceptance.
