# B12 — active engineering memory

Session: 20261104T2132Z-B12-c4a8; generation B-2026-11-04. Start: 2026-11-04T21:33:58.649Z. Only write branch feature/android-native-port.

## Live inputs
Read B_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, SOURCES_AND_ACTIONS_AR.md, TEMPLATES.md, REVIEW_2026-11-04.md, SUMMARY.md, AGENTS.md, CURRENT_OWNER_REQUIREMENTS.md, prompt/README.md, CONTINUE_RAFT_AR.md, STATUS.md and ZIP2_SOURCE_PROVIDER.md. Initial branch HEAD f8028d15b2401d1fd8c73b2316e5bf76fef88eae; latest real Raft release android-early-test-41812889049-1 (APK86), no successful newer delivery. Observed latest recent CI runs 41916497948, 41916497902, 41916497807 all SUCCESS. CL provenance: review 2026-11-04 at CL commit 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29, 225757-156 log segment3: WorldHasBeenLoaded -> GameManager.OnWorldRecieved -> SaveAndLoad.SaveGame -> SteamUserStats.StoreStats -> DllNotFoundException steam_api64. Evidence is a proven failure, not sole root cause.

## Scope and plan
LOCAL-005 independent SaveGame Steam UserStats boundary (not B50 Cheat SteamID, B07 callback, B24 callback compile). Current scripts/adapt_android_offline_startup.py SaveAndLoad pinned SHA b150dd404da48b8012f6659680b3552c11500c4ec97a64ad9aa12c60094568bb; LocalPlayerIdentity.Enabled true only on Android non-editor. Plan: narrowly bypass **only remote optional StoreStats** when locally offline, while keeping the true .rgd disk write, source identity, original Windows call, original callback order and exceptions. Must fail closed for unrecognized source and duplicate/missing/masked statements; test synthetic expected/negative cases, no private C# text in public artifacts. No user device or Unity outcome until observed. No audio, Settings or touch changes.

## Work
B12-20261104T2132Z-B12-c4a8-steam-stats-save; status planned at registration. No original source, assets, .meta or save bytes to publish. Update this memory and status after implementation/verification, including limitations and next independent step.
