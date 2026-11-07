# T4 scheduled — physical mouse recapture audit
- session_id: 20261107T1138Z-T4-scheduled-capture-rearm-v4n8
- origin: scheduled
- base_sha: 44162b6c33f19aeb8e01d70594c065584228e6ef
- scope_commit: dbf7c79a7efe252fb3a631a6bb53a9fdeaad9a8f
- resumed_from_sessions: 20261107T1040Z-T4-scheduled-mouse-escape-h7k2; 20261107T0841Z-T4-scheduled-immutable-mouse-stage-r6p2
- work: prompt/coordination/work/INPUT-005/T4-20261107T1138Z-T4-scheduled-capture-rearm-v4n8.json
- issue: INPUT-005 OPEN; LOCAL-005 OPEN; NOT_READY 0/3

## Source-derived discriminating contract
Read owner feedback first: the owner's 42058825739 artifact successfully entered a world, saved, exited and reopened. That proves neither current physical mouse capture nor current package installation. AndroidPhysicalMouseCapture.ApplyCursorLock(Locked) is the explicit original-author-intent arm; Update's Escape key branch clears originalLockIntent before calculating shouldCapture. If original game code does not call the adapted ApplyCursorLock(Locked) after closing pause, physical capture cannot resume even with a connected physical mouse. Conversely, a later call should rearm it, so no unconditional reacquire patch is justified without original control-flow or device evidence. Native View.requestPointerCapture is asynchronous: requested=true alone is not nativeCaptured=true; only successful View capture/probe and motion samples justify relative-axis substitution.

## Distinct test discriminators
A) Game->Escape->menu: expect release, native release outcome and usable Raft menu pointer; keyboard Escape still functions. B) Menu->game without mouse reconnect: require a new capture request and subsequent relative samples, then continuous camera movement beyond display edges. C) Repeat with app focus loss/recovery and unplug/replug: no stuck capture or touch/keyboard interference. D) Confirm .rgd save/reopen separately; do not turn source tests into phone acceptance. A log with release but no later capture request suggests lost authored lock intent; a request without relative events suggests native capture/View/source delivery, not necessarily missing authored intent. If no release appears, first check focus and cursor state. Need immutable signed APK/OBB source mapping and device logs before attributing cause.

## Observations and limits
- GitHub HEAD checked: 44162b6c33f19aeb8e01d70594c065584228e6ef; recent workflow runs 42365737052 and 42365731144 completed success on different source SHAs. No new Unity workflow dispatched.
- Source inspected: android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs; existing original-axis adapter scripts/t4_adapt_original_mouse_axes.py. Existing lock cardinality evidence is 4 X / 4 Y / 2 lock sites, not proof of the menu return path.
- CL is read-only; owner report points to pinned CL evidence, but no new on-device logs were reproduced in this run.
- No code or .meta/GUID/.rgd modifications, no new APK, no native/device test, no false claim of recapture fix. T5's Resolution/button placement and delivery remain separate.
- Next useful implementation step: establish the original authored pause->resume cursor-lock assignment (or instrument an Android-only state transition diagnostic) and distinguish missing rearm from Android View failure. Coordinate with T5 on package provenance only; avoid duplicate native runs.
- Result: bounded source audit/checkpoint; conditional bug remains unconfirmed.