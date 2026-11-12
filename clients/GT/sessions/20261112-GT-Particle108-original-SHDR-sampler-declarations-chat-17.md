# GT — Chat-17: stage-local cbuffer conflict resolved in real Unity; source DXBC dcl_sampler census

- session_id: GT-20261112-CHAT-17-SHDR-SAMPLER
- origin: chat
- branch write-only: `feature/android-native-port`; read-only `zip2` SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- Preserve all original Raft Unity assets, shaders, Materials, scenes, `.meta` GUIDs and `.rgd`; no Git LFS; owner stopped T1–T5.

## Independent real Unity verification

[43233472806](https://github.com/alwansan/raf/actions/runs/43233472806) completed FAILURE at actual Unity 2021.3.45f2 Android Vulkan. It passed synthetic/preflight/staging and successfully applied private VS/FS cbuffer symbol separation to four Shader48 keyword variants. The previous GLSL linker error for two incompatible `cb1_0_m0` vector-array sizes **did not recur**. Private shader imported true, material pass count 1, four variants registered, Android Vulkan AssetBundle created (6225 bytes), but Unity validation status **INCONCLUSIVE**: still three unresolved sampler naming/binding errors for the vertex shader. These are the remaining compiler blocker; an AssetBundle file without Shader errors=0 is not proof of valid render or original Material links. No phone pixels, no game APK output.

Source-authenticated strict [43232633015](https://github.com/alwansan/raf/actions/runs/43232633015) remains `TRANSLATOR_SOURCE_SAMPLER_SLOT_MISSING`. Existing RDEF census [43228860357](https://github.com/alwansan/raf/actions/runs/43228860357) proves eight of eight original DXBC stages have no RDEF. The lack of RDEF is an original source fact, not a licence to guess samplers.

## New original SHDR/SHEX dcl_sampler parser

To obtain the original compiled sampler register declarations **without** RDEF, added:

- [source-only parser](../../scripts/gt_particle108_original_dxbc_sampler_decl.py) — commit [0ef59a6](https://github.com/alwansan/raf/commit/0ef59a684c27c558ea72c0aeb7f50813e0758ebb). Bounded DXBC chunk table, exact SHDR/SHEX program, sampler opcode #90 (D3D10/11 tokenized shader format), operand type sampler, immediate 1D index, explicit mode; rejects malformed/relative/untrusted operands. Uses SHA-pinned source originals and compares private sampler sets with Unity Shader `m_TextureParams.m_SamplerIndex` and translated HLSL registers. Outputs **counts only**; never original names, slots, GUIDs or HLSL.
- [strict synthetic tests](../../tests/test_gt_particle108_original_dxbc_sampler_decl.py) — commit [f59f23f](https://github.com/alwansan/raf/commit/f59f23f500e5bb3b8b810ffe958f0356bcf54e81). Covers legal declarations and source modes, absent RDEF, duplicate slots, malformed operands/container, missing/multiple source shader chunks, source/translated sampler schema.
- [real ZIP2 workflow integration](../../.github/workflows/raft-t3-particle108-private-shaderlab-variants.yml) — commit [79f3652](https://github.com/alwansan/raf/commit/79f365236185f5e62fdd37ef52c61a41fb03b8cd), before strict Shader48 source binding. Pinned source, eight real original DXBC stages, private translator HLSL, then sanitized counts.
- First integrated CI [43235259784](https://github.com/alwansan/raf/actions/runs/43235259784) was **QUEUED** when recorded. No parser PASS claimed until source-only real stage result is inspected.

## Current native and graphics boundaries

- Full native [43205543533](https://github.com/alwansan/raf/actions/runs/43205543533) still active in full Unity import/compile at immutable c8680938 snapshot (last inspected real asset import log around 2026-11-12T13:22Z); no signed APK/OBB/XAPK confirmed. Do not cancel or duplicate.
- Source texture arrays/material links (9/28/416) and 50 BC3 top mip slices separately verified in [43207734641](https://github.com/alwansan/raf/actions/runs/43207734641), but native full old snapshot does not contain every later strict combined gate.
- **770 custom Material docs remain Dummy** post-vendor restoration. Particle108 original Material GUID/pixel fidelity not proven. Current action is evidence recovery, not wholesale renderer restoration.

## Next

1. Check `43235259784` strict synthetic tests, then original DXBC `dcl_sampler` real stage and safe count report. If error, fix parser or source condition with narrow synthetic regression.
2. Determine whether source compiled sampler declarations differ from Unity serialized sampler slots; do not infer binding from translator ordinal. Use original source opcode and SPIR-V reflection for exact association if available. Keep shader source and private values out of public artifacts.
3. After original sampler identities proven, perform private real Unity Shader48 compile with **zero shader errors** and same-instance Material binding tests before integrating original Shader GUIDs into native production.
4. Preserve all previous color, mesh, texture, water and postFX progress. Wait for the active native full build's actual result and inspect earliest failure before rerunning.
