# GT — Chat-14: original Particle108 Shader48 private Unity import and Android Vulkan probe

- session_id: GT-20261112-CHAT-14-ORIGINAL-PARTICLE108-UNITY
- origin: chat; GT standalone. Only writable: feature/android-native-port.
- Original source: pinned ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385, never Git LFS.
- Owner stopped T1–T5; no waiting.

## Why this work is part of true graphics restoration

Source export baseline: 1536 Materials, 750 builtin, 786 originally Dummy-export-linked; after official TMP/PostFX/Volumetric 16 custom docs non-Dummy, **770 still Dummy**. Source Material/Texture and BC3 top-mip data integrity: real 9/28/416/50 [43207734641 SUCCESS](https://github.com/alwansan/raf/actions/runs/43207734641); strict native gate [d734b7c7](https://github.com/alwansan/raf/commit/d734b7c71327747b80808cc307bdc5c41154c432).

To work toward actual original shader restoration rather than inventory-only, selected original unique particle Shader48 used by 108 source ParticleSystemRenderer Material slots, with six original scenes SHA verified plus four original shader/material owners SHA verified. Four source-specific keyword variant DXBC vertex/fragment pairs recovered and checked in isolated source probe; 8 stage glslang Vulkan1.1 passes.

## This session code and target

- [Private Unity project stager](../../scripts/gt_particle108_private_unity_project.py) Commit c0530917: only accepts SHA-origin verification receipt of four source keyword routes, eight validated original VS/FS stages and one complete non-Dummy private ShaderLab; checks no original files, GUIDs or assets edited and protects private paths/exports.
- [Synthetic regression tests](../../tests/test_gt_particle108_private_unity_project.py) Commit 676077a0: missing route, missing keyword, unsafe symlink and source-name leak protections.
- [Editor C# compile validation](../../android-port/Experiments/GT/Editor/OriginalParticleShaderValidation.cs) Commit 696f5cc6: pinned Unity 2021.3.45f2, Android Vulkan only, actual Shader import, 4 source keyword variants in ShaderVariantCollection, one-pass isolated Material, private Android shader AssetBundle strict compilation. Safe aggregate result only, no HLSL/GUID/keyword strings uploaded, zero original game asset writes; no Android phone pixel claim.
- Modified original source [workflow](../../.github/workflows/raft-t3-particle108-private-shaderlab-variants.yml) Commit 74bc4398 to actually compile in Unity via game-ci with separate environment UNITY_LICENSE. Tests were initially failed by overly narrow synthetic helper directory guard, then fixed [a77cfc30](https://github.com/alwansan/raf/commit/a77cfc3069058d86dbcc4200478a72659f6150a3) and [067a640f](https://github.com/alwansan/raf/commit/067a640f844fc1b751f4431760c0e8ca1d74d126). No shader source changes or original SHA change.

## Last verified execution, do not overclaim

[43220728060](https://github.com/alwansan/raf/actions/runs/43220728060): synthetics PASSED, exact original four HLSL ShaderLab candidates PASSED, 8 glslang Vulkan11 translated stage branches PASSED, original two-keyword lattice names mapped and compiled provisional unified shader PASSED, private Unity project preparation PASSED. **Unity Editor private Android Vulkan AssetBundle compile is IN PROGRESS**. This is a bounded proof, not game restoration yet; actual Unity result determines next move. [43205543533](https://github.com/alwansan/raf/actions/runs/43205543533) full native still IN_PROGRESS at Unity 2021.3.45f2 Android import, separate immutable old source commit, no delivered APK/OBB/XAPK proven.

## Next

1. Inspect completed run 43220728060 job step and sanitized JSON. If failed first stage, fix/test, retry without leaking original game bytecode. If succeeded, only then begin same-instance original Shader48 GUID and exported Material bindings integration inside disposable project, retain originals/Meta untouched.
2. Check build 43205543533; if fails inspect earliest failure, produce code-fix + regression, no duplicate while still running.
3. Keep full candidate private and do NOT call restored Dummy Materials until real native imported same GUID and Material program coverage audited, then test Android GPU pixels. 
