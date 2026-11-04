# B05 project memory

Initial session `20261104T2107Z-B05-9e24`, first activation; no prior B05 repository files found. Initial HEAD f1dd7fccb7607264d7ec9fee6a67cb73cbbd7eb7; state registration commit b9f68e0b3de57f8fce8681d7d6248866261232b9.

Read live B_TEAM PROMPT_AR/README/OPERATING_MODEL_AR/SOURCES_AND_ACTIONS_AR/TEMPLATES/REVIEW/SUMMARY/RESTORE; AGENTS, CURRENT_OWNER_REQUIREMENTS, ZIP2_SOURCE_PROVIDER, prompt README/CONTINUE/STATUS; issues LOCAL-005/RENDER-002/WATER-001. Original source ZIP2 pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385; no game data downloaded.

Baseline: latest actual Raft game APK86 run41812889049; CL 2026-11-04 logs show Steam StoreStats failure after WorldHasBeenLoaded and invalid water shader/FFT. B50 already guards StoreStats and Cheat.GetSteamID in source but no new phone test; B02 tests sRGB, B44 compares Material m_Colors, B47/B48/B49 cover water source. Sound/Settings owner-confirmed functional; touch/controls/layout deferred.

Active RENDER-002 approach: SHA-authenticated original Material m_TexEnvs vs same-instance exported YAML, verifying preserved slots, null/bound semantics and internal target PPtrs with explicit trace. Avoid guessed external pointers, original payload disclosure and modifying any game resources. A synthetic source check is not runtime/color proof; NOT_READY 0/3. Restore using session/work, check live HEAD before writes. Plan next implement test and integration source validator, record results.
