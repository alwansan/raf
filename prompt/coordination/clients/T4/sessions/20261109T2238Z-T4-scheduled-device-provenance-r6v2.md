# T4 session 20261109T2238Z-T4-scheduled-device-provenance-r6v2

origin=scheduled
identity=T4
branch=feature/android-native-port

## Restored
Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, owner requirements, STATUS, T_TEAM coordination and T4 memory. Prior run 42704145152 was reported successful for 71 existing regressions, while six later envelope tests awaited independent confirmation. Previous T4 capture correlator and its tests inspected directly. Owner-confirmed real device success for world entry/save/exit/reentry remains tied ONLY to run 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628), not later game source.

## Completed
Published independent scope record at prompt/coordination/work/INPUT-005/T4-20261109T2238Z-T4-scheduled-device-provenance-r6v2.md in commit a211194a1173d5b768d498d7626a76a1b46b9f0b. Confirmed correlator intentionally sets device_pass=false and cannot prove actual game clicks. Avoided duplicate workflow and T5 overlap. No Unity/game changes or APK release.

## Limits
Could not independently confirm newest Actions queue/results or inspect all fresh CL files; no new phone log or signed game test was available to this run. No mouse gameplay fix claimed. Work record is an evidence/acceptance handoff, not implementation.

## Next
Obtain same signed game candidate package provenance + single chronological process-local JSONL with captured=true LEFT/RIGHT/MIDDLE and V/H wheel; correlate Unity getter slots, check game response, keyboard and focus, then run world save/reload regression. Confirm six newest envelope tests in CI. Do not request duplicate full Unity build. INPUT-005 OPEN; LOCAL-005 device success retained; NOT_READY.
