# B05 project memory

Initial session `20261104T2107Z-B05-9e24`, first activation; no prior B05 repository files found. Initial HEAD f1dd7fccb7607264d7ec9fee6a67cb73cbbd7eb7; state registration commit b9f68e0b3de57f8fce8681d7d6248866261232b9.

Read live B_TEAM PROMPT_AR/README/OPERATING_MODEL_AR/SOURCES_AND_ACTIONS_AR/TEMPLATES/REVIEW/SUMMARY/RESTORE; AGENTS, CURRENT_OWNER_REQUIREMENTS, ZIP2_SOURCE_PROVIDER, prompt README/CONTINUE/STATUS; issues LOCAL-005/RENDER-002/WATER-001. Original source ZIP2 pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385; no game data downloaded.

Baseline: latest actual Raft game APK86 run41812889049; CL 2026-11-04 logs show Steam StoreStats failure after WorldHasBeenLoaded and invalid water shader/FFT. B50 already guards StoreStats and Cheat.GetSteamID in source but no new phone test; B02 tests sRGB, B44 compares Material m_Colors, B47/B48/B49 cover water source. Sound/Settings owner-confirmed functional; touch/controls/layout deferred.

Active RENDER-002 approach: SHA-authenticated original Material m_TexEnvs vs same-instance exported YAML, verifying preserved slots, null/bound semantics and internal target PPtrs with explicit trace. Avoid guessed external pointers, original payload disclosure and modifying any game resources. A synthetic source check is not runtime/color proof; NOT_READY 0/3. Restore using session/work, check live HEAD before writes. Plan next implement test and integration source validator, record results.

## Verified checkpoint 2026-11-04 21:17 UTC
- Source utility: `scripts/b05_verify_material_texenv_bindings.py`, [8398553](https://github.com/alwansan/raf/commit/8398553c2e4d58863998bc329ecf332af08fa0b2). Source-free 11 regression cases: [94f47ac](https://github.com/alwansan/raf/commit/94f47acffd185820445fbb9df1b2b52e0288c687).
- Isolated workflow [5948d0d](https://github.com/alwansan/raf/commit/5948d0d5041424bb175e007481b38bc0c9f19a18), [CI41914198631](https://github.com/alwansan/raf/actions/runs/41914198631) **COMPLETED SUCCESS** (11/11 synthetic checks); no LFS, APK, Unity or device.
- Report: [docs/B05_MATERIAL_TEXENV_LINEAGE_2026-11-04.md](../../../docs/B05_MATERIAL_TEXENV_LINEAGE_2026-11-04.md). State/issue/work/events/experiment recorded.
- The test guards original-vs-same-instance export material texture slot presence, null/boundness and traced same-owner original Texture PPtr. **External owner links not proven, UV scale/offset not verified, actual original/export execution not run.** Correct source fidelity remains an unresolved hypothesis; pale/white cause not demonstrated. Rejected bare cross-owner PathID matching.
- RENDER-002 OPEN; status paused after scoped test integration, NOT_READY 0/3. Do not claim material repair, new playable APK or phone color fix. Next: check updated HEAD/Actions, obtain SAME-instance exporter object trace and verified ZIP2 original data, execute tool and repair actual differences if any. Do not disrupt other B workers, sound or Settings; touch deferred.
