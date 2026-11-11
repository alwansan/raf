# 20261111-GFX-chat-source-siv-fragcoord-73 | GFX105 authentic shader system semantic witness

role=GFX-LAB; origin=chat; write branch=experiment/android-graphics-rootcause; resumed_from=20261111-GFX-chat-original-spirv-interpolation-72.

## Source and actual GitHub Actions verified
Original source pinned immutable ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, no shader/game bytes publicly copied. Retrieved actual run list and job logs through connected GitHub, not guessed.

| Gate | Real run | terminal | tests | safe artifact | source purged |
|---|---|---|---|---|---|
| GFX103 original ordinary versus SIV DXBC | 42945815709 | SUCCESS | 17 | 13822676727 | YES |
| GFX104 private original NP→SPIR-V→GLES310 | 42946470013 | SUCCESS | 14 | 13822842279 | YES |
| GFX105 original POSITION NameToken→SPIR-V FragCoord→GLSL | 42949456992 | SUCCESS | 18 | 13824207690 | YES |

Earlier GFX105 run 42949270886 **FAILED** on GFX105 own stricter-than-spec token parser: valid one-DWORD DXBC instructions were rejected by mistaken `length<2` guard. Fixed to `length<1` with special `DCL_INPUT_PS_SIV` NameToken minimum4 retained, and added a synthetic one-DWORD preceding SIV regression; successful final commit `d4c87f3dabead92fc97c6a2350b4398e995886d7`. Never attribute initial failure to original shader. Verified final run includes private ZIP2 checkout, original stage audit and purge step.

## Real source result, not synthetic
GFX103: 524 exact authentic Shader48 stage pairs across 7 runtime passes, 472 distinct fragment stages in these pairs. Ordinary DCL_INPUT_PS modes: linear and constant; ordinary noperspective **0**. System interpreted DCL_INPUT_PS_SIV `linear_noperspective` **16** distinct source fragment stages; no other native NP.

GFX104: all 16 affected original fragment stages validated SPIR-V, all 16 emitted GLES310; SPIR-V input BuiltIn count16, ordinary NoPerspective0 and no errors. Source mapping still unverified by counts alone.

GFX105: parsed the original DXBC last SIV NameToken under official token format; **16/16 system `POSITION` (enum1), 0 other**. Each translated SPIR-V fragment contains an Input `BuiltIn FragCoord` (SPIR-V builtin value15), and emitted GLSL ES310 references `gl_FragCoord`: **16/16 source-system-name→SPIRV→GLSL candidates**, 0 unresolved and all 18 synthetic tests PASS. Safe saved evidence `gfxlab/evidence/20261111_gfx105_original_siv_fragcoord_safe.json`, alongside `gfxlab/evidence/20261111_gfx103_original_siv_split_safe.json` and `gfxlab/evidence/20261111_gfx104_original_spirv_siv_safe.json`.

**Engineering implication:** original `NoPerspective` source declarations are system `POSITION` and translated as fragment coordinate builtins, not ordinary VS→FS varying qualifiers. Do NOT globally change source Shader48 GLSL to native NV `noperspective`. Owner GFX102 true device native 310/320 is valid but supplemental, not necessary for these system-value declarations.

## Limits and next phase-one work
The three-way semantic mapping is a **source-level candidate identity** based on DXBC NameToken, SPIR-V BuiltIn and GLSL `gl_FragCoord`; it does NOT prove D3D versus GLES coordinate values, render-target origin, depth conventions, perspective reciprocal W, original material/CB register mapping, original skinned hierarchy, or source shader pixels. `originalShaderRestored=false`, `originalAnimationRestored=false`, `phase_closed=false`.

Next focus on GPU original-material pixel parity and rig/hierarchy instead of more synthetic noperspective testing. If pixel parity requires a new phone APK, use existing GFX model probe architecture with auto ZIP export. No owner intervention needed for CPU-only source gates.
