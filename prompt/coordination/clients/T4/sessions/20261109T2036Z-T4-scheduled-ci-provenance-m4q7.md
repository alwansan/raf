# T4 scheduled — verified mouse source CI and device boundary
session_id: 20261109T2036Z-T4-scheduled-ci-provenance-m4q7
origin: scheduled
issue: INPUT-005
baseline_sha: 054305bfea3f0417003955877ecdbcc75b424ecd
scope_commit: 83bf697f6f7290a92024f4175faa1cd53610950a
experiment_key: T4-INPUT005-ci-provenance-20261109-m4q7
resource_key: none
status: evidence_checkpoint; device_pending

## Recovery and owner result
Read docs/DEVICE_FEEDBACK_42058825739_AR.md and T4 previous session 20261109T1939Z-T4-scheduled-reader-poison-q8m5.md, plus current AGENTS/owner requirements/team operating model. Owner actually entered world, saved, exited and re-entered on artifact 42058825739, source e9c358eda01785b65e4eb14f18723da426635628; release packaging failed. This is limited phone evidence, not new candidate proof. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 contains linked game screenshots and logs. T4 mouse source bridge was earlier integrated in 20 authentic original call sites but no signed game phone acceptance.

## Verified live CI (2026-11-09 UTC)
GitHub Actions T4 same-epoch Unity mouse runtime evidence workflow run 42685509815 SUCCESS at source a3660d2eabff6ad03b29551256879832580ba516; thus prior session's poisoned-reader-only regression is no longer CI-pending. Later same workflow 42693129361 SUCCESS at 29cba2a3344df64094c9409a3117f167d5b1717d, and 42692994798 SUCCESS at 6f3df6bf68921ca2a80106192724b7dbb94bb3a0. Earlier 42686865448 and 42686942143 FAILED; newer green runs supersede only source-test failures, not phone acceptance. No equivalent workflow was dispatched. Live branch baseline 054305bfea3f0417003955877ecdbcc75b424ecd. T2 evidence-refresh run 42693951346 failed, unrelated to T4 mouse. The newer source tests are not Unity APK tests.

## Scope and limitations
No game or .rgd modification, no Android phone access, no APK/OBB/XAPK or mini-lab build, no touch/controller/keyboard/Settings/audio change, no T5 Resolution/button-layout overlap. Do not claim mouse button or wheel gameplay PASS from a source-only CI. Stay in Chat for paired T4 chat. Next T4: inspect latest source diff and fresh CL/test captured=true phone traces; correlate same signed Raft APK, same PersistentDiagnosticLog session and epoch, captured callback press/release/scroll, fallback getter and actual UI/gameplay response, including focus release and keyboard. Preserve owner world-save regression. If no new device trace, continue distinct source-level fix rather than repeat CI.
