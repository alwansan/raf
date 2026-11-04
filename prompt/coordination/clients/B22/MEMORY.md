# B22 — engineering memory

Session: `20261104T2134Z-B22-c91f` (first registration; no pre-existing B22 state found).

- Branch: only `feature/android-native-port`. Registration baseline `03ecf8ffda13347c9ffb17ef4c5aea3a4eb86b48`; concurrent B clients active.
- Read: B_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, SOURCES_AND_ACTIONS_AR.md, TEMPLATES.md, SUMMARY.md, REVIEW_2026-11-04.md, RESTORE_AR.md; AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, docs/ZIP2_SOURCE_PROVIDER.md, prompt/README.md, CONTINUE_RAFT_AR.md, STATUS.md latest sections, RENDER-002/LOCAL-005 issues, W2/B44 scripts/tests/reports.
- Source pin ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; every original payload requires SHA/size check, no new LFS. Archive identity not validated.
- Latest Raft APK86: [41812889049](https://github.com/alwansan/raf/actions/runs/41812889049) / `android-early-test-41812889049-1`. CL read-only HEAD `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`; team CL report documents pale materials and original water/FFT pass failures. Owner-confirmed audio/Settings; deferred touch.
- Other lanes: B44 original m_Colors same-export; B05 texture/UV; B02 importer sRGB; W2 aggregate material scalars; B50 Steam stats save fix; B07/B24 callback. B22 is separate **per-instance scalar value fidelity**, not another aggregate census.
- W2 source-verified baseline: 1,556 materials, 33,899 m_Floats, 0 original m_Ints across 82 owners. _Cutoff and _SrcBlend/_DstBlend/_ZWrite are crucial. Wrong exported values are an untested hypothesis, not proven device cause.
- Plan: strict pinned original/private export-trace/YAML comparison of floats and ints; fail on swapped identity/missing/duplicate/nonfinite issues; report only integer aggregate counts; synthetic negative tests, isolated CI. Initial source scope SHA-verified 14 shader-bearing owners from B44, NOT 82-owner full-game coverage.
- RENDER-002 OPEN and NOT_READY 0/3. No game/native build, source asset modification, .meta/GUID/.rgd, sound/Settings/touch work.

Next: implement and test comparator, write report, update state/work/experiment/event/issue/status with exact evidence.

## Verified tool result at 2026-11-04T21:44:30Z
Source implementation 064f4d68; tests/workflow e1d95ca6; CI 41918404573 completed SUCCESS job126884115085, 14 independent synthetic cases. Only compare-contract proven: no original ZIP2 game Material+same-instance export were staged. Binary32 value matching, duplicate YAML, swapped identity and report nonleak controls included. Docs/B22_MATERIAL_SCALAR_EXPORT_PARITY_2026-11-04.md holds invocation. Experiment and B44/W1 discussion recorded. Scoped tool completed; RENDER-002 OPEN, NOT_READY 0/3. Next use in a coordinated private export, do not start another equivalent Unity build. Original data, sound, Settings, touch, native requests, releases and scheduled tasks untouched.

## Second P0 work checkpoint: LOCAL-005 source staging

- After completing Material scalar tool, inspected Android APK86 SaveGame steam_api64 failure and existing B50 source fix, B07/B24 callback probes and B14 offline-startup stage integrity; selected a distinct runtime-operation instrumentation apply() failure mode (not a Steam/gameplay change).
- Source prior apply() followed linked project/Assets/source parent or backup ancestors and did not protect backup copy failures within its transaction. Fixed in [2f50776d](https://github.com/alwansan/raf/commit/2f50776dfe51a5d856f3d0484a8b788ee09c04bd), preserving all real original method bodies, save/Steam logic, .meta/GUID; now refuses linked ancestors, byte-authenticates backup prior to mutation, rolls source back on install failure and RETAINS backups on failed rollback.
- New synthetic tests at tests/test_b22_runtime_stage_integrity.py, isolated .github/workflows/raft-b22-runtime-stage-integrity.yml. [CI41920661518](https://github.com/alwansan/raf/actions/runs/41920661518) SUCCESS (14 B22 tests plus existing test_runtime_operation_traces.py), on SHA a483f9f1636abb8602269712a7f79e8946f5b196. A later cosmetic single-line test cleanup [ee76eeec](https://github.com/alwansan/raf/commit/ee76eeec16575488f529ee5e31df4d20d2742113) requires final CI outcome read; no runtime logic changed.
- Detailed proof/report [docs/B22_LOCAL_RUNTIME_STAGING_INTEGRITY_2026-11-04.md](../../../../docs/B22_LOCAL_RUNTIME_STAGING_INTEGRITY_2026-11-04.md). Work and experiment records for LOCAL-005 updated, issue remains OPEN. Real authenticated Unity source staging, actual APK86+ source fix runtime, local new-world/create/save/.rgd restore all untested on phone; NOT_READY 0/3.
- Exact scope: no original game assets, audio, Settings, touch/layout, native requests, releases, CL data or other workers' code modified. No duplicate full build initiated; next coordinate original export/material parity and native/device verification when justified.

### Final source-only checkpoint 41921049831

[Final B22 LOCAL staging CI41921049831](https://github.com/alwansan/raf/actions/runs/41921049831) COMPLETED SUCCESS on ee76eeec after removal of inert test expression; existing trace regression + 14 new synthetic cases run again. [Canonical B-team generator CI41921246829](https://github.com/alwansan/raf/actions/runs/41921246829) COMPLETED SUCCESS with fast-forward-only push and no force. Both tracks have source-integrated tools and saved work/experiment/issues/status; neither has actual original-game export/device proof. No work continues outside this session. Next: run scalar checker on next private original ZIP2 same-process export; later native/gamepad-independent phone world create/save/load .rgd check on a rebuilt version, verify water/FFT and preserve audio/Settings. Project NOT_READY, 0/3.
