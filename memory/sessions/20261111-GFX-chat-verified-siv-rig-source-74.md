# 20261111-GFX-chat-verified-siv-rig-source-74 — original Shader48 system semantic closure candidate + authentic source bone hierarchy

role=GFX-LAB; origin=chat; write-branch=experiment/android-graphics-rootcause; resumed_from=20261111-GFX-chat-source-siv-fragcoord-73; immutable ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385.

## Actual CI verification (not guessed)
GitHub REST workflow runs plus each actual job log and artifact checked through the connected GitHub app:
- GFX103 run 42945815709: SUCCESS, 17 tests, artifact 13822676727, private source purge verified.
- GFX104 run 42946470013: SUCCESS, 14 tests, artifact 13822842279, purge verified.
- GFX105 final run 42949456992: SUCCESS, 18 tests, artifact 13824207690, purge verified. Initial failure 42949270886 was our scanner bug disallowing single-token DXBC instructions; fixed and re-tested.
- GFX106 final run 42950536938: SUCCESS, 10 tests, artifact 13825061622, purge verified. Initial run found shared Mesh ambiguous Renderers; exact selected source GameObject disambiguation solves M01/M04; support for signed Unity PathID retained.

## Original Shader48 interpolation identity
GFX103 counted 524 exact original pairs, ordinary NoPerspective =0, system interpreted SIV NoPerspective =16. GFX104 proved 16 valid SPIR-V translated fragment stages with 16 builtin inputs and 16 GLES310 emissions. GFX105 parsed all 16 DXBC SIV NameToken=POSITION and actual SPIR-V BuiltIn FragCoord and generated GLSL gl_FragCoord matches each. Zero unresolved categories. This is typed semantic candidate parity, NOT value equivalence of SV_Position vs GLES gl_FragCoord, not PC/Adreno pixels or original runtime material/CB identity. Source-safe evidence: gfxlab/evidence/20261111_gfx103_original_siv_split_safe.json, gfxlab/evidence/20261111_gfx104_original_spirv_siv_safe.json, gfxlab/evidence/20261111_gfx105_original_siv_fragcoord_safe.json.

## Original six-mesh rig source readiness
Source authenticated 6 models, of which 5 skinned, 1 static. 213/213 source bone pointers resolve to typed Transform, 213/213 have finite local transforms, and 213 bindposes match original Renderer bone counts. M01 and M04 each share their Mesh among 6 candidate renderers; exact GameObject selection now proves unique original renderer. M01 100/100, M02 8/8, M04 100/100 bone ancestry reaches selected RootBone. M00 1/3 and M05 1/2 RootBone ancestry partial, but all original Transform references resolve; do not report missing bones or corrupted skeleton. Source-safe evidence: gfxlab/evidence/20261111_gfx106_original_rig_hierarchy_safe.json.

## Decisions and next engineering
Native noperspective under GLES310 is device-proven only on synthetic GFX102; original Shader48 ordinary input NoPerspective is absent in the authentic source. Do NOT globally replace shader qualifiers. GFX107 next should preserve original indexed vertices/weights/indices/bindposes, reconstruct CPU rest pose using exact PPtr Transform parent graph, avoid fake welded OBJ skinning, and only then test authentic Unity/Adreno renderer. G8 Material t/s/CB, shader states, original normal sampling and PC↔Adreno pixel parity remain OPEN.

Flags: originalShaderRestored=false; originalAnimationRestored=false; original_rig_restored=false; pcAdrenoPixelParityVerified=false; phase_closed=false.

All writes this chat only experiment/android-graphics-rootcause; T1-T5, main, feature/android-native-port, zip2 unchanged.
