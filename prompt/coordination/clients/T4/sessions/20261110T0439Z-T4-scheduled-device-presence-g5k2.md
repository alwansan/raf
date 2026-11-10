# T4 checkpoint — 20261110T0439Z-T4-scheduled-device-presence-g5k2
origin: scheduled
session_id: 20261110T0439Z-T4-scheduled-device-presence-g5k2
resumed_from_sessions: 20261110T0336Z-T4-scheduled-capture-retry-audit-j6p9; 20261110T0235Z-T4-scheduled-evidence-gap-n7q4
baseline_sha: 671f2ca3177df94b88b23808bca78c5715a08f24
scope_commit: ec6a91c7b1c571e5787b45d2a258057d57860b45
work: prompt/coordination/work/T4/20261110T0439Z-T4-scheduled-device-presence-g5k2.md

## New source-level boundary identified
AndroidPhysicalMouseCapture.Update requires originalLockIntent=1 AND PhysicalMousePresent() before requesting pointer capture. PhysicalMousePresent enumerates Unity InputSystem Mouse.all, excluding RaftAndroidTouchLeft. This is a potential failure boundary on Android where OS physical mouse events and InputSystem device registration differ. The current signed-game evidence does not determine whether this occurs; **do not assert bug fixed or bypass gate**. The next minimal diagnostic should distinguish missing original lock, missing InputSystem mouse, Android View denial and Unity reader gap. Source file unchanged.

## Current external evidence
Owner report docs/DEVICE_FEEDBACK_42058825739_AR.md: Artifact 42058825739 entered/saved/reopened world on POCO F5 Pro; packaging publish failed. Preserved as artifact-specific OWNER_CONFIRMED scenario, LOCAL-005 remains open for regressions. CL/test inventory on main shows latest shared-20261109-233132-554663211, with T4-01..09 previously NEEDS_INPUT. T4-01..09 mini cannot certify game. HEAD at start 671f2ca3177df94b88b23808bca78c5715a08f24; Actions 42747722414 SUCCESS is T1 FFT, not T4. No full game build, no phone run, no CL image pixels re-evaluated in this session.

## Boundaries and next action
No changes to .rgd, FileManager, Unity gameplay, keyboard, touch, audio, Settings, T5 Resolution/right-side buttons. No CI duplicate. Next: inspect/extend bounded diagnostics only after checking team file ownership and newest HEAD; obtain same signed-game JSONL of lock intent, InputSystem physical mouse presence, capture request, view identity and legacy getter results. INPUT-005 OPEN; device proof required. This session records an independently actionable hypothesis, not a source fix.
