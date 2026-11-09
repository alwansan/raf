# T4 scheduled checkpoint — CL captured mouse evidence

session_id: 20261109T0951Z-T4-scheduled-cl-capture-gap-m6q2
origin: scheduled
base_sha: bf2431b389ff8f5141b4d6cd08315c5f035f9531
work_commit: 164058742d07a2707950bfe302df940a01376826
status: evidence_gap_confirmed; INPUT-005 OPEN

Read owner docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, current requirements, STATUS, team protocols and T4 memory. Owner confirmed playable local world, save and reopen on artifact 42058825739; packaging publish failed, source e9c358eda01785b65e4eb14f18723da426635628. No regression assertion on newer build.

Fresh CL main read-only inspection: old T4 builtin mouse export (2063 bytes) and shared-20261108-232759-468049775 export (33429 bytes, APK 0.2.13-shared, source e7a6248b0d0c14b9772bd52f3bbdc5cf22fa9b9a) contain no capture_request, captured=true, route=captured, ACTION_BUTTON or ACTION_SCROLL. Their automatic case completion cannot validate physical pointer capture. Previous CL captured=false LEFT and vertical wheel evidence remains separate. No new phone/game proof; do not infer physical failure from absence of actions.

Original ZIP2 Legacy Input adapter source-only CI42518143297 passed, but actual Unity consumption under captured=true untested. No new CI launched; no game code, keyboard, .rgd, audio, Settings, touch, UI or Resolution edited. T5 owns UI and Resolution; no resource contention. Branch read bf2431b389ff8f5141b4d6cd08315c5f035f9531 before work. Work path prompt/coordination/clients/T4/work/20261109T0951Z-T4-scheduled-cl-capture-gap-m6q2.md.

Next: T4-02 physical mouse pointer capture ON and captured=true callback, actual LEFT/RIGHT/MIDDLE press/release, vertical/horizontal scroll, Unity Legacy Input correlated same signed candidate; verify focus loss and keyboard retained. Preserve LOCAL-005 device success, INPUT-005 OPEN, full game NOT_READY.
