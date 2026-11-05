# T4 independent recovery — 20261105T0341Z-T4-automation-conflict03

identity: T4
status: paused_identity_conflict
session_id: 20261105T0341Z-T4-automation-conflict03
resumed_from_session: 20261104T2357Z-T4-lw01
baseline_sha: UNKNOWN (GitHub commit search does not establish current branch HEAD; no invented SHA)
taken_over_from: B07, B14, B19, B24, B37, B50, T4 loader CI41939908432, original completion CI41943357681, ILSpy repeatability CI41944365772, FileManager CI41942655373.

Read T_TEAM/PROMPT_AR, README, RESTORE_AR, OPERATING_MODEL_AR, LEGACY_HANDOFF, MIGRATION, owner requirements, state, MEMORY, prior T4 isolated session, FileManager report and current probe/test code. Other required reference reads were attempted in this run; no complete branch HEAD, latest workflow states or device logs independently established. The shared T4 state still declares session 20261104T2357Z-T4-lw01 active, and an independent FileManager session exists. Do not overwrite state/MEMORY or overlapping work.

## Engineering review (read-only, no new source patch)
Inspected scripts/t4_original_filemanager_contract.py and tests/test_t4_original_filemanager_contract.py. The authentic CI41942655373 observation is one lexical call/declaration token for each distinct FileManager target and zero block-bodied definitions recognized by imported _bodies. The probe reports unresolved_original_name_tokens via regex matching NAME( anywhere in masked source, so it cannot discriminate a method declaration from an invocation. No original target signature or IO/catch count is proven. The synthetic 10/10 suite has block-bodied declarations and does not cover original unresolved syntax. Existing independent T4 session 20261105T0244Z already proposed a declaration-shape classifier; avoid duplicating that work without a new original-source result.

## Next nonduplicate step
Prioritize integrated Android candidate from T5 once source pin provenance is resolved. Require precise markers WorldHasBeenLoaded.firstMoveNext, WorldHasBeenLoaded.originalCompletionAssigned, OnWorldRecieved, SaveGame/SaveWorld/SaveUser, save/Load.caughtException, and actual .rgd file size/hash across close/relaunch/reopen. If candidate unavailable, first coordinate original ILSpy source pin discrepancy with T5; then run a single SHA-pinned read-only original FileManager declaration-shape classifier with call-site negative controls, rather than repeat unchanged CI. Do not alter original schema, completion flags, audio, Settings or deferred input.

No new Unity build, device test, source fix, or Action cancellation. LOCAL-005 OPEN; NOT_READY 0/3. This record is an isolated conflict-safe checkpoint, not a claim of engineering completion.
