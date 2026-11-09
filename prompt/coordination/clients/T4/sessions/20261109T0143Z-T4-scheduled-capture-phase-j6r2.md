# T4 — capture phase evidence guard
session_id: 20261109T0143Z-T4-scheduled-capture-phase-j6r2
origin: scheduled
resumed_from_sessions:
- 20261109T0036Z-T4-scheduled-capture-evidence-q4m8
- 20261108T1958Z-T4-chat-legacy-button-wheel-bridge-y8m2
base_sha: cf764d7671efb58dc57f5952bd1c2875e97ec504
work: prompt/coordination/work/INPUT-005/20261109T0143Z-T4-scheduled-capture-phase-j6r2.json
issue: INPUT-005 (OPEN)

## Evidence
- Owner docs/DEVICE_FEEDBACK_42058825739_AR.md: original Artifact 42058825739 entered world, saved, exited, reopened; publish failure is distinct; LOCAL-005 regression protection remains.
- Owner CL mouse evidence pinned 4680f5dc: physical LEFT 13 press/release pairs and 55 VSCROLL, all captured=false; does not prove captured=true or Unity input.
- T4 authentic ZIP2 legacy adapter source CI42518143297 SUCCESS (20 call sites / 12 files), not a phone game validation.
- At read HEAD cf764d7671efb58dc57f5952bd1c2875e97ec504, T5 SAF source CI42547068324 in_progress. No duplicate workflow dispatched. T5 owns shared mini and UI/Resolution.
- Analyzer had a false-evidence risk: after capture_request=ON, a source-identified input lacking captured= field was silently classified as phase on. Request does not imply granted capture.

## Engineering outcome
- Scoped reservation commit 08ab1aaf8ae275b5e24cd717bfdbf12ac4ab0066.
- Analyzer fix commit acedf8264c608c438a062b5cb1745860670172c1: only explicit captured=true becomes on, captured=false becomes off, absent/invalid flag becomes unknown. This avoids conflating requested and accepted pointer capture.
- Regression test commit 659ef28b65c6ae65c869a7d0cf4fbffdde6be16d, file test_t4_capture_phase_evidence.py, covering missing captured flag and explicit true/false. Test has not yet been run by CI or on device; no runtime fix claimed.
- No game source, .rgd, FileManager, keyboard, camera, T5 Resolution, touch, audio, Settings, shared Mini or CL modified. No new Unity/Android build.

## Follow-up
Run `python -m unittest test_t4_capture_phase_evidence` in source checkout; capture actual ON/granted and LEFT/RIGHT/MIDDLE + vertical/horizontal scroll under pointer capture from T4 unified Mini, then compare with Unity Legacy Input in same signed game candidate. Keep INPUT-005 OPEN and NOT_READY 0/3. Do not infer success from synthetic regression.
