# T3 — authentic original Renderer-class impact of high-use Shader48 (2026-11-05)

**Scope:** source-only, SHA-authenticated original six PC Raft Unity scenes + four original Material/Shader provider assets, pinned ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. No game source/data bytes, names, PathIDs or private shader GUIDs appear here. Work session `20261105T210656Z-T3-chat-renderer-class921-7d62` (origin chat).

## Verified original result

[GitHub Actions 42109994654](https://github.com/alwansan/raf/actions/runs/42109994654), immutable source commit `3342cf6b1c996c2bcf7b7bf4d6caae23e3b7c29e`, **SUCCESS**. Source-free unit controls passed **15/15 T3 + 22/22 B03**. Original ZIP2 staging and SHA checks passed: six scenes and four owner files (reconstructed owner bytes **269,007,288**). The real original UnityPy/serialized graph gave:

| Original type | Material slots of all renderers | Verified typed Shader48 slots |
|---|---:|---:|
| MeshRenderer | 1,374 | 1,372 |
| SkinnedMeshRenderer | 46 | 46 |
| ParticleSystemRenderer | 219 | 215 |
| **Total** | **1,639** | **1,633** |

Four material slots were null across the original scenes; two non-null slots reference a Shader outside the four authenticated owner scope. These are serialized source slots, not GPU draw calls.

**One uniquely highest-use original Shader48 accounts for exactly 921 true Renderer Material slots:** 914 MeshRenderer slots and 7 SkinnedMeshRenderer slots. These correspond to 914 and 7 distinct Renderer objects respectively. **Zero** of that Shader's original slots is a ParticleSystemRenderer. This is a source-only classification; its real post-native GUID/ShaderLab output after all restorers and its Android pixels remain unknown. Earlier authenticated experiment established that this source Shader48 contains four original passes, and another *bounded three-vendor* actual export still yielded Dummy; neither result proves its status in a full native restorer run.

**Independent effects scope:** 215 original ParticleSystemRenderer Material slots reference typed Shader48 objects **other** than the source top-921 shader. A particle's Shader reference alone does not prove it rendered, fired an emitter, caused a white rectangle, or failed alpha blending. Prioritize the remaining particle-Shader identities in a PRIVATE original source graph, but publish only grouped class/rank counts. Determine actual textures/alpha/Blend/pass/keyword and Android runtime binding before editing source. The current owner device report shows white raft/hand and square effects, but has not attached them to these original shader identities.

## Code/test lineage

- [Read-only original source class-count extension](https://github.com/alwansan/raf/commit/6a07848324991973598a45378dd85ff055d279f3) in `scripts/t3_original_renderer_shader_impact.py`: counts slots and distinct Renderer objects separately; only public Unity Renderer class labels emitted, original shader IDs remain private.
- [Three adversarial fixtures](https://github.com/alwansan/raf/commit/7fb7889b838b71f330dc95c5a7f7c2d95d5167dc) in `tests/test_t3_original_renderer_shader_impact.py`: duplicated material slots on one Renderer, tied top original shader refusing arbitrary winner, source-name/identity leak check.
- [Bounded genuine original source workflow](https://github.com/alwansan/raf/commit/3342cf6b1c996c2bcf7b7bf4d6caae23e3b7c29e): `.github/workflows/raft-t3-original-renderer-shader-impact.yml`, existing 22min job and SHA pins, added real class accounting assertions and safe artifact `t3-authentic-original-6scene-renderer-shader-use-42109994654`. No Unity/APK/native export, no LFS or game asset changes.

## Proof boundary / next

**RENDER-002 OPEN / NOT_READY.** The 921-used Shader48 is a candidate for widespread white **mesh** materials, not for all square effects. Remaining unknown: which exact original particle Shaders cover those 215 slots; real ShaderLab pass/Blend/keywords and texture dependency fidelity; full-native 921 Shader GUID profile; Unity compile and phone pixels.

Next experiment: source-only per-ParticleSystemRenderer ranked shader use, retaining private IDs on runner, with negative controls on material slot vs distinct Renderer count. Do not rerun the 12-owner AssetRipper export unless a new original/full-native restoration question needs it; preserve T1/T2 water and T4/T5 jobs, sound/Settings and input.
