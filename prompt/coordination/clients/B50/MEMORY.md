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

## Checkpoint 20261104T2039Z-B50-d7a3: StoreStats boundary source fix integrated (2026-11-04T20:48Z)
- Production adapter `scripts/instrument_android_runtime_operations.py` [c06acd1](https://github.com/alwansan/raf/commit/c06acd1da46e729a42f8b9bbf2f280a3b05921cc) guards the **sole executable original** `SaveGame` `SteamUserStats.StoreStats()` for Android-local; guard inserted after original source SHA check, before original-operation tracing. Windows stats path and original SaveWorld/SaveUser/.rgd calls remain unchanged. Unknown source revisions or duplicate/missing callsite refuse transformation. Prior save-path and local ID adapters remain unchanged.
- Dedicated [CI41909535307](https://github.com/alwansan/raf/actions/runs/41909535307) SUCCESS source 67d75cc; existing [original Android offline startup CI41909535306](https://github.com/alwansan/raf/actions/runs/41909535306) SUCCESS on same source, including private original-source recovery, adapted RPC/identity harness and C# compile. Strict scope: managed compile and source contract, *not* Unity/IL2CPP/on-phone gameplay, world-save/reload or removal of all Steam DLL callsites.
- Earlier [41909268096](https://github.com/alwansan/raf/actions/runs/41909268096) and [41909431128](https://github.com/alwansan/raf/actions/runs/41909431128) FAIL were a negative-control test fixture with literal \\n hiding C# closing brace in comment; fixed only fixture in [67d75cc](https://github.com/alwansan/raf/commit/67d75cc7381a03f2b5ee166afc9d48de0d15217a). This did not indicate production adapter defect. Incident in incidents/B50.
- CL SHA `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`, latest game APK86 source d181ee71; no newer device source observed. Owner SOUND and Settings continue to work; touch/layout deferred. Graphics WATER-001/RENDER-002 open (APK86 40327 invalid water passes; 5555 invalid FFT kernels).
- Persistent records: work LOCAL-005 marked completed **for guarded stats callsite only**; issue remains OPEN. Experiment `experiments/B50/20261104T2039Z-B50-d7a3-storestats-boundary.json`, event `events/B50/20261104T2047Z-local-steamstats-sourcefixed.json`, scoped incident.
- Next useful step: probe independently reported `Cheat.AllowCheatsForLocalPlayer -> SteamUser.GetSteamID` for an Android offline identity guard with exact original caller evidence; DO NOT use fake world flags. Coordinated future device APK trial should create, save, exit, reopen .rgd; P0 water/shaders still block readiness (0/3).
