# INPUT-005 T4 independent work 20261111T0543Z-T4-scheduled-route-a7m4
origin=scheduled
baseline_sha=6ebe24010efe2ab98e73f830ad41b36b96061b88
experiment_key=T4-CAPTURE-CALLBACK-SEMANTICS-20261111
scope=tests/test_t4_capture_callback_semantics.py; prompt/coordination/clients/T4/sessions/20261111T0543Z-T4-scheduled-route-a7m4.md
shared_resource=none; no Unity or mini build
hypothesis=source callback should never consume nonmove events, should forward genuine physical source actions to epoch-gated staging, and keyboard must retain Unity original path. Existing tests assert selected tokens but not their combined contract.
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md world save/reopen confirmed only for artifact 42058825739; OWNER_FEEDBACK_2026-11-08_AR.md camera improved, buttons/wheel not device-confirmed.
T5 owns resolution and unified mini; no modifications to shared native input implementation or .rgd.
