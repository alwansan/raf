# GFX-LAB 20261110-GFX-chat-independent-dxbc-sample-pairs-21
- session_id: `20261110-GFX-chat-independent-dxbc-sample-pairs-21`, origin=`chat`, resumed_from=`20261110-GFX-chat-sampled-image-register-pairs-20`
- base_sha=`af352c61c8aefa6375927b56bb4bd3d515aa182d`; only writable `experiment/android-graphics-rootcause`
- experiment_key=`GFX-MULTI-047`; issue=`RENDER-002`; resource_key=`original-DXBC-SHDR-source-sample-use`
- Original source ZIP2 pinned `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- Previous GFX046 [CI42835954397](https://github.com/alwansan/raf/actions/runs/42835954397) validated compiler-lowered 37/37 SPIR-V sampled uses; did NOT independently decode original DXBC sample instructions.
## Design / controls
- Independent, bounded Microsoft tokenized SHDR `sample/sample_c/sample_l/sample_d/sample_b/gather4` source-opcode operand decoder. Parse destination, source coords, texture and sampler operands; require original SHDR t/s declaration membership; relative/extended resource operands remain UNKNOWN. Safe private pair multisets checked against same keyword+tier vkd3d SPIR-V OpName + OpSampledImage/OpImageSample* graph.
- Negative controls: original source declaration mismatch, dynamic index, truncated instruction, wrong source type, instruction operand count, duplicate SPIR-V IDs, multiplicity vs per-pass distinct counts. Never export original register IDs, names, pair identities, code, resource bytes.
- Microsoft public opcode reference https://github.com/microsoft/DirectX-Headers/blob/main/include/directx/D3D12TokenizedProgramFormat.hpp ; vkd3d public operand layout https://sources.debian.org/src/wine/10.0~repack-12/libs/vkd3d/libs/vkd3d-shader/tpf.c .
- Exactly seven representative matched pass pairs / fourteen stages, not all 524 variants. Original source/translated shader bytes private runner only.
- CI pending. Do not claim positive parity until full original source + translated stages and purge pass.
## Limitations
- Even if source opcode t/s matches translated program t/s, original `Material property → t/s/b#` mapping and CB byte offsets remain blocked by stripped RDEF and absent reflection; no Android original Shader48 runtime, no real PC-Adreno pixels, no game APK. `originalShaderRestored=false`.

## Verified final result
- CI [42838485544](https://github.com/alwansan/raf/actions/runs/42838485544) SUCCESS; source-free tests **314 passed**; private source purge PASS.
- 7 original Shader48 Passes, 14 authentic source stages, original DXBC direct opcode inspection vs translated SPIR-V internal pair multisets: **14/14 stage comparisons match**, **37/37 sample/gather operations exactly paired**, source unresolved 0, translated unresolved 0.
- Per-public-Pass original source and SPV fragment counts: [10,4,2,6] and [10,4,1]; source vertex sample operations all 0.
- [Safe count-only artifact 13774542864](https://github.com/alwansan/raf/actions/runs/42838485544/artifacts/13774542864), expires 2026-11-17T14:53:12Z. Private original source/registers/shader bytes not published.
- Evidence level `ORIGINAL_SOURCE_WITH_INDEPENDENT_DXBC_INSTRUCTION_TO_TRANSLATED_SPIRV_CPU_PAIR`, not Android GPU. No Material property→DX11 t/s/CB or CB layout offsets.
- Next suggested GFX048: source-private full 524-variant sampling coverage census/invariance check before GPU pipeline. Original Shader48 restoration FALSE, G7–G12 BLOCKED. No APK, no T-team modifications.
