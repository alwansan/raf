# A7 INPUT-005 — touch pointer re-enable lifecycle repair

Date: 2026-11-03T15:08:56.691Z; owner `raft-20261103T145805Z-a7c2f809`; source `7517f30fd7010af11dac6444f7c0b3d3dadd5064`.

**Defect:** actual `AndroidTouchPointer.OnDisable()` calls `Suspend(true)`, but prior `OnEnable()` never reset the flag, so a re-enabled component consumed raw gameplay touch events without dispatching gameplay commands.

**Fail-first evidence:** first test-only [CI41659146129](https://github.com/alwansan/raf/actions/runs/41659146129) failed a harness-only C# local name collision (CS0128); fixed at [34dcdb06](https://github.com/alwansan/raf/commit/34dcdb06bc401cad3ec8f8d42f335aadc2782bff). Corrected strict C# harness extracts the exact production `OnEnable/OnDisable/Suspend/OnEvent` methods. Genuine [RED41659588079](https://github.com/alwansan/raf/actions/runs/41659588079) failed `MULTITOUCH_ROUTE: reenable-clears-stale-suspension`.

**Repair:** [7517f30fd7010af11dac6444f7c0b3d3dadd5064](https://github.com/alwansan/raf/commit/7517f30fd7010af11dac6444f7c0b3d3dadd5064) sets `suspended = false` at the start of each `OnEnable` before re-registering input handlers; only the authored Android pointer source is changed in production.

**Success:** [platform41659802113](https://github.com/alwansan/raf/actions/runs/41659802113) COMPLETED SUCCESS, actual C# raw routing/lifecycle checks **17**, gesture/500ms checks **446**, LEFT Mouse0/physical mapping checks **53**. [offline41659802250](https://github.com/alwansan/raf/actions/runs/41659802250) COMPLETED SUCCESS with `RAFT_OFFLINE_COMPILE exit=0 errorCodes={} affectedFiles=[]`.

**Limits:** strict Unity event doubles rather than actual Unity Editor/InputSystem/UGUI/Android; no native/phone test. Old APK80/source9462f8e does not include the fix. No asset/meta/GUID, water/shader, native request/build, release, CL or scheduler changes. Scoped A7 work completed; game remains NOT_READY, 0/3 readiness reviews.
