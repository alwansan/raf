# B50 — engineering memory

Session: `20261104T2039Z-B50-d7a3`; base HEAD: `4086cd508c154ad081d2e3931e6775c622f37c3d`; registered 2026-11-04T20:39:16Z.

## Live references read
- B_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, SOURCES_AND_ACTIONS_AR.md, TEMPLATES.md, REVIEW_2026-11-04.md, SUMMARY.md, RESTORE_AR.md; AGENTS.md, CURRENT_OWNER_REQUIREMENTS.md, prompt/README.md, CONTINUE_RAFT_AR.md, STATUS.md, ZIP2_SOURCE_PROVIDER.md.
- Original ZIP2 pin: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; no original assets copied or uploaded.
- Device summary: APK86, documented full-game delivery run 41812889049/source d181ee7152580f49ee0b41dfd05fa2bfdacfafe5; CL snapshot 5394407b. Source SHA of installed phone APK not cryptographically established.

## Mission and scope
Select LOCAL-005 (offline SaveGame/Steam stats fatal exception) as independent P0 complement to heavily investigated WATER-001/RENDER-002. Proven phone log stack: `SteamUserStats.StoreStats -> SaveAndLoad.SaveGame -> GameManager.OnWorldRecieved -> WorldHasBeenLoaded`, `DllNotFoundException: steam_api64`. Root cause likely unguarded Windows stats API; this is **not** proof it is sole failure. Do not forge world load flags, suppress other errors, alter original .rgd schema, audio, Settings or deferred touch.

## Planned engineering
Inspect exact current source, adapter, startup/SaveGame and tests; implement targeted Android offline stats boundary only if verified, run cheap unit/static checks, publish SHA/commit/evidence, update issue+event/state and prompt/STATUS. Read concurrent HEAD before every write. No Unity/native request until justified; do not overwrite others. Current stage: registered/awaiting source inspection.

## Recovery
Read work record `prompt/coordination/work/LOCAL-005/B50-20261104T2039Z-B50-d7a3-steamstats-offline.json` and session record before touching source. Current state and next tests to be updated after execution. NOT_READY 0/3.
