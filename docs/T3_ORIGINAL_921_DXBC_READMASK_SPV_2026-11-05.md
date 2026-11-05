# T3 — Genuine original DXBC PS input ReadWriteMask vs SPIR-V input lane count (2026-11-05)

**Issue**: RENDER-002 OPEN, NOT_READY, 0/3 immutable device reviews. **CI**: [42073397586](https://github.com/alwansan/raf/actions/runs/42073397586) genuine original **COMPLETED SUCCESS**, source-free [42073255841](https://github.com/alwansan/raf/actions/runs/42073255841) **59/59 PASS**. No game asset, Unity ShaderLab, source code or device pixel change; no claim of full visual repair.

## Reason for this precise experiment

Earlier authentic [T3 original DXBC semantic trial 42071059741](https://github.com/alwansan/raf/actions/runs/42071059741) proved **22/22** original selected Shader48 Vertex/Fragment SemanticName+Index linkage with 75 declared PS input component mask bits and no missing types/lane allocation. Separately, [T3 same-authentic-SPIR-V trial 42068915602](https://github.com/alwansan/raf/actions/runs/42068915602) found only **44** Fragment input scalar/vector components in both original SPIR-V and translated HLSL roundtrip. It could not be assumed whether the 31-lane difference was lost or simply unused inputs.

A DXBC signature has independent **Mask** (allocated components) and **ReadWriteMask** (actually read input channels). The serializer parses these distinctly; *output* signature write bits have different inversion semantics, so this study uses **input ISGN/ISG1 exclusively**, never applies output inversion. Reference: vkd3d DXBC signature parser in [Wine 10.0, dxbc.c](https://sources.debian.org/src/wine/10.0~repack-6/libs/vkd3d/libs/vkd3d-shader/dxbc.c/), and [vkd3d used-mask design](https://www.winehq.org/pipermail/wine-devel/2020-September/173948.html).

## Source lineage / immutable scope

- Pinned original ZIP2 provider commit: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- Genuine source SHA-verified **six** original scenes and **four** original Shader/Material owner files (269,007,288 bytes total), no LFS; original Shader48 identified by **921 Renderer Material-slot uses** in these six scenes.
- Four original normal Passes, one **exactly linked original Vertex/Fragment compiled DXBC pair per Pass** selected by identical player-bucket and permutation key: eight genuine D3D11 programs, **four original PS programs** privately compiled DXBC→SPIR-V→HLSL→SPIR-V in disposable runner storage.
- Source has **33** total matched original V/F variant pairs and eight unmatched original VS permutations; **29 of 33 matched pairs and all eight unmatched VS variants remain outside this probe**. Shader authored source and ShaderLab are not restored.
- CI [42073397586](https://github.com/alwansan/raf/actions/runs/42073397586) source commit `48f35ed6bfe64d829b1996beeab27d6202608019` checks exact source blob SHAs of four T3 scripts/tests, a sole explicitly authorized request-marker commit and stage-source SHA digests. No other original session was cancelled.

## Authentic observation (safe aggregate, four original PS stages)

| Metric | Verified value |
|---|---:|
| Original PS user semantic input records | 22 |
| Original PS system-value signature records (excluded) | 4 |
| Original DXBC PS allocated input component lanes (Mask) | **75** |
| Original DXBC PS actually read component lanes (ReadWriteMask) | **44** |
| Original declared-but-unread lanes | **31** |
| Original user semantic records wholly unread | **8** |
| Original user semantic records partially unread | **0** |
| Original PS read lanes lacking corresponding declared original VS semantic-output lane | **0** |
| Source SPIR-V fragment user input records / scalar lanes | **14 / 44** |
| HLSL roundtrip SPIR-V fragment user input records / scalar lanes | **14 / 44** |
| Individual original Passes with equal original PS read-lane count and source SPIR-V fragment input-lane count | **4/4** |
| Individual original Passes with equal read-lane count and HLSL roundtrip SPIR-V fragment input-lane count | **4/4** |
| Original vs roundtrip SPIR-V Fragment input-lane counts equal | **4/4** |
| Sum of per-Pass absolute difference: DXBC read-lane vs original SPIR-V / roundtrip SPIR-V | **0 / 0** |

**Confirmed narrow conclusion:** For these four exact compiled original Shader48 PS variants, the total **31-lane declared-versus-reflected gap is fully accounted for by 31 DXBC lanes not actually read**. The four Passes agree separately on **44 read lanes**, both before and after the existing HLSL roundtrip. The original user semantics split into **14 records with at least one channel read** and **eight records wholly unread**; source and roundtrip SPIR-V separately have **14** user input records. This is strong evidence **against** a missing-input-*count* explanation for the white graphics in the examined variants, and aligns with source dead-input elimination.

**Not confirmed:** Equal per-Pass cardinalities and even 14-vs-14 record counts do **not** prove which DXBC original SemanticName+Index/register/component corresponds to a given SPIR-V Location/Component. Original→derived generated names were already shown non-preserved (0/34 inputs, 0/29 outputs in [42062573338](https://github.com/alwansan/raf/actions/runs/42062573338)). Interpolation modes, stage IO component-value parity, resource CB/sampler/texture bindings, blend/depth/pass states, Unity ShaderLab, device/Adreno pixels and all unsampled original permutations remain unknown. No original shaders or Unity assets were patched.

## Implementation and test boundary

- [Independent genuine probe](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/t3_original_921_dxbc_readmask_spirv.py): consumes authentic previously SHA-pinned Shader48 exact sample V/F pairs; uses unchanged original DXBC signature parser, checks PixelShader user `used_mask & ~mask == 0`, original source semantic coverage and actual bytecode translation flags, then allows only sanitized scalar/vector SPIR-V reflection types and bounded Location/count. Does **not** expose private semantic names/code/hashes, and never declares name/Location mapping or visual proof.
- [21 synthetic negative/positive tests](https://github.com/alwansan/raf/blob/feature/android-native-port/tests/test_t3_original_921_dxbc_readmask_spirv.py) + 21 inherited genuine original semantic parser tests + 17 SPIR-V component tests = **59/59** PASS in [CI42073255841](https://github.com/alwansan/raf/actions/runs/42073255841). Earlier [CI42073175240](https://github.com/alwansan/raf/actions/runs/42073175240) had **3 synthetic-only failures** from a duplicated keyword argument in fake test helper; corrected at `522551776669108903001a14f116f4cc7833162a`; no real private original code run in that failed job.
- [Isolated SHA and explicit-request-gated workflow](https://github.com/alwansan/raf/blob/feature/android-native-port/.github/workflows/raft-t3-original-921-dxbc-readmask-spv.yml) never cancels T1/T2/T4/T5. Original code/bytecode/SPIR-V/HLSL stayed in runner temporary directories. The only uploaded safe aggregate artifact is `t3-921-original-PS-readmask-SPIRV-counts-42073397586`, ID `13436913300` (7-day retention).
- Safe result status: `ORIGINAL_921_DXBC_PS_READ_MASK_VS_SPIRV_INPUT_COUNTS_MEASURED`. Original shader authoring, device readiness and numeric pixel parity remain explicitly `false`.

## Next engineering discriminator

With original 75 allocated vs 44 used input lanes accounted for, **do not repeat this four-pair aggregate experiment unchanged**. The unresolved program-level question is **correspondence**, not total lanes: privately compare the exact original used SemanticName+Index, source component type and register/component read-mask against source SPIR-V numeric Location/Component/type mapping per original stage; fail closed on ambiguous reshuffling and generated names. Follow with actual ShaderLab Pass/ShaderImporter, keyword, CB/sampler/texture/sRGB and material bindings to identify white surfaces in native Unity/Adreno, and cover additional original variants if needed. Prioritize P0 WATER-001 and RENDER-002; **never mark game READY without actual device color and complete gameplay evidence**.
