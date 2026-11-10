# GFX-LAB — 20261110-GFX-chat-owner-autolog-matrix-05
- session_id: `20261110-GFX-chat-owner-autolog-matrix-05`; origin=`chat`; resumed_from=`20261110-GFX-chat-auto-logs-export-04`
- base_sha: `bcd9d09b42da1557f31794068cc9c7beba3bbb53`
- source original: ZIP2@`15964ea8f246b6e076ce26b60931ee2e1a9a2385` (not downloaded in this session)
- experiment_key: `GFX-OWNER-003` / issue RENDER-002
- scope: owner-exported GFX031 ZIP analysis; independent APK DEX audit CI correction; no full game build
- status: `OWNER_ZIP_PARSED; CODE_FIX_PENDING`; evidence_level: `OWNER_ANDROID_DIAGNOSTIC_LOGS`, not `ANDROID_GAME_PIXELS`

## Local private verification
- Owner ZIP SHA256 `154f2367d12bf5be258d89c0517af8fecbf0c562b11feb5c03e33226161bb26d`, CRC PASS, 5 files (1 session).
- 77 events, 67 state snapshots, summary 0 warnings, 0 Unity errors, 0 dropped records, no write failure; device Xiaomi 23013PC75G / Adreno730 / GLES3 / Unity 2021.3.45f2 Linear.
- All M00–M05 and four Standard/white diagnostic material modes appear in snapshots; M00 only for separate channel R/G/B/A and forced-linear samples; M03 Surface index 1 **not observed**, all 67 snapshots surface 0.
- Public safe counters only; private snapshots, screenshots, cached binaries, device identifiers beyond known model must not be committed.
- Signed GFX031 Android APK previously proved by CI42802005319. Supplemental DEX CI42804520804 failed `EXPECTED_SIGNED_ANDROID_APK_ABSENT` because workflow assumed artifact root path; original build workflow uploads APK from nested Unity export directory. Correct artifact path discovery while keeping SHA/signature gates.
- Proven user export from the owner-produced ZIP, but independent physical path record only if owner confirms placement; do not claim original Shader48 restored.

## Negative controls
`originalShaderRestored=false`, `originalAnimationRestored=false`, original Shader48 Material-to-register/CB mapping BLOCKED, dynamic render states BLOCKED, PC pixel parity absent, no new original Shader48 APK. T branches, main, zip2 read-only.

## Runs / results / next step
Pending patch + CI. Record the immutable SHA and result here before closing the cycle.

## Final verified status — 2026-11-10
- **SUCCESS** owner-uploaded GFX-MULTI-031 auto ZIP CRC with one actual Xiaomi Adreno730 diagnostic session: 77 events, 67 state snapshots, no logged Unity errors/warnings/dropped records/write failures. Six models, four fallback modes each, but Normal/Metallic/R/G/B/A/ForceLinear only M00; M03 second material index 1 NOT captured.
- Second uploaded `test model(2).zip` SHA256 `adc08713ad67a987d0b30ac01b1b6e9004342b359aeb97ed1ee61866fecc4238` matches earlier owner screenshot archive, so it is **not a new shader-reference source**.
- Safe aggregate published: `gfxlab/evidence/20261110_gfx031_owner_safe_counts.json` (no raw private user ZIP/screenshots/ShaderCache or IL2CPP data).
- DEX audit initial [CI42804520804](https://github.com/alwansan/raf/actions/runs/42804520804) FAILED only due to assuming an APK at artifact extraction root. Patched recursive exact-name/unique-file lookup, retained immutable size+SHA/CRC/DEX assertions; [CI42806407666](https://github.com/alwansan/raf/actions/runs/42806407666) **SUCCESS**: 1 APK, bridge=true, method=true, destination=true, temp purge=true.
- Improved source-free parser per-model coverage and M03-specific surface check; strict session-name pairing. [CI42806606474](https://github.com/alwansan/raf/actions/runs/42806606474) FAILED because new synthetic test used literal backslash-n, not newline. Corrected JSONL fixture; [CI42806757535](https://github.com/alwansan/raf/actions/runs/42806757535) **SUCCESS**, 193 Python tests, source-free, no new APK.
- Level: **OWNER_ANDROID_DIAGNOSTIC_LOGS** only, **not original Shader48 execution** and **not Raft game/PC pixel parity**. Owner file proves ZIP was created and readable; ZIP alone cannot independently prove exact external storage path unless owner reports it.
- Next: explore unused compiled Shader48 stage metadata/RDEF as source-only GFX-MULTI-032; never fabricate missing Material→t#/s#/CB offsets or declare phase 1 closed prematurely.
