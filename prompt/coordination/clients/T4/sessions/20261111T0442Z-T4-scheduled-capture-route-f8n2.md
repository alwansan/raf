# T4 scheduled — captured action contract
session_id: 20261111T0442Z-T4-scheduled-capture-route-f8n2
origin: scheduled
resumed_from_session: 20261111T0335Z-T4-scheduled-input-acceptance-n7q3
base_sha: 2234733f (last prior T4 checkpoint; live branch advanced)
scope_commit: 3df1960c2ba9edde693fc0ed6cc0119b7edbae34
test_commit: fe0a7e9aa373de8b65f8c3ce0f0522edc7cf44ea
correction_commit: 81e16a4ab08fcadf9cef05a3dabe301048b556b2
work: prompt/coordination/clients/T4/work/INPUT-005/20261111T0442Z-T4-scheduled-capture-route-f8n2.md

## Evidence
Read 5 Nov phone report, 8 Nov owner feedback, current AndroidPhysicalMouseCapture.cs, prior T4 test/session and coordination. Phone world/save/reopen success on artifact 42058825739 remains confirmed for that binary; newer 8 Nov report confirms relative camera motion but no LEFT/RIGHT/MIDDLE/scroll. No source-only claim overrides device results.

## Deliverable
Added tests/test_t4_captured_action_contract.py with three independent source contract tests: Android captured non-MOVE event fields and non-consumption, callback-to-buttonWheel-to-Legacy reader snapshot route, and reset on lost capture. Corrected test delimiters immediately in 81e16a4. This is a guard, NOT a fix for missing click/scroll. It preserves keyboard, touch, cursor, original .rgd, sound, Settings and T5 Resolution. No Unity build or CI dispatched.

## Validation/limits
GitHub connector fetched source and published test; no executed Python/CI test or Android device confirmation in this cycle. Container DNS cannot resolve github.com, so local checkout was unavailable. No reliable live Actions queue enumeration exposed by connector; do not claim no concurrent runs. Test command: python -m unittest discover -s tests -p 'test_t4_captured_action_contract.py'.

## Next
Run new source tests in existing lightweight CI or checkout. Compare device callback markers physical_mouse_captured_action_callbacks and physical_mouse_legacy_reader_evidence for the SAME signed candidate and session; if callbacks absent investigate View listener/dispatch route; if callbacks present but fallback reader absent investigate Raft callsite replacement and Unity frame sampling. Coordinate T5 unified mini APK, no duplicate native build. INPUT-005 OPEN; NOT_READY 0/3.
