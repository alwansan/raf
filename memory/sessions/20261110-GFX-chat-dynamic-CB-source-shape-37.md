# GFX-LAB — 20261110-GFX-chat-dynamic-CB-source-shape-37
- session_id: 20261110-GFX-chat-dynamic-CB-source-shape-37; origin=chat; resumed_from=20261110-GFX-chat-final-joint-class-144-157-36; base_sha=8f56b4943d141b9bc379411771748f47a0965f3b; experiment_key=GFX-MULTI-063; issue_id=RENDER-002.
- resource_key: original-Shader48-source-CB-dynamic-operand-shape-and-SPV-authenticated-loaded-pointer-diagnostic.
- ONLY writable branch experiment/android-graphics-rootcause. main, feature/android-native-port, ZIP2 and T-Team read-only.
## Verified baseline
- GFX056–062 seven source-private SHA-pinned CI runs inspected exactly one original matched VS/FS pair per Pass-JOINT b/t/s+CB declaration and t/s sampled-use class: 157/157 source representative classes bounded CPU SPV structural tests passed. 524 genuine original source pair variants, 936 compiled source stage programs (not all individually translated); total **1190 source CB dynamic/extended operand uses** across 314 representative stage instances remain UNRESOLVED, not original Shader48 restored.
## New hypothesis and test scope
- GFX063 first independently parses and partitions all 1190 previously unhandled original dynamic/extended CB operands inside the same nine supported DXBC arithmetic opcode families. Cross-check legacy 1190 count source-private with two independent scans per source stage. Categories include dynamic b+vec register, dynamic b, vec-relative, vec immediate32+relative, vec immediate64+relative, extended-only modifier and unsupported shape. No original index values, shader IDs or CB size exported.
- Build *source-free* SPV dynamic UBO pointer provenance scanner from authenticated original b-register SPV Uniform global and reflected vec4 layout, through supported OpAccessChain/OpInBoundsAccessChain and OpCopyObject to actual OpLoad. Reject wrong struct member, wrong integer type, missing OpLoad, alias via OpPhi/OpSelect and source-dynamic-vs-SPV identity assumptions. One max-dynamic original exact pair per Pass (7 pairs /14 SPV stages) is translated for **new diagnostic**, not full repeat of GFX056–062. No source per-operand index expression equality implied, not all 1190 dynamically resolved by observing SPV reads.
- Source ZIP2 original SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385, ephemeral Actions runner, no source shader bytes/DXBC/SPV/registers/keywords or private pair signatures in repo/artifact, unconditional purge.
- Known GFX054 original Shader48 Unity Material property to true DXBC t/s/b and CB member semantics BLOCKED. No original GPU run on Android/Adreno and no APK or T-Team edits; originalShaderRestored=false, phase_closed=false.
## Files
- gfxlab/tools/multi_shader_original_dynamic_cb_taxonomy.py
- gfxlab/tests/test_multi_shader_original_dynamic_cb_taxonomy.py
- .github/workflows/gfxlab-multi063-source-dynamic-cb-taxonomy.yml
- experiments/20261110-GFX-chat-dynamic-CB-source-shape-37.json
- CI pending; update memory, restore, roadmap and count-only evidence only after verification.
