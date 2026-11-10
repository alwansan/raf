# T4 scheduled checkpoint — 2026-11-10 17:36 UTC
session_id: 20261110T1736Z-T4-scheduled-cl-evidence-j8p2
origin: scheduled
resumed_from_sessions: 20261110T1643Z-T4-scheduled-ci-confirmation-n2f7; 20261110T1538Z-T4-scheduled-epoch-ci-k9v2
work_commit: 899491c7986db0e137c17bbbdbdc512f12184a5b
work: prompt/coordination/clients/T4/work/INPUT-005/20261110T1736Z-T4-scheduled-cl-evidence-j8p2.md

Read owner 5 November device report, owner 8 November mini-lab feedback, T4 classifier and tests, and CL session-summary for 20261108-164850-270. CL has no event-level click/scroll counters, so summary cannot locate missing LEFT/RIGHT/MIDDLE/wheel boundary. Owner directly confirms relative camera movement works while all buttons/wheel fail. 42846576303 remains source-only CI success, not device proof.

World entry/save/exit/reentry is OWNER_CONFIRMED only for artifact 42058825739, source e9c358eda01785b65e4eb14f18723da426635628; packaging publication failed. Preserve original .rgd, keyboard, audio, Settings; T5 owns resolution and unified lab build. No gameplay code, CI, APK or shared files changed in this cycle.

Next: compare bounded native Android event trace to Unity legacy button and wheel states, with timestamps and focus/reacquire. If no native events, investigate Android bridge; if native events but no Unity states, investigate bridge mapping; if Unity states but no gameplay action, inspect Raft consumer. INPUT-005 OPEN; do not infer success from CL aggregate counters.
