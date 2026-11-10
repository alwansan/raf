# T4 scheduled checkpoint — 20261110T0643Z-T4-scheduled-eligibility-contract-m8q5
origin: scheduled
session_id: 20261110T0643Z-T4-scheduled-eligibility-contract-m8q5
resumed_from_sessions: 20261110T0545Z-T4-scheduled-capture-gate-e2c9; 20261110T0439Z-T4-scheduled-device-presence-g5k2
base_sha: de94af945c2ef98be68e4816c7c7bc1a87bfabb1
issue_id: INPUT-005
scope: prompt/coordination/work/T4/20261110T0643Z-T4-scheduled-eligibility-contract-m8q5.md
source_commit: be31b5532a842544bf48a7ad744c5081d21cbd8c
test_commit: 597faee02c3ff9f2a8f9aa447c7c15d6a7c6f318
status: source_contract_added_unexecuted

## Evidence and change
Owner's 5 Nov signed artifact 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628) entered world, saved, exited and reopened. This remains limited OWNER_CONFIRMED evidence for that artifact; preserve original .rgd and world flow. Read docs/DEVICE_FEEDBACK_42058825739_AR.md, owner requirements and team protocol. Current source HEAD at start de94af945c2ef98be68e4816c7c7bc1a87bfabb1. Previous T4 pointer-capture eligibility telemetry source be31b553 has CI42763994149 success on Python trace classifier, NOT phone or Unity compile proof.

Added four new source-level regression tests at tests/test_t4_capture_eligibility_contract.py: real physical mouse gate and virtual touch exclusion; exhaustive four-bit eligibility truth table; transition-only telemetry and unknown Android grant; Escape keyboard and capture release/request/probe preservation. Test file was committed with content-SHA updates; current AndroidPhysicalMouseCapture.cs blob 99b3926bf5f3352c0e38aad858eb834be39472a8. Read-only JS source assertions confirm 4 tests present and exact gate, marker, escape, request and probe anchors. **Python unittest not executed**: runtime cannot resolve raw.githubusercontent.com, and connector-fetched source cannot be mounted automatically into shell. No CI dispatched, no APK build, no phone evidence. Test assertions need actual CI before calling verified.

## Coordination and limits
No changes to Android input implementation, keyboard, touch, .rgd, FMOD, Settings, or T5 Resolution and shared Mini. No fake device success. CL prior T4 mini tests still require physical captured mouse and actual game consumption; INPUT-005 OPEN. Full game readiness NOT_READY 0/3.

## Next
Run `python -m unittest discover -s tests -p test_t4_capture_eligibility_contract.py -v` in an existing source-only CI or accessible checkout, fix any failing contract assertions; no duplicate heavy workflow. Then inspect next signed game JSONL for physical_mouse_capture_eligibility + request/callback + legacy reader + real game button/wheel effects, preserving keyboard and world save regression. If inputSystemPhysicalMouse=false despite real Android mouse, investigate source-independent Android InputDevice detection without admitting virtual touch. T5 owns Resolution.
