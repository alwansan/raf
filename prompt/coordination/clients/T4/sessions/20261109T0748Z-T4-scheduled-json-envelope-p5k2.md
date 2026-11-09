# T4 scheduled — JSONL envelope validation (2026-11-09 07:48 UTC)

- session_id: 20261109T0748Z-T4-scheduled-json-envelope-p5k2
- origin: scheduled
- branch: feature/android-native-port (only write branch)
- original HEAD: db95391aecfd7d73d5a4dad8bab1f506d10df533
- observed HEAD after writes: 7dd83c543e0c20c0084983e81e4b2261971831e8
- scope: INPUT-005; scripts/t4_analyze_mouse_lab_routes.py and tests/test_t4_analyze_mouse_lab_routes.py, no shared resource.
- work: prompt/coordination/clients/T4/work/INPUT-005/T4-20261109T0748Z-scheduled-json-envelope-p5k2.json

## Evidence / continuation
Owner [device feedback](../../../../docs/DEVICE_FEEDBACK_42058825739_AR.md) confirms world entry/save/exit/reopen on artifact 42058825739, source e9c358eda01785b65e4eb14f18723da426635628, not the later signed input adapter. CL/test latest visible commit 24a677fc8fa4749c0bcf8a3cac01fa80b1641c86 (2026-11-08 22:03 UTC); existing T4 CL mouse evidence only proves uncaptured callbacks, not captured Unity Legacy buttons. Keep LOCAL-005 and INPUT-005 open. T5 owns shared Mini/Resolution/three UI buttons. No Unity builds canceled or repeated.

## Engineering change
- Work claim commit f692414f0d79ab38f2d0dc6c79860957f21f382d.
- Fix commit 82db68b8b056a02eb0a800202e3b0d3b6962da81: reject valid JSON records that are not objects (list, null, scalar) instead of raising AttributeError and aborting evidence analysis; reject explicitly malformed captured flags instead of assigning to unknown.
- Regression commit 7dd83c543e0c20c0084983e81e4b2261971831e8: two tests including 5 malformed-but-valid JSON envelope examples followed by a genuine captured button, and two invalid capture flags with one legitimately unknown callback.
- Validation: source change and tests committed; Python execution NOT verified here because container network DNS prevents retrieving current branch. Do not claim test PASS or device success.

## Next
Run `python -m unittest tests.test_t4_analyze_mouse_lab_routes` in existing source-only CI or local checked-out repo, without duplicating running workflows. Acquire real captured=true Android callback and Unity Legacy Input consumption on same signed Raft game build. Preserve keyboard, cursor transition, .rgd, audio, Settings, touch; no XAPK readiness claim.
