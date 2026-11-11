# 20261111-GFX-chat-owner-gfx102-native-noperspective-71 — GFX102 verified native NoPerspective, GFX103 original Shader48 source gate
role=GFX-LAB; origin=chat; branch=experiment/android-graphics-rootcause; resumed_from=20261111-GFX-chat-gfx101-owner-adreno-102-matrix-70.

## GFX102 actual owner Android evidence
Owner ZIP SHA256: 82fa4235ec6e4a88e8d02fd89cb4077fa228dd8c617cb697503c3137dfa44ff5 and 858d6bd354b17fdfdf6f8f2c6f3930099bce015d36c206b2f990f20a37a58a29. Both ZIP CRC pass; 8 entries each, 5 PNGs each valid with image decoder and metadata SHA256. Both contain identical summaries and 25 identical event logs, i.e., may be two exports of one GPU run, not necessarily independent experiments. Private raw data NOT committed.
Owner Adreno 730 GLES3.2 GLSL ES3.20 advertises GL_NV_shader_noperspective_interpolation among 104 extensions. Smooth, Flat, AffineEmulated controls compile/link/readback GPU PASS. NativeNoPerspectiveES300 VS/FS compile FAILED 'noperspective' reserved word. NativeNoPerspectiveES310 AND NativeNoPerspectiveES320 VS/FS compile/link/readback GPU PASS; both native outputs exactly match the entire raw RGBA pixels and PNG SHA of affine emulation, not just 3 sampled points. Raw SHA256 ee7ceeaf02c698f4c805caea6d8ffad23913a86c25aec794429fd0cf174456a3; native CPU affine MAD 0.001141990429516256 vs CPU smooth MAD 0.16301616768295013. Smooth reference MAD 0.0010914190494416291.
Original-free native GPU qualifier experiment is VERIFIED on one phone/micro-scene. Shader48 runtime/material/rig/PC pixels NOT verified. Safe aggregate: gfxlab/evidence/20261111_gfx102_owner_adreno_native_noperspective_safe.json.

## GFX103 original interpolation source guard, no APK
Earlier GFX039 census counted 16 source linear_noperspective declarations across 655 distinct PS programs, and separately 16 system-interpreted declarations, but their overlap was UNKNOWN. Need cross-tabulate DCL_INPUT_PS opcode98 ordinary versus DCL_INPUT_PS_SIV opcode100 system-interpreted (SV_Position/gl_FragCoord candidate), not blindly convert SIV to an ordinary varying.
gfxlab/tools/gfx103_source_interpolation_gate.py: fail-closed DXBC SHDR token parser, reject lost ordinary noperspective in generated GLSL, explicit NV extension require on ES310/320, reject ES300, mark SIV builtin semantics unverified.
gfxlab/tools/gfx103_source_interpolation_census.py: scan all 524 exact original pairs across seven passes from SHA-pinned ZIP2, count ordinary/SIV per pair and distinct original PS program; publish safe aggregate only.
Tests: gfxlab/tests/test_gfx103_source_interpolation_gate.py (11 synthetic source-free tests), gfxlab/tests/test_gfx103_source_interpolation_census.py (4 synthetic pair/count/negative tests). Workflow: .github/workflows/gfxlab-multi103-source-interpolation-classes.yml. Original ZIP2 source fetched at 15964ea8f246b6e076ce26b60931ee2e1a9a2385 and purged after workflow, no original source bytes or shader data uploaded; no full game or T-team branch changes.
Do NOT claim GFX103 CI tests passed or source ordinary/SIV counts before independent Actions result. Source-code/CI workflow committed; terminal run and safe aggregate PENDING.

## Follow-up priorities
1. Verify GFX103 source-private workflow success and exact 524-pair real ordinary/SIV counts.
2. For ordinary source NoPerspective verify original DXBC declaration -> SPIR-V NoPerspective decoration -> GLSL310 required NV extension -> linked source stage -> actual Adreno pixels.
3. For SIV source system-interpreted inputs independently verify builtin mapping, not ordinary-varying equivalence.
4. Continue material-to-register and CB payload, texture/normal, rig/skinning, and PC↔Adreno pixels; phase one remains OPEN.
Truth flags: originalShaderRestored=false; originalAnimationRestored=false; pcAdrenoPixelParityVerified=false; phase_closed=false.
