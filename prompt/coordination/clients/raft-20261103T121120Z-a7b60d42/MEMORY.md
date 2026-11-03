# A7 new session — raft-20261103T121120Z-a7b60d42

Started 2026-11-03T12:11:20.674Z on `feature/android-native-port` HEAD `905bd61c040025aa37dda22816126108b8e8c793`; session `A7-20261103T121120Z-3a28b2d1`, resumed from previously completed `raft-20261103T113245Z-a7e48c92` without overwriting old records.

Read live prompt README/CONTINUE, STATUS, CURRENT_OWNER_REQUIREMENTS, AGENTS, coordination README, linked handoff, platform workflow, authored TouchPointerGesture, Button, pointer methods, and existing BoundaryMatrix. Examined live HEAD/Actions (no current queued or in_progress), last APK80 release older SHA, historical read-only CL log folders; other current clients focus on FFT/WATER, DISPLAY, HAPTICS, LOCAL, DIAG/RENDER. INPUT-005 records from prior A7 sessions completed. No source overlap found for the scoped gesture CPU experiment.

Hypothesis: repeated stationary or same-coordinate touch events update `lastTime` but still `emit(Move,x,y)`, causing a redundant `InputSystem.QueueStateEvent` for every unchanged point, unrelated to hold state. A bounded C# failing test should first show redundant events; then suppress zero-position-delta Move only, while preserving `lastTime`, Tick and exact 500ms threshold, actual movement and Cancel/Up/Down. Distinguish deterministic event-count reduction from measured phone performance.

Do not modify Unity, APK/OBB/XAPK, scheduled tasks, release, native request, CL, original assets, protected branches; preserve RIGHT physical devices and synthetic LEFT Mouse0. All work on one branch with expected HEAD SHA lease and self-owned files. Update work/experiment/state/status/handoff after verified CI.
