# T3 RENDER-002 — device-to-source trace

session_id: 20261107T2230Z-T3-scheduled-render-device-chain-k4p9
origin: scheduled
baseline_head: 7b5af0689a1414b3ddfc2baea0da32484e16fe9c
status: OPEN / NOT_READY

## Scope and non-overlap
Only this new work note and T3 session note. No production assets, shared files, workflows or build requests. T1 owns FFT; T2 owns Foam; T4 physical mouse; T5 layout/resolution/delivery. Experiment key: T3-device-white-smoke-source-chain-20261107; shared resource: none. Inherited T3 source/export matching runs 41939404454 (41 materials, 227 TexEnv, 89 internal pointers) and 41940350604 (150 RGBA), which rule out a narrow internal-pointer/UV/color-export-loss hypothesis, **not** shader/variant/import/Android pixels.

## Device evidence and falsifiable hypotheses
Owner's 2026-11-05 device report docs/DEVICE_FEEDBACK_42058825739_AR.md: world entry/save/exit/re-entry worked on artifact run 42058825739, release publication failed. White hand/raft and square smoke are visible in linked CL screenshots pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. CL log summaries: 220911-559 has 23,884 water pass and 3,850 FFT kernel errors; 230108-327 has 39,132 and 6,026. Neither error count alone proves cause of white hand or square particle.

Hypothesis A (white geometry): material shader/variant or sampler/sRGB binding differs at Unity Android import despite authenticated source/export TexEnv and RGBA parity. Evidence needed: actual prefab renderer -> material GUID -> shader GUID/keywords -> texture GUID -> compiled Android shader variant, with shader errors correlated by timestamp. Do not alter mesh absent vertex/index evidence.

Hypothesis B (square smoke): particle material texture alpha missing, incorrect alpha clip/blend/ZWrite, or fallback shader draws quad. Evidence needed: prefab ParticleSystemRenderer -> material -> shader passes/keywords/Blend/ZWrite -> alpha texture and importer -> screenshot frame correlation. Distinguish square smoke from water-pass failures; avoid global particle shader replacements.

Hypothesis C (lighting): missing shader lighting variant, lightmap/normal data or incorrect color space; first verify two original Light identities and 150 RGBA values already matched, then isolate material-specific vs global effects.

## Next bounded execution
1. Fetch actual CL image bytes (not filenames alone), verify each pinned image and visually annotate hand/raft/particle regions privately. 2. Parse scene/prefab and Material PPtr GUID chains for these objects; emit safe counts and hashed internal IDs only, never game assets. 3. Compare ShaderLab passes/keywords and Android import logs for exact materials. 4. Only patch after a measured mismatch and run isolated source validation before asking T5 for a trial build. ZIP2 source pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385 must be verified per docs/ZIP2_SOURCE_PROVIDER.md. Do not claim source-only analysis reproduces Android pixels.

## Live observations
At 2026-11-07 22:22 UTC branch HEAD 7b5af0689a1414b3ddfc2baea0da32484e16fe9c (T2 docs); recent Actions 42419692491 T1 paired FFT success and 42416699458 T4 mouse classifier success. Neither is Android device confirmation. Trial vote remains T3 'لا يحتاج' pending substantive integrated graphics fix. No duplicate Unity request.
