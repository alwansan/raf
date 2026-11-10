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
