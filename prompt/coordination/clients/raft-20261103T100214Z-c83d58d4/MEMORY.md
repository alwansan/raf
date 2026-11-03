# A7 — independent INPUT-005 recovery

- Session: A7-20261103T100214Z-4121ce131222; client: raft-20261103T100214Z-c83d58d4; UTC 2026-11-03T10:02:14Z; base SHA `cb95d4bb8b736013f996a7583e434775a5160223`.
- Goal: investigate LEFT Mouse0 Android touch ownership / cancellation / held drag without modifying original UGUI/controller/physical-input semantics; source-only bounded experiment.
- Read: `prompt/README.md`, `prompt/CONTINUE_RAFT_AR.md`, `prompt/STATUS.md`, `docs/CURRENT_OWNER_REQUIREMENTS.md`, `AGENTS.md`, `prompt/coordination/README.md`, latest linked handoff; recent HEAD/Actions/releases and CL log tree (read-only).
- Other coordination reviewed: FFT-FORMAT-009 independent completed/paused, DISPLAY-003 active, HAPTICS-008 two active agents. No touch-work client was listed at registration. Avoid those paths; recheck live work before writing.
- No queued/in-progress branch Actions at initial review. No Unity/APK/OBB/XAPK, release or scheduled-task requests authorized for this role.
- Hypothesis pending source inspection, not a claimed defect. Last phone APK80 precedes new left-input fixes; CPU tests are not phone proof.
- Next: inspect live pointer files and test harness; plan a precise regression, run local checks, update own experiment and handoff if verified.
