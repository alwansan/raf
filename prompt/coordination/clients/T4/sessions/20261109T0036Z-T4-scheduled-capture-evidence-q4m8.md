# T4 scheduled session — 20261109T0036Z-T4-scheduled-capture-evidence-q4m8
origin: scheduled
identity: T4
scope_commit: ec6d7052d005ea61b0d4667ba91c1b52ccba5c96
baseline_sha: 278c1395fda36d3ff4ae602a0ec1f68dcc375f76
work: ../work/20261109T0036Z-T4-scheduled-capture-evidence-q4m8.md

## Verified evidence
- Owner docs/DEVICE_FEEDBACK_42058825739_AR.md: real device world entry, save, exit, reopen on artifact 42058825739; package publishing failure distinct.
- T4 MEMORY: genuine uncaptured Android mouse callback evidence 13 LEFT press/release pairs and 55 vertical scroll events in CL pinned 4680f5dc, **captured=false only**. Original game source adapter 20 Legacy Input call sites/12 files passed source-only CI42518143297, not phone proof.
- Current analyzer source read: physical_mouse_source requires actual source bits; explicit button edges require actionButton bits, ACTION_SCROLL for wheel; result device_success_proven false. ACTION_DOWN/UP actionButton=0 remains ambiguous, and buttonState during MOVE cannot establish edges.
- Shared build readiness r4: T5 Mini v0.2.13 CI42519487402 success; phone screenshot/captured evidence still pending. No duplicate Mini requested.
- GitHub branch HEAD at start 278c1395fda36d3ff4ae602a0ec1f68dcc375f76. Most recent listed Actions 42529039014 completed success on dcf9bc3; no gameplay proof from that status.

## Outcome and limitations
No game runtime, analyzer, CL, keyboard, .rgd, audio, Settings, T5 UI/Resolution or Unity workflow altered. Created isolated scoped work and session to prevent false mouse success. No new Android captured=true trace found in reviewed evidence; a signed full-game device test remains essential. INPUT-005 OPEN; LOCAL-005 success limited to original tested artifact; NOT_READY 0/3.

## Next concrete step
When owner exports T4-02 with captured=true and capture_request ON, replay ordered same-device DOWN/UP/PRESS/RELEASE with actionButton/buttonState and de-duplicate Activity/View; compare JNI callback to Unity Legacy Mouse0/1/2 and scroll on same signed game SHA. Only then implement edge inference or bridge correction. No need to rebuild existing Mini unless T5 identifies a compiled driver change.
