# T4 scheduled checkpoint — 2026-11-09 12:39 UTC

- session_id: 20261109T1239Z-T4-scheduled-device-gate-h6r2
- origin: scheduled
- branch: feature/android-native-port only
- base evidence: previous T4 session 20261109T1142Z-T4-scheduled-capture-evidence-q4m8; prior work 20261109T1044Z-T4-scheduled-capture-request-observability-v2q9; prior authenticated original mouse bridge CI42518143297 and original device CL evidence pinned 4680f5dc.
- scope commit: 912043d75f241ace37ebe1d96ecaf3665b987cea
- original owner phone artifact: Actions 42058825739, source e9c358eda01785b65e4eb14f18723da426635628, limited OWNER_CONFIRMED world create/save/exit/re-enter. Distribution failed; do not conflate with later source.

## Verified and inference boundary

Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM/CHAT_AND_SCHEDULE_AR.md, PROMPT_AR.md, OPERATING_MODEL_AR.md and T4/MEMORY.md via GitHub connector. The 5 Nov device report points to pinned CL 520c4cf and screenshots, and documents successful world/save/re-entry with mouse cursor/system bars and rendering defects. The later T4 MEMORY records authentic CL 4680f5dc uncaptured mouse LEFT and vertical wheel events, but captured=false and no capture_request; this is not a captured-button or Unity gameplay acceptance result. Authenticated original source fallback 20 call sites/12 files and CI42518143297 source PASS; no signed game build/phone proof for this integration. The unified mini v0.2.13 CI42519487402 is not the full Raft game and does not close INPUT-005.

## Decision and next executable step

No new native build, no fake input PASS, no edit to shared T5 UI/Resolution. Avoid repeating the existing source-only mouse tests and acceptance matrix. Next evidence must pair, from **the same signed candidate and same session**, Android capture_request=ON and route=captured captured=true physical LEFT/RIGHT/MIDDLE press+release and V/H wheel with Unity Legacy Input consumer traces and visible gameplay responses; check camera pointer confinement, pointer restored in menu, keyboard, focus loss, and old .rgd save. If CL lacks this, classify NEEDS_INPUT rather than regression/failure. T5 owns shared mini APK and UI/Resolution; T4 owns game mouse bridge.

## Execution limitations

The local git HTTPS transport could not resolve github.com (DNS); the authenticated GitHub connector read source docs and created scope. No direct run enumeration or CL tree listing was available from tools in this cycle, and no local original game assets or Android hardware were available. Therefore no assertion of fresh CL content or currently running Actions is made. Work is evidence gate only; INPUT-005 remains OPEN, LOCAL-005 retains owner-confirmed old artifact acceptance, full game NOT_READY 0/3.
