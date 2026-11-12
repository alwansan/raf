# GT — Chat 18: proven Unity Android Vulkan shader compilation; independent diagnostic phone APK

- session_id: GT-20261112-CHAT-18-UNITY-APPROX-DEVICE
- origin: chat; write branch `feature/android-native-port` only.
- source ZIP2 pinned SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; no Git LFS.
- T1–T5 stopped by the owner; do not wait for their locks.

## Important true success

[43236578305](https://github.com/alwansan/raf/actions/runs/43236578305) completed **SUCCESS**, with actual Unity 2021.3.45f2 Android Vulkan shader import, four `ShaderVariantCollection` variants, one material pass, zero shader errors, and a **9,321-byte private Android Shader AssetBundle**. That isolated original-DXBC-derived candidate used **approximate Linear/Repeat inline SamplerState declarations**, plus stage-local translated cbuffer identifiers. Its safe report explicitly says `originalMaterialBindingProven=false`, `originalRuntimeKeywordSelectionParityProven=false`, `originalAndroidAdrenoPixelsProven=false`, `gamePlayerBuilt=false`. **No claim of restoring the original Shader48 Material or 770 Dummy shader documents.** Do not upload temporary HLSL/ShaderLab source or private GUIDs as artifacts.

## Why original exact shader binding is still blocked

[43237509847](https://github.com/alwansan/raf/actions/runs/43237509847) and [43237137442](https://github.com/alwansan/raf/actions/runs/43237137442) proved source-authenticated **eight** original DXBC Shader48 stages, all with RDEF absent, containing **ten D3D11 `dcl_sampler` declarations**, but **zero** matching serialized `m_SamplerIndex` slots and **zero** rows in present `m_CommonParameters.m_Samplers` metadata. Ten translated HLSL `SamplerState` definitions exist. The strict Material binding gate ends `TRANSLATOR_SOURCE_SAMPLER_SLOT_MISSING`, correctly fail-closed. Source correspondence/filter/wrap/runtime binding cannot be inferred from numeric coincidence or compiler-only Linear/Repeat approximation.

## Device-test work this session

Created independent **offline standalone Vulkan Android ARM64 diagnostic**; it must not touch native game files, original Materials, .meta/GUIDs, or native full build:
- [Runtime](../../android-port/Experiments/GT/Runtime/GTParticlePhoneRuntime.cs), commit `66d5f4ecc8558e50160e35200007a65765e9c7c4`: 4 preview variants, quad and particle preview, FPS/GPU/Vulkan details, `COPY LOG JSON`, save safe JSON in app persistentDataPath. Exposes `originalShaderRestored=false`, `originalMaterialBindingProven=false`, `originalAdrenoPixelsVerified=false`, `approximateSamplerStates=true`.
- [Unity Editor APK build](../../android-port/Experiments/GT/Editor/GTParticlePhoneBuild.cs), commit `dbd4964ddb9a83d7d31ce21b05fb0961302c6a16`: build new empty offline test scene only, four diagnostic Materials and generated checker texture, Android Vulkan-only, ARM64 IL2CPP, landscape, development APK. Test scene and APK are separate from original Raft data.
- [Synthetic contract tests](../../tests/test_gt_particle108_phone_probe_contract.py) commit `60d467a835ad169c0e68b7718dae13b71e62512b`.
- [Phone CI](../../.github/workflows/raft-gt-particle108-approx-phone-apk.yml) commit `39db5fee4e91e4717ea7814bc67db8a635dd30f1`: SHA-authenticate original source privately, produce compiler-only approximate HLSL ShaderLab in disposable scratch, stage independent Unity project, invoke `RaftGT.GTParticlePhoneBuild.Build`, require Android Vulkan ARM64 APK, upload APK and sanitized safe JSON **only** if accepted. No HLSL source in Actions artifact. [Run 43241736207](https://github.com/alwansan/raf/actions/runs/43241736207) **at Unity build stage at last observed snapshot**, **NOT yet declared completed or downloadable**.

## Native full build

[43205543533](https://github.com/alwansan/raf/actions/runs/43205543533), source SHA `c86809380ab1e5b95ccf65e30074422a7e744c05`, remained **in_progress** inside real Unity Editor 2021.3.45f2 `reconstruct` job `131139869574`. No completed APK/OBB/XAPK verified. It predates newer original BC3/416-link integration strict source gates. Do not cancel/retrigger duplicate while running.

## Next required actions

1. Inspect 43241736207 final step and C# Unity/IL2CPP/Android compile logs. If failure, fix minimal first failing error in isolated test project and rebuild; do not misrepresent failure.
2. On successful build, link actual GitHub Actions Artifact and request phone screenshot/JSON only when user decides to test; Android runtime and output have approximate sampler, so visual difference cannot establish original parity.
3. For source-authentic shader acceptance, separately recover original DXBC sampler→texture *usage* relationships and filter/wrap semantics using provable original instruction/Material/Texture links, or explicitly keep blocked. Never map only by original vs translated numeric index.
4. Check [native run](https://github.com/alwansan/raf/actions/runs/43205543533) after completing private APK. Keep source ZIP2 SHA unchanged, zero LFS, preserve 9/28/416/50 source parity gates.
