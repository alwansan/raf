# T3 session 20261110T2230Z-T3-scheduled-guid-hash-e7q3
origin=scheduled
issue=RENDER-002
status=SOURCE_DIAGNOSTIC_COMMITTED_TESTS_NOT_EXECUTED
branch=feature/android-native-port

## Evidence read
Owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md: source e9c358eda01785b65e4eb14f18723da426635628, artifact 42058825739 confirms world/save/exit/reentry only. White hand/raft, square smoke, missing lighting remain OPEN. CL pinned at 520c4cf409aa20a4db54ff80ed87d8807d9cba57; image URLs and error summaries supplied by report. No fresh image binary or full CL log fetched in this cycle. Current requirements dated 8 Nov include shared mini lab; T4 mouse, T5 resolution/layout. Read AGENTS, CURRENT_OWNER_REQUIREMENTS, STATUS, T_TEAM chat/schedule, PROMPT, operating model and prior T3 session 20261110T2133Z-T3-scheduled-guid-coverage-h6p2; state.json is older chat checkpoint.

## Registered work
prompt/coordination/work/RENDER-002/T3-20261110T2230Z-T3-scheduled-guid-hash-e7q3.md committed at 2cb1091f47fb2d486b542b2d0306fd7607042a01. Scope isolated from game assets and other T workers; no shared CI/Unity/GPU resource.

## New work
- scripts/t3_unity_guid_link_audit.py: unresolved GUID references now include SHA256 prefix16 per source extension, permitting repeated missing-in-supplied-tree references to be joined without publishing raw GUIDs. Existing aggregate counts and size-limit coverage retained. Commit c8f06c7b47a19da31256aa96389903270c0c7fba.
- tests/test_t3_guid_audit_hashed_unresolved.py: two fixtures check cross-source grouping, resolved exclusion, raw GUID privacy and empty inventory. Commit c9bcac27263f4513b9e910cd8cbdc464553c9bf2.
- Test suite not executed; no PASS or Android visual proof claimed. No new full APK/OBB/Unity CI dispatched. No proprietary resources or .meta changed.

## Resume
Run python3 -m unittest discover -s tests -p 'test_t3_guid_audit_hashed_unresolved.py' plus existing GUID tests on live HEAD. If PASS, run authenticated ZIP2/export limited tree scan and capture only aggregate + hashed joins; find smoke prefab -> material -> shader/texture, compare blend/alpha/ZWrite and image. Confirm full tree coverage and distinguish unresolved-in-supplied-tree from missing game resource. Previous authentic 41-material/227-TexEnv same-export match rules out internal texture UV loss for that bounded sample only. RENDER-002 OPEN; NOT_READY 0/3. No claim of current HEAD or Actions state beyond fetched files.
