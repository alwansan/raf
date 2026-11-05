# T4 isolated recovery session — 20261105T0843Z-T4-parser-validation-isolated
status: paused_identity_conflict
resumed_from_session: 20261104T2357Z-T4-lw01
baseline_sha: 83dbe8401d42e13bb556224e0466e4f397145ff4
taken_over_from: T4 prior FileManager diagnostic commits c3919ed,b133e4d,21b6a089,eeea61c2,52004731; B07/B14/B19/B24/B37/B50 historical evidence (no agents restarted).
track: LOCAL-005

## Live checkpoint
T4 state.json still says active, session 20261104T2357Z-T4-lw01, updated 2026-11-05T00:54Z; other automation sessions exist. Treat as possible identity conflict: no state.json or MEMORY.md edits. Original authenticated source CI41939908432, CLR CI41943357681 and ILSpy repeat CI41944365772 are source/managed only. No device proof. Latest CL/main SHA 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29. Latest documented actual Raft game release android-early-test-41812889049-1, APK86. Recent GitHub Actions query returned no queued or in_progress runs; latest T3 parity run 41994969127 succeeded and T1 native import 41978496060 failed. No cancellation or build started.

## Plan and finding
Plan: verify that the corrected declaration-shape tests are actually executable, without redoing private original ILSpy or heavy Unity builds. Read scripts/t4_filemanager_declaration_shapes.py and tests/test_t4_filemanager_declaration_shapes.py from live branch. Eight test methods exist, but no dedicated execution workflow and no evidence that they ran. The script imports _executable_positions from B07 and classifies only lexical candidates; it explicitly returns target_absence_proven=false, runtime_callability_proven=false, device_tested=false. Do not infer original FileManager absence or runtime correctness from lexical classification. Existing raft-t4-original-filemanager-io.yml runs the *other* contract tests, not the new declaration-shape tests. This is a specific verification gap.

## Safe next step
Add isolated low-cost synthetic-only T4 test workflow with path filters and independent concurrency, then check its actual run; if passing, use pinned ZIP2 private source in existing authenticated workflow only for a genuinely new FileManager hypothesis. Native integrated APK create/save/relaunch/reopen remains unverified. No changes to game, Steam, sound, Settings, touch, GUID or .rgd. LOCAL-005 OPEN, NOT_READY 0/3.
