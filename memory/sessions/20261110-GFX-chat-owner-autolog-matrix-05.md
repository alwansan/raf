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
