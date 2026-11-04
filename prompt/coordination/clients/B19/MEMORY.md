# B19 — Raft Android engineering memory

Session: `20261104T2137Z-B19-svpr3` (first B19 session). Active track: `LOCAL-005`, offline SaveAndLoad original source portability and source integrity. Baseline at first inspection: `e78ea6d9770ccc33b0f15e14152dd46d4be22679`; re-read HEAD before each commit.

## Sources read
B_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, SOURCES_AND_ACTIONS_AR.md, TEMPLATES.md, REVIEW_2026-11-04.md, SUMMARY.md, RESTORE_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/README.md, prompt/CONTINUE_RAFT_AR.md, prompt/STATUS.md and ZIP2_SOURCE_PROVIDER.md. Current local-path source and tests inspected.

ZIP2 immutable original provider `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; do not copy original binaries to raf. CL review source `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`, APK86 final reports `SteamUserStats.StoreStats` to missing `steam_api64` after WorldHasBeenLoaded. This specific call already source-guarded by B50 and B12 independently working on deeper SaveAndLoad boundary. B07/B24 traced callback with original managed compile; newer device confirmation not available.

Latest real Raft Android release is `android-early-test-41812889049-1` / APK86 at source `d181ee7152580f49ee0b41dfd05fa2bfdacfafe5`, **not** newer LogRaft releases. CI jobs in progress observed; none cancelled. WATER-001/RENDER-002/LOCAL-005 remain OPEN, NOT_READY 0/3. Audio and Settings work on owner's phone; touch and layout are deferred.

## Scope and hypothesis
Independent of active B12/B13 writes to `scripts/adapt_android_offline_startup.py`: investigate `scripts/adapt_original_save_paths.py` transaction for the one authenticated original `SaveAndLoad.cs` + `.meta`. Current routine copies source and metadata into backup then mutates C#, but failure after a partial copy can leave an incomplete backup; repeated adaptation refuses it and can stop future world-save source staging. Also check linked nested provider/backup paths and rollback. Preserve source bytes, original .meta and original .rgd semantics. Source SHA pin is `b150dd404da48b8012f6659680b3552c11500c4ec97a64ad9aa12c60094568bb`; do not modify pin or private original content. A synthetic test cannot prove device saves.

Work record: `prompt/coordination/work/LOCAL-005/B19-20261104T2137Z-B19-svpr3-save-path-transaction.json`. Next: implement bounded safe transaction plus fault-injection tests and run reproducible unit tests; record whether failure hypothesis reproduced. No native/Unity requests until coordinated.
