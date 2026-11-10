# GFX-LAB 20261110-GFX-chat-authenticated-cb-byte-address-27
- session_id 20261110-GFX-chat-authenticated-cb-byte-address-27; origin=chat; resumed_from=20261110-GFX-chat-ubo-global-symbol-provenance-26
- base_sha e2693873dec5709b77403fed16be2307cc24e454; writable only experiment/android-graphics-rootcause; original ZIP2 pinned 15964ea8f246b6e076ce26b60931ee2e1a9a2385.
- experiment_key GFX-MULTI-053, issue RENDER-002, no T-team changes, no APK or heavy Unity.
## Baseline
- GFX052 CI42847513772: 66/66 original DXBC b-register source names linked via actual SPV Uniform global OpName, binding and byte size for 14 representative Shader48 stages, 356 synthetic tests.
- GFX051 CI42845677322: 208/208 static original source b#/vec4 index locations (nine covered arithmetic opcodes only) found by provisional SPV numeric binding, 27 dynamic/extended original operands, 20 SPV candidates outside covered source subset.
## Hypothesis / checks
- Starting from original source dcl_constant_buffer and authenticated real SPV Uniform global, require independent reflected UBO type contains exactly one vec4 array with offset=0, array_stride=16, literal array extent=original vec4 declaration and block_size=16*extent. Trace only actual OpAccessChain [literal struct member 0, literal vec index] and OpLoad from same pointer to calculate byte address, and compare privately with original source b#/vec index*16 (source subset only).
- Fail closed on missing array metadata, wrong member types, multiple members, nonzero offset, non16 stride, dynamic and out-of-range indices, mismatched source register identity, missing actual OpLoad, original opcode coverage gaps. Source property names, CB offset values, IDs, DXBC/SPV binaries never exported.
## Files
- gfxlab/tools/multi_shader_original_cb_byte_addresses.py
- gfxlab/tests/test_multi_shader_original_cb_byte_addresses.py
- .github/workflows/gfxlab-multi053-source-cb-byte-address.yml
- CI pending. originalShaderRestored=false. No Material property semantics, original Android GPU shader, 524 full variant coverage, or PC-Adreno pixel parity implied.
