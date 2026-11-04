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
