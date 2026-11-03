# A7 restored — OnEnable lifecycle input repair

- Session: `A7-20261103T145805Z-7bf83c12`; username `raft-20261103T145805Z-a7c2f809`; UTC 2026-11-03T14:58:05.824Z; resumed_from completed A7 `raft-20261103T132738Z-a7f64e28`.
- Live baseline HEAD `7462e0b2754720a8b6581cf00e037cb9af094e04` on `feature/android-native-port`. A7 historical five identities examined, all completed; latest previous source `583f414dee85f1659783a08ab2b4363cc2992d14`, successful platform CI41645428990 and offline41645429004.
- Protocol: unified prompt, coordination README/templates, owner requirements, AGENTS, prompt README/CONTINUE/STATUS, readiness ledger and latest handoff inspected. Existing INPUT-005 work/experiments/discussions/incidents read; all five prior A7 scopes completed, not device verified.
- Initial live Actions 41658257952 pending, 41658185465 in_progress, separate reconstruction/preflight lanes; do not cancel/duplicate. Other WATER/RENDER/HAPTICS/LOCAL/DISPLAY work not touched.
- **New reproducible source hypothesis:** AndroidTouchPointer.OnDisable() calls Suspend(true); OnEnable() allocates input devices and handlers but does not reset suspended, so a reused enabled component consumes new gameplay events and emits nothing. Validate with actual extracted OnEnable and OnEvent in strict C# doubles before changing source.
- Scope: authored AndroidTouchPointer + existing CPU packet-routing verifier only; preserve raw secondary touch, UGUI sticky ownership, LEFT Mouse0, 500ms, real peripherals. No Unity/native builds, no CL write, no scheduler, no protected branch or assets.
- Next checkpoint: red CPU test, minimal fix, green platform/offline CI; update independent records, STATUS and linked handoff with evidence and limits.

## A7 final verified checkpoint — 2026-11-03T15:08:15.607Z

- Test-only CI41659146129 failed with **harness C# CS0128**, which was corrected in test commit [34dcdb06](https://github.com/alwansan/raf/commit/34dcdb06bc401cad3ec8f8d42f335aadc2782bff), not counted as gameplay defect evidence.
- **Red:** [41659588079](https://github.com/alwansan/raf/actions/runs/41659588079) on unpatched actual production OnEnable/OnDisable/Suspend/OnEvent failed at `MULTITOUCH_ROUTE: reenable-clears-stale-suspension`.
- **Fix:** [7517f30fd7010af11dac6444f7c0b3d3dadd5064](https://github.com/alwansan/raf/commit/7517f30fd7010af11dac6444f7c0b3d3dadd5064) sets `suspended=false` on each OnEnable to allow a reused component to receive touches after OnDisable.
- **Green platform:** [41659802113](https://github.com/alwansan/raf/actions/runs/41659802113) SUCCESS on exact source 7517f30fd7010af11dac6444f7c0b3d3dadd5064: 17 raw/lifecycle checks,446 gesture 500ms tests,53 LEFT Mouse0 mapping checks, physical devices preserved by source harness. **Green original offline:** [41659802250](https://github.com/alwansan/raf/actions/runs/41659802250) SUCCESS `RAFT_OFFLINE_COMPILE exit=0 errorCodes={} affectedFiles=[]`.
- Same original APK80 source9462f8e,11 delivery assets; CL/raft log/lf four old 2-Nov folders read only. No Unity or Android phone acceptance. Source work completed; global INPUT, WATER/RENDER and game readiness NOT_READY (0/3) remain.
- No Unity/APK/OBB/XAPK, release, LFS, .meta/GUID, CL write, tasks or protected branches touched; next session fresh HEAD/Actions/peer read.
