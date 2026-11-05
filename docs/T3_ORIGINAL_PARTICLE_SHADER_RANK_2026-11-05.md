# T3 — six original ParticleSystemRenderer shader targets, authenticated source rank (2026-11-05)

**Status: SOURCE-ONLY EXPERIMENT SUCCESS; RENDER-002 remains OPEN/NOT_READY.** Owner T3, chat session `20261105T211313Z-T3-chat-particle-shader-rank-4e92`.

## Reproducible pinned original evidence

[GitHub Actions 42110973101](https://github.com/alwansan/raf/actions/runs/42110973101), commit `5d81dc7e89960c87be8a077b5c214e163ddabe81`: overall **SUCCESS**, Python source-free controls **19 T3 + 22 inherited B03 = 41/41 PASS**. Verified exactly six original scenes and four true Shader/Material owners from ZIP2 source immutable SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, **269,007,288 owner bytes**, no LFS; UnityPy original serialized graph read privately on the runner. Only source-free aggregate counts were uploaded; no raw game data, names, PathIDs or shader GUIDs in the artifacts.

- Original scenes contain **219 ParticleSystemRenderer Material slots**, **215** of which map to true type-48 Shader objects in four SHA-authenticated owners. The remaining four are outside this typed scope; do not silently assign them to any of the six.
- Exactly **six** distinct original typed Shader48 targets cover those 215 particle slots, ranked by particle slot use (anonymous): **108, 34, 34, 20, 16, 3**. Sum exactly 215.
- Highest source particle-shader rank is unique: **108 slots**, belonging to **54 distinct ParticleSystemRenderer objects** (repeated material slots ≠ extra Renderer objects). This Shader has **one original parsed Pass**. It has **zero MeshRenderer/SkinnedMeshRenderer slots** in these six original scenes; total original renderer slot use exactly **108**.
- Ranks two and three tie at **34/34**; neither source identity is declared second-best without a tie-breaker.
- In prior [authenticated top921 class audit](https://github.com/alwansan/raf/actions/runs/42109994654), the overall unique highest-use Shader48 served **914 MeshRenderer + 7 SkinnedMeshRenderer and zero ParticleSystemRenderer**; it is a **different** source Shader. Together these results cleanly separate high-use white mesh candidates from particle material priorities.

## Code and scope

- [Source graph rank, mixed-class provenance and tie safeguards](https://github.com/alwansan/raf/commit/a4a0f31438d65714661f1bd1f779bdc62032f7e7) extend `scripts/t3_original_renderer_shader_impact.py` without exposing private shader names, IDs, GUIDs, raw original bytes or per-object IDs.
- [Four synthetic source-free negative/positive tests](https://github.com/alwansan/raf/commit/449b2235acfaa68837d9e8fa6f1495e810a42807) verify global shader use ≠ particle-only use, duplicate material slots vs Renderer object counts, tied top Shader rank is not assigned arbitrarily, and zero-particle scope cannot invent a source Shader.
- [Actual original SHA-pinned workflow](https://github.com/alwansan/raf/commit/5d81dc7e89960c87be8a077b5c214e163ddabe81) retains 22-minute timeout, no native Unity/AssetRipper game export, authentic original 6-scene/four-owner staging, prints only safe numeric rank and source-known Pass count. Artifact `t3-authentic-original-6scene-renderer-shader-use-42110973101`.

## Limitations and actionable next step

**This does not prove:** the original one-Pass particle shader's Blend factors or alpha source; sprite/particle texture identity and sRGB; whether the resulting restored ShaderLab is still Dummy; whether the game invoked an emitter; or whether the square fire/smoke pixels seen on the user's Android phone use this shader. Classifying material references by source class is not equivalent to GPU draw calls. No device/Unity compile or APK is produced.

**Next:** On SHA-authenticated original ParticleSystemRenderer highest-used Shader48 (108 particle slots, 54 Renderer objects, one serialized Pass), privately extract its original Pass render-state Blend/SrcBlend/DstBlend/ZWrite/ZTest/alpha coverage, texture/sampler and keyword references with integrity checks; compare to actual postrestorer ShaderLab GUID and target device square-smoke screenshot before editing Unity shader assets. Preserve provenance, source-only verdict, no private IDs, and coordinate with T5's full native workflow. Investigate second-place tied shaders (34/34) without choosing one arbitrarily.

No original game assets, .meta/GUID, shader programs, water, sound, Settings, mouse/touch or save files were changed. No other clients' jobs were cancelled or duplicated. Reconcile with T1/T2's water pipeline and T5's native build before any shared asset edits.
