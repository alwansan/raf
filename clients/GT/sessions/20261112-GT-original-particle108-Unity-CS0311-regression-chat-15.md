# GT / Chat-15 — Particle108 real Unity compile error and private HLSL source-binding diagnostics

- session_id: GT-20261112-CHAT-15-CS0311-REGRESSION
- origin: chat
- repository: alwansan/raf
- only write branch: `feature/android-native-port`
- original source: pinned `zip2` at `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, SHA-authenticated only, **no Git LFS**
- T1–T5 previously stopped by owner; GT authorized to continue without awaiting them

## Real execution evidence (UTC 12 November 2026)

- [43220728060](https://github.com/alwansan/raf/actions/runs/43220728060): 4 source-authenticated original Particle108 VS/FS Shader48 pairs and 8 private Vulkan1.1 glslang stage branches passed. Actual Unity 2021.3.45f2 editor compilation **failed**: `CS0311` at `OriginalParticleShaderValidation.cs:100`, because `ShaderVariantCollection` is an `UnityEngine.Object`, not a `ScriptableObject`, so `ScriptableObject.CreateInstance<ShaderVariantCollection>()` cannot compile. The current Editor test source uses `new ShaderVariantCollection()` instead. **No Unity shader bundle or Android GPU success proven**.
- [5c41bf9](https://github.com/alwansan/raf/commit/5c41bf9411478bb3ecb30a60c4bd4585e052856b): independently added a regression assertion to `tests/test_gt_particle108_private_unity_project.py`: require Unity 2021 proper public `new ShaderVariantCollection()` construction, refuse the observed `ScriptableObject.CreateInstance<ShaderVariantCollection>`, and check the bundle entry point remains present. Test stage passed in [43225350415](https://github.com/alwansan/raf/actions/runs/43225350415); later real original source resource stage failed, so **workflow as a whole failed**. This is a *static source guard*, not a successful real Unity import proof.
- [43224513253](https://github.com/alwansan/raf/actions/runs/43224513253): private source `ORIGINAL_NAME_INDEX_NONIDENTIFIER`; not necessarily texture binding because full Unity name table contains other symbols.
- [43224805848](https://github.com/alwansan/raf/actions/runs/43224805848): source-resource proof `SOURCE_TEXTURE_MAPPING_UNRESOLVED`.
- [43225118785](https://github.com/alwansan/raf/actions/runs/43225118785) and [43225350415](https://github.com/alwansan/raf/actions/runs/43225350415): real private source-binding stage `TRANSLATOR_NO_SOURCE_SAMPLER_DECLARATIONS` after source authentic 4 pairs/8 glslang. This is a strict unresolved proof; do **not** infer textureless VS without source metadata.
- [43225536504](https://github.com/alwansan/raf/actions/runs/43225536504): synthetic fail-closed regression caught a valid sampler alongside an unsupported `space1` sampler declaration; later source guard now explicitly rejects unsupported nonzero space regardless of other valid bindings. At snapshot, [43225736525](https://github.com/alwansan/raf/actions/runs/43225736525) was running; do not call PASS without a successful job.
- [43205543533](https://github.com/alwansan/raf/actions/runs/43205543533): pre-existing full native request at `c8680938` remained **in progress** in Unity Editor import; logs show genuine assets being imported as late as 12:30 UTC, no confirmed APK/OBB/XAPK. Do not cancel or spawn a duplicate while it remains active. That run does not include later strict 9/28/416/50 combined gate code.

## Accepted vs unproven

- Accepted already: 82 SHA-authenticated original source owners, 9 original Class187 texture arrays/28 Material references, 416 external material texture pointers, 50 authentic BC3 top-mip slices, as proven by [43207734641](https://github.com/alwansan/raf/actions/runs/43207734641). Synthetic Unity C# constructor regression now added.
- Unproven: actual Shader48 Unity import and Android Vulkan bundle, binding and runtime equivalence of the 108 ParticleSystemRenderer slots, all 770 remaining dummy-export Materials, lower mip fidelity and Adreno render output.

## Next actions

1. Inspect the latest Particle108 same-branch run by its **failed step and safe status code**, not by workflow badge alone. Distinguish source metadata from translator register spaces; do not guess sampler or texture identity.
2. Once true source↔translated HLSL bindings pass, re-run isolated Unity Android Vulkan `ShaderVariantCollection` and strict AssetBundle compile. Record safe aggregate only.
3. Only then attempt same-instance original shader GUID/Material export links. Preserve original GUIDs and .meta in production, retain 9/28/416/50 strict gates.
4. Inspect completion of full native `43205543533`; fix the first actual failing step if it fails, or audit signed APK/OBB/XAPK if complete. No duplicate active build.
