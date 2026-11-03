# INPUT-005 — stale suspended flag after re-enable

- Author `raft-20261103T145805Z-a7c2f809`, time 2026-11-03T15:09:30.854Z; status **source fixed, CPU verified; device pending**.
- Cause: `AndroidTouchPointer.OnDisable` invokes `Suspend(true)`, but old OnEnable failed to reset `suspended`. Re-enabling the component consumed but ignored gameplay touches.
- Initial harness run41659146129 failed test-only CS0128; corrected [34dcdb06](https://github.com/alwansan/raf/commit/34dcdb06bc401cad3ec8f8d42f335aadc2782bff). [RED41659588079](https://github.com/alwansan/raf/actions/runs/41659588079) failed expected `MULTITOUCH_ROUTE: reenable-clears-stale-suspension` with actual authored lifecycle methods.
- Fix [7517f30fd7010af11dac6444f7c0b3d3dadd5064](https://github.com/alwansan/raf/commit/7517f30fd7010af11dac6444f7c0b3d3dadd5064) resets suspension on enable. [GREEN41659802113](https://github.com/alwansan/raf/actions/runs/41659802113) 17 routing/lifecycle +446 gesture +53 Mouse0 checks; [offline41659802250](https://github.com/alwansan/raf/actions/runs/41659802250) compiled original managed source exit0/errors{}.
- No Unity/phone test or new APK; scoped fixed, general INPUT and graphics readiness remain open.
