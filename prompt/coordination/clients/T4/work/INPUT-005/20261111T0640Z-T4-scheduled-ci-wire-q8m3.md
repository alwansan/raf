# T4 INPUT-005 scoped work 20261111T0640Z-T4-scheduled-ci-wire-q8m3
origin=scheduled
baseline=d485f212e14c43e2fbc1083e846b9d9321922f7f
experiment_key=T4-CAPTURE-CONTRACT-CI-20261111
shared_resource=none; cheap source-only workflow; no Unity, native, APK or shared lab build
files=.github/workflows/raft-t4-mouse-trace-classifier.yml; this work record; own session file
hypothesis=New tests/test_t4_captured_action_contract.py and tests/test_t4_capture_callback_semantics.py were added in prior scheduled sessions but omitted from the classifier workflow's sparse checkout and execution, so no CI evidence exists for them.
method=Add only those two tests to existing sparse checkout, push paths and python compilation/unittest, preserving existing tests and avoiding a duplicate workflow. Do not modify game input, touch, keyboard, Resolution, save or settings.
owner_phone=42058825739 confirms world create/save/exit/reopen only; game mouse LEFT/RIGHT/MIDDLE/scroll still unconfirmed. CL 8 Nov mini uncaptured physical LEFT/wheel evidence cannot prove captured game input.
status=planned
