# T2 Foam — original two-pass VS/PS paired compilation proof (2026-11-05)

Source-original, not Unity or Android device acceptance. Worker T2, issue WATER-001.

## Authenticated inputs and design

- Pinned original `zip2` commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; reassembled only `Raft_Data/sharedassets0.assets` (115,978,112 bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`) without LFS.
- Original serialized Shader PathID 2420, raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`. Reuse [B20's private original-stage packet](B20_FOAM_PRIVATE_PACKET_2026-11-04.md) and [B25's authentic pass state](B25_ORIGINAL_FOAM_RENDER_STATE_2026-11-04.md): **4 real translated programs** (VS,PS for each of two passes), **2 actual 247-byte render states**.
- New `scripts/t2_foam_original_pair_compile.py` requires the exact authenticated B20 manifest, four original DXBC source SHA pins, per-stage HLSL SHA/byte commitments, original two pass state SHA, physical non-symlink files and scratch privacy. Builds each pass's **one private HLSL source** using the existing stage-select preprocessor arrangement (`scripts/w1_depth_shaderlab.py:stage_body`) and recompiles *both* stage configurations with `glslangValidator -V` and `spirv-val --target-env vulkan1.1`. Private HLSL and SPIR-V never leave temporary CI scratch; no source code, original materials, .meta or original game bytes published.

## Verified result

- [Final original CI 42121817207](https://github.com/alwansan/raf/actions/runs/42121817207) **COMPLETED SUCCESS**, job `127575852396`, source commit [ff938dbe](https://github.com/alwansan/raf/commit/ff938dbe4a0db6e6dac5d2808c944ee882415cf7).
- All **10/10** source-free negative controls passed; original owner and B20 four program/two state hashes authenticated. Genuine private staging produced **2/2 joint VS+PS pass sources** and validated **4/4 compiled stage variants** through SPIR-V Vulkan 1.1. Stage order `(pass0 VS,pass0 PS,pass1 VS,pass1 PS)` verified.
- Previous [42121569920](https://github.com/alwansan/raf/actions/runs/42121569920) and [42121619881](https://github.com/alwansan/raf/actions/runs/42121619881) failed on source-only path guards: first the shared `RUNNER_TEMP` nested original packet, then the JSON safe report under `RUNNER_TEMP`. Both stopped **before** the actual pair stage compilation, and were fixed without weakening SHA checks. Only the last CI establishes stage-pair compilation success.
- Verified safe log: `status=original_foam_two_pairs_compiled_vulkan11`, `original_passes=2`, `compiled_stage_pairs=2`, `compiled_stage_variants=4`, `stage_order_exact=true`, `reused_original_247_byte_render_states=true`.

## Boundary / next engineering

The source-authentic joint per-pass compilation is an important **ShaderLab integration prerequisite**, not an installed ShaderLab: the original Shader has **two serialized authored properties**, including only one texture property; other original four sampled names are runtime-set `Material.SetTexture` inputs rather than fictitious authored properties. No `Properties` block was fabricated, no CB0 alias synthesized, and no runtime constant-buffer/texture/sampler upload or original pixel-equivalence proof was claimed. In particular `shaderlab_constructed_or_installed=false`, `unity_2021_import_or_android_pixels_verified=false`.

Next: source-authentic strict serializer for both original authored properties, shader pass metadata and exact source-driven CB/resource mapping, then private two-pass ShaderLab candidate and coordinated Unity/Adreno compile with T1 FFT and T5 integration. Do not turn source-only compilation into water-ready or cancel other teams' jobs.

**WATER-001 OPEN, project NOT_READY 0/3.** Working sound and Settings untouched, touchscreen layout deferred.
