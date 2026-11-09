# T3: authenticated original smoke-name ParticleSystemRenderer → Material21 → Shader48 rank bridge
**Date:** 2026-11-09 UTC · **issue:** RENDER-002 OPEN · **worker:** T3 chat session `20261109T0150Z-T3-chat-particle-emitter-3p7k`

## Why this experiment was needed
The user observed a square smoke/fire-like effect and white surfaces in [original Raft 5 November phone screenshots](DEVICE_FEEDBACK_42058825739_AR.md). T3 earlier established a heavily used original `ParticleSystemRenderer` Shader48 at 108 Material slots and 54 renderer objects. The 108-use original graph's 5 Material21s, 3 Texture2D target pointers, 10 TexEnv slots, 15 colors and 145 Float32 scalar slots matched one authentic AssetRipper export ([run 42243130856](https://github.com/alwansan/raf/actions/runs/42243130856)), but the selected exported ShaderLab still carried `DummyShaderTextExporter` ([run 42223071341](https://github.com/alwansan/raf/actions/runs/42223071341)). **Those facts never proved the 108-use Shader48 is the user's square-smoke emitter.**

## New original graph and exact source provenance
- Private original ZIP2 source SHA: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, six SHA256-pinned original Unity scenes and four independently SHA-verified shader/material owners (269,007,288 assembled owner bytes, no LFS).
- [Scoped original checker](../scripts/t3_original_particle_emitter_semantics.py) links each original `ParticleSystemRenderer.m_Materials` to the private original Material21 source identity and its already authenticated Shader48 pointer; independently joins `m_GameObject` to the actual original scene GameObject class1 and its `m_Name`. All original source identities remain **private inside Actions**.
- Fixed categories are purely generic *name hints*: smoke/steam/dust/ash, fire/flame/ember/spark, water/foam/splash/bubble. The filter supports CamelCase or punctuation. No object name, original path, GUID/PathID, proprietary shader/material code or image bytes are uploaded. Name-match absence cannot prove that a shader renders no smoke.
- **[Original hosted CI 42548907189](https://github.com/alwansan/raf/actions/runs/42548907189) SUCCESS**: source-free negative controls, original six scenes/four owners, real graph and GameObject joins, bounded-safe aggregate artifact [13644781433](https://github.com/alwansan/raf/actions/runs/42548907189/artifacts/13644781433).
- **[Extended original hosted CI 42549246777](https://github.com/alwansan/raf/actions/runs/42549246777) SUCCESS**: same immutable source scope, added private Shader48 rank join and validated total **215 Shader48 Material slots** from source; safe rank-only aggregate artifact. No new Android/Unity build.
- **[CI 42549491342](https://github.com/alwansan/raf/actions/runs/42549491342) SUCCESS**: lightweight source-free additional negative controls for equal 34-use Shader ranks, unknown source pointers, slot overflow and private identity non-disclosure. No second heavy export or original source used in this test.

## Measured real original results (counts not names)
| Source scope | ParticleSystemRenderer objects | GameObject names resolved | Fire-like name matches | Smoke-like name matches | Water-like |
|---|---:|---:|---:|---:|---:|
| Unique original 108-use Shader48 | 54 | 54 | 25 | **0** | 0 |
| All other 6-scene ParticleSystemRenderers | 56 | 56 | 17 | **17** | 0 |

**Critical actual source-identity distinction (not a guess from equal ranks):**
- All **17 smoke-like GameObject renderers** in the six original scenes contribute **34 Material slots** to **one and the same private original Shader48** whose total original ParticleSystemRenderer Material-slot use rank is **34**.
- **25 fire-like renderers** contribute 50 slots to the distinct original **108-slot** Shader48; a further **17 fire-like renderers** contribute 34 slots to **another source-authenticated Shader48**, also ranked **34**.
- The two **34-use Shader48s are distinct in the private original source graph**. The public result deliberately publishes only safe rank/count tuples; equal rank alone must never be used to conflate the fire and smoke shader.
- No water-like names matched in this selected six-scene set. This says nothing about the rest of the game, the water system or unnamed emitter effects.

## Interpretation / what cannot be claimed
The leading 108-use original Shader48 is more clearly associated with **fire-like** GameObject names in this sample. The actual original smoke-name association instead singles out a **different anonymous 34-slot Shader48**, a substantially narrower source candidate. However name hints are not actual on-phone emitter/Shader ID evidence. The selected six scenes are not the whole game; ParticleSystems may be nested or dynamically instantiated. No original 34-smoke Shader48 translated/compiled/program variant has been recovered or matched to Android pixels. No correct alpha transparency, blend, material tint/texture, original smoke/white hand remediation, or Unity smoke effect in a running Android APK is established.

The earlier real CL six R3 PNG colors ([CI42547145230](https://github.com/alwansan/raf/actions/runs/42547145230)) are **synthetic GLES lab screenshots**, not original Unity Raft particles. Do not use their captured nonblack pixels as proof that in-game smoke is restored.

## Next exact engineering step
With the original source-only **34-use smoke-labeled Shader48 identity kept private in a SHA-pinned runner**, inspect its original `m_ParsedForm` Shader48 pass state and keyword/program/texture sampler references, then compare that same original Shader48 to its real bounded postvendor exported ShaderLab and Android native import. Classify blend/alpha and any dummy/lost program **without guessing a replacement or publishing proprietary source**. If the 34-use shader is actually dummy or lacks an alpha texture in the current native build, produce a reproducible targeted shader/texture repair candidate, run source and Unity compile checks, and require the user's actual Raft frame to verify the specific square smoke. Do not replace the 108-use fire shader as a guessed smoke fix.

This scope does not change original Raft assets or GUIDs, audio, save files, mouse, Android test pack, shared mini APK or full XAPK. **RENDER-002 remains OPEN, full native game still NOT_READY 0/3.**
