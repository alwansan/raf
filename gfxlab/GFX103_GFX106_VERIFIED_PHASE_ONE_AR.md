# GFX-LAB — GFX103–GFX106 verified original shader and skinned-source milestones

Branch: experiment/android-graphics-rootcause. Source ZIP2 SHA: 15964ea8f246b6e076ce26b60931ee2e1a9a2385.

## Shader48 DXBC → SPIR-V → GLES310

- GFX103 CI42945815709 SUCCESS / 17 tests: 524 original exact Shader48 pairs, 472 distinct fragment stages; zero ordinary NoPerspective; 16 source system-interpreted NoPerspective declarations.
- GFX104 CI42946470013 SUCCESS / 14 tests: all 16 affected Fragment programs validated SPIR-V and emitted GLSL310 with one BuiltIn input each; no normal NoPerspective varyings.
- GFX105 CI42949456992 SUCCESS / 18 tests: source DXBC system NameToken=POSITION for 16/16, SPIR-V BuiltIn FragCoord for 16/16, GLSL gl_FragCoord for 16/16; no exceptions. The first failed CI was caused by our one-DWORD token parser bug and was fixed before the verified final run.
- System semantic candidate preservation is SOURCE-LEVEL evidence, not PC↔Adreno fragment pixel/value parity. Do not globally force native noperspective qualifiers on original Shader48.

## Original skinned Mesh renderer/bone hierarchy

- GFX106 CI42950536938 SUCCESS / 10 tests; source originals private, purge verified.
- Six original models: M03 non-skinned; five others have total 213 authentic bone PPtrs, all 213 resolve to typed Transform objects, all 213 local Transform values finite and 213 source bindposes match.
- M00: 3/3 bone Transform available; 1/3 ancestor chain reaches selected RootBone.
- M01: 100/100 links; all 100 reach selected RootBone (complete source hierarchy).
- M02: 8/8 links; all 8 reach selected RootBone (complete source hierarchy).
- M04: 100/100 links; all 100 reach selected RootBone (complete source hierarchy).
- M05: 2/2 links; 1/2 reaches selected RootBone.
- M01/M04 shared Mesh each has 6 renderer candidates; correct selected GameObject source identity disambiguates to exactly one. M00/M05 partial RootBone ancestry does NOT imply bones are lost.
- This does NOT establish reconstructed Android rig pose, original animations or GPU skinning.

## Immediate next gate (GFX107)

Source-private original indexed Mesh/vertex streams and bone weights/indices/bindposes, correct Transform hierarchy and renderer root coordinate space, CPU rest-pose skinning, then Android proof with original material/normal/Shader48 shader and PC↔Adreno captured pixel comparison. Never weld original skinned vertices based only on OBJ geometric coincidence.

Truth flags: originalShaderRestored=false, originalAnimationRestored=false, original_rig_restored=false, pcAdrenoPixelParityVerified=false, phase_closed=false.

Evidence: gfxlab/evidence/20261111_gfx103_original_siv_split_safe.json, gfxlab/evidence/20261111_gfx104_original_spirv_siv_safe.json, gfxlab/evidence/20261111_gfx105_original_siv_fragcoord_safe.json, gfxlab/evidence/20261111_gfx106_original_rig_hierarchy_safe.json.

Actions: https://github.com/alwansan/raf/actions/runs/42949456992 and https://github.com/alwansan/raf/actions/runs/42950536938
