# T4 scheduled session — 20261108T0044Z-T4-scheduled-retry-telemetry-q6p2

- origin: scheduled
- baseline HEAD: 5a6c1d26c27a701febbc68579ab6dae87e64ff2d
- owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; phone Artifact 42058825739 source e9c358eda01785b65e4eb14f18723da426635628 confirmed world enter/save/exit/reenter; package publication failed. Preserve this limited device result and .rgd compatibility.
- inherited checkpoint: clients/T4/sessions/20261107T2343Z-T4-scheduled-capture-retry-audit-v5n2.md; prior 17 classifier tests CI 42416699458 successful on older source.
- scope: INPUT-005 physical mouse retry visibility only; T5 owns three buttons and Resolution. No touch/keyboard/Settings/audio/world changes.
- diagnosis: RequestCapture() increments epoch every 1.5s when nativeCaptured remains false, but previously logged physical_mouse_capture_requested only for first request. This prevents attribution of subsequent attempts.
- implementation: commit 86a4b488ac533ccf2429776e166edf9a02df6a79 adds bounded physical_mouse_capture_retry markers for attempts 2,4,8,...; counter resets on ReleaseCapture. Retains original first marker, listener/epoch/capture logic, and no raw input payload.
- tests: commit d835bd7c0db43aa4d4d52993a4485b3473a99011 adds 3 source-contract unittest cases; not yet executed on CI. Static source assertions were checked before publishing; no runtime verification.
- work record: prompt/coordination/work/INPUT-005/20261108T0044Z-T4-scheduled-retry-telemetry-q6p2.json. No native build, CI dispatch, releases or cancellations.
- next: execute cheap Python tests (or attach to existing T4 workflow after coordination), inspect phone logs from a build containing this instrumentation, then fix confirmed runtime capture fault. INPUT-005 OPEN; no claim that pointer capture or Raft cursor works on phone.
