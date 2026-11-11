# T4 scheduled session — mouse capture routing guard
session_id: 20261111T0335Z-T4-scheduled-input-acceptance-n7q3
origin: scheduled
baseline_sha: 2b80f4c1febdf3f3aff6b4bb96986aa9914b7014
scope_commit: 22ed2daa553f24f4af7e893804b53ea8f103d09c
test_commit: 3ad58d9b13fe4e164cba3ae281279850dca0c15b
work: prompt/coordination/clients/T4/work/INPUT-005/20261111T0335Z-T4-scheduled-input-acceptance-n7q3.md

## Result
Added tests/test_t4_mouse_capture_routing_guard.py, a source-only four-test regression guard for: non-MOVE callback observation without consumption; authored lock+real mouse eligibility and virtual touch exclusion; original Legacy Input first with captured fallback for LEFT/RIGHT/MIDDLE and wheel; release on pause/focus loss/disable and no keyboard event injection. This does not change game behavior, game assets, keyboard, .rgd, audio, Settings or T5 Resolution.

Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md and live T_TEAM protocols. Owner artifact 42058825739 remains accepted for world/save/reopen on that binary only. Latest owner 8 November CL indicates camera movement but buttons/wheel not working. Read actual AndroidPhysicalMouseCapture.cs and prior bridge doc. Native captured action staging and Legacy wrappers already exist: do not implement a second mouse injection system.

## Validation and limits
Fetched the live C# source through GitHub connector and checked the key callback pattern, action routing, release hooks and scroll axis presence with an independent JS regex probe: all true. Local Python test execution not possible because the container cannot resolve github.com to retrieve the repository; no CI or device test claimed. No Unity/Android build launched, no existing Actions cancelled. Test should run via `python -m unittest discover -s tests -p 'test_t4_mouse_capture_routing_guard.py'` from repository root; review results before integrating it into CI.

## Next
1. Execute the new source guard in a GitHub Actions or checked-out repository test context, without duplicating existing heavy workflows.
2. Compare current signed game source SHA to owner CL and collect `physical_mouse_capture_eligibility`, `physical_mouse_capture_requested`, `physical_mouse_captured_action_callbacks`, `physical_mouse_legacy_reader_evidence` markers on the same actual Unity build; distinguish Android callback, Legacy fallback and gameplay action.
3. Only patch a demonstrated missing stage. Preserve keyboard, original Raft cursor, touch and .rgd. Coordinate with T5 on unified mini lab and Resolution.
INPUT-005 remains OPEN / DEVICE_PENDING. NOT_READY 0/3.
