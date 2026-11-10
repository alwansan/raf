# T5 scheduled checkpoint — 20261110T224739Z-T5-scheduled-evidence-boundary-k7m2
origin: scheduled
resumed_from_sessions: 20261110 T5 PERF-007 9e7a510 / 9ac20bf; previous 42889557850 failure
scope_commit: 8fdc0524b1c43b6d673d5ef1cc3ad1b4518bc038
status: blocked_external_binary_provenance; no CI launched

## Verified live source audit
Read docs/DEVICE_FEEDBACK_42058825739_AR.md and AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM protocol/PROMPT/OPERATING_MODEL. Owner reports game world entry/save/re-entry on 42058825739, source e9c358eda01785b65e4eb14f18723da426635628. Delivery publish failed; signed APK/OBB installed hashes remain unverified. The CL pinned 520c4cf screenshot and telemetry are not sufficient to identify exact installed binary. Historical 220911-559 57 presentation FPS estimates average 22.29, 230108-327 only 2 eligible; HUD 18.27 FPS and p95 82.82 ms are separate methods. Do not merge or call GPU time.

Additional 8–9 Nov owner policy supersedes old multi-mini arrangement: one shared Mini APK, shared-20261109-r5; CI42691609924 SUCCESS, artifact13707257362, Mini package com.alwansan.raft.lab.shared versionCode17 SHA256 272d4ce9a199c5876b179926c9f27ed0d7a8c4db34b2a3993de2c44a94e323cf; this is NOT the actual Raft APK/OBB and cannot validate its resource pairing. R5 is debug-signed and no device PASS confirmed in the read policy. The full-game trial vote round trial-20261106-r1 remains non-consensus and stale, not a fresh build authorization.

Read scripts/t5_cl_fps_cohort_gate.py and scripts/t5_cl_pid_epoch_audit.py: current source deliberately withholds session FPS aggregation when process epoch is unverified or mixed, and comparison cannot become SAME_SCENE_BINARY_COMPARABLE without independently validated binary and scene. No unsafe loosening of gates.

## Limitations
GitHub connector supports source reads and commits, but no accessible Actions run/log listing in this run; prior PERF-007 fix 9e7a510 CI success not independently verified here. CL screenshot bytes and original signed APK/OBB bytes not acquired in this run. No phone test, no Unity build, no changes to mouse/UI/Resolution. Work item is provenance reconciliation, not a game fix. Avoid claiming ready.

## Next actions
1. Fetch actual signed delivery manifest and APK versionCode/OBB filename-size-SHA from a single 42058825739 artifact pair; compare to manifest and signed cert. Treat mismatch as failure.
2. Check CI for 9e7a510 PERF-007 on pinned CL real logs; distinguish actual assertions from skipped jobs.
3. Review live UI files and T4 scopes; implement right-side three-button safe-area placement and Resolution fixes on separate files with source tests; T4 handles pointer capture.
4. Keep full XAPK request gated, no duplicate Unity, and maintain shared Mini policy.
