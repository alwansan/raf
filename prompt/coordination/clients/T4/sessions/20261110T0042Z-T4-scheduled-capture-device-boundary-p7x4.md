# T4 scheduled session — 2026-11-10 00:42 UTC
session_id: 20261110T0042Z-T4-scheduled-capture-device-boundary-p7x4
origin: scheduled
resumed_from: 20261109T2335Z-T4-scheduled-mouse-game-boundary-v3k8.md and T4 MEMORY.md (including 2026-11-08 real CL mini and original source bridge)
baseline_sha: 9ee4ba027df6e968370f942eafc7ab19b412bcde
scope_commit: f9c58a3b78ac62eaf6229427c440fa5478bf1854
work: prompt/coordination/T_TEAM/work/20261110T0042Z-T4-scheduled-capture-device-boundary-p7x4.md

## Findings and boundaries
Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, T_TEAM instructions and T4 memory/state; checked latest branch HEAD and Actions. Owner-confirmed world/create/save/exit/reenter on artifact 42058825739 only; do not regress .rgd. T4 source bridge CI42518143297 success, tests not signed-game proof. The pinned CL/test real Android mini trace had uncaptured left clicks and wheel, so it cannot demonstrate capture-to-Unity or in-game action. CI42704145152 passed previous source tests; latest observed T3 run 42728727179 success, unrelated to input. No new game-side device JSONL is proven in this session.

## Concrete deliverable
Published independent scoped acceptance protocol with per-button and per-axis 3-stage evidence, APK/OBB fingerprint requirement, epoch/session provenance, keyboard/focus/cursor/save regression matrix. This prevents false positives from successful Android callbacks or Unity getter counters alone. No shared files, T5 Resolution, T5 mini APK, native build, Unity game code, original .rgd or touch changed.

## Result
Documentation/protocol integrated, not device fix. INPUT-005 OPEN, LOCAL-005 retains limited owner-confirmed world save/reopen, NOT_READY. CI not rerun. Next: acquire authentic signed-game same-process JSONL after T5 authorized build, correlate captured events to original getter slots and game reactions, implement source fix only where missing boundary is demonstrated.
