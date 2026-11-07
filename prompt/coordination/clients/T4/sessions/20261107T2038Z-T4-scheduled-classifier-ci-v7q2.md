# T4 scheduled checkpoint — 20261107T2038Z-T4-scheduled-classifier-ci-v7q2

origin=scheduled; issue=INPUT-005; branch=feature/android-native-port.
base_sha=9ace8ce8627adcbb4fe01e5cf88b0939f9660064.
resumed_from_sessions=20261107T1939Z-T4-scheduled-r4m9; 20261107T1843Z-T4-scheduled-multi-rearm-f6k2.

## Evidence and coordination
Read owner phone feedback, AGENTS, owner requirements, STATUS, and T_TEAM chat/schedule, prompt, operating model. Owner confirmed playable world, save, exit and reopen using artifact from run 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628). Publication failure does not invalidate that limited device observation. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 is older than the newly added mouse intent trace; it cannot prove the new trace works. LOCAL-005 remains open. T5 owns button relocation and Resolution. No touch, keyboard, save, .rgd, audio or Settings edits.

Inspected HEAD 9ace8ce8627adcbb4fe01e5cf88b0939f9660064, latest T4 session and INPUT-005 work list; Actions list exposed no in-progress/queued runs among latest 30 results. Last confirmed mouse bridge CI 42373576554 succeeded at 27fc3baf (not current classifier). No equivalent classifier-only workflow existed; existing raft-t4-mouse-capture-bridge.yml is a heavier original-DLL C# proof and does not include classifier tests.

## Engineering delivered
Registered independent work scope in commit 7a9d92733b62ba74820df08db537cbc7173b2a8c before implementation. Added .github/workflows/raft-t4-mouse-trace-classifier.yml in commit b1b3d66a6d14859d2c82a033d8dbca4f00202e7d. The bounded Ubuntu 24.04 Python-only workflow uses sparse checkout, no LFS, no game assets, no original binary, no Unity, 5-minute timeout, non-cancelling concurrency, and executes py_compile and unittest discover for the 17 committed regression tests. Triggered only by the two classifier paths or workflow file, plus explicit manual dispatch.

## Verification boundary
GitHub contents API confirmed workflow commit. Actions listing immediately after commit did not yet expose a new run; status=waiting_ci/unverified. Do not claim 17 tests passed. No Android device test or physical mouse fix. No Unity build dispatched. Next cycle: check Actions for workflow run at b1b3d66a or newer; inspect failing test if any; apply classifier to fresh device Escape→menu→game logs; distinguish Android request/capture and authored cursor lock; preserve keyboard. Coordinate any runtime patch before editing shared mouse bridge.
