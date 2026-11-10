# T4 checkpoint — 20261110T1135Z-T4-scheduled-device-evidence-m4q8
origin: scheduled
issue: INPUT-005 OPEN; LOCAL-005 OPEN
base_sha: 9bc14b73295fc139ffbf0709c4d044cbd960b99e
scope_commit: 67e631d8f3058c4956f3f97e641db53769a11bd1
resumed_from: 20261110T1036Z-T4-scheduled-native-device-gate-b7q2; 20261110T0939Z-T4-scheduled-gate-source-audit-r6m2; 20261108T1958Z-T4-chat-legacy-button-wheel-bridge-y8m2
origin evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57; source run 42058825739 e9c358eda01785b65e4eb14f18723da426635628

## Newly checked facts
- Read current source AndroidPhysicalMouseCapture.cs on branch and verified Android captured listener records button press/release/scroll and legacy wrappers exist; button/scroll listener returns false to preserve Unity original handler. Presence gate is Unity InputSystem Mouse.all, with virtual touch excluded. This remains a candidate failure point, not a confirmed Android bug.
- Read live CL/test/shared-20261109-233132-554663211/summary-20261109-233132-554663211 (1).json: app_source=731d7a68bb3826b348d0314f694737b522e92976; pack SHA256=9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6. All T4-01 through T4-09 are NEEDS_INPUT with observed 'User action, mouse/file or judgment is required'. No PASS or FAIL for physical captured mouse is evidenced by these nine cases. CL folder contains T3 PNGs, shared events, T2 traces; not a signed Raft game mouse trace.
- Actions recent branch list shows no active/queued among eight most recent; T4 classifier source CI42776921454 completed SUCCESS. No repeat dispatch. Head after isolated scope commit 67e631d8f3058c4956f3f97e641db53769a11bd1.
- Owner phone proved local world enter/save/exit/reopen on 42058825739. Preserve .rgd format and world compatibility; this success is not a new full-game mouse pass. No changes to T5 Resolution, UI or shared mini lab.

## Falsifiable next-game trace decision table
1. authoredLock=false or focus=false or paused=true: no request expected. Do not bypass original authored cursor state; keyboard/Escape and focus-release behavior take precedence.
2. authoredLock=true, focus=true, paused=false, physicalPresent=false while native InputDevice SOURCE_MOUSE is independently proven: device discovery gate mismatch. Only then consider native capability-filtered presence fallback; exclude touchscreen, virtual RaftAndroidTouchLeft and touchpad ambiguity.
3. physicalPresent=true, capture_request attempted, hasPointerCapture=false: Android View/focus/capture denial or wrong-view epoch. Compare view identity and retry/loss logs; don't rewrite Legacy Input consumers.
4. captured callback with authentic button/wheel but legacyFrameInputBuffered=0: native event classification/frame staging gap. Inspect source/deviceId, epoch, action button, held mask, event time and frame ordering.
5. captured callback and buffered frame >0 but getterCalls=0: original game consumer route not invoked in that scene; test authored game UI/world input call sites. If getterCalls>0 but positiveFallback=0 inspect frame sample ordering. If positiveFallback>0 and gameplay action absent, investigate UI hit-testing, cursor position/lock and input ownership.
6. Captured clicks working but Android bars/black cursor persist: separate WindowInsets/cursor visibility concern; coordinate T5 safe-area/resolution and do not conflate display with click pipeline.

## Evidence limits / handoff
No phone access, no new signed game APK, no original Raft gameplay execution, no verified pointer capture or click pass. Source-only tests do not close INPUT-005. No CI/build requested, no original assets exposed. Next owner test needs fresh signed game trace tagged APK/OBB manifest and original scene, keyboard/Escape, focus/reconnect, LEFT/RIGHT/MIDDLE and vertical/horizontal wheel, and authored-lock/capture eligibility plus legacy getter markers. Compare with existing shared mini only as Android driver evidence, not game evidence. Keep LOCAL-005 OPEN and NOT_READY 0/3.
status: completed_evidence_boundary; no behavioral code change
