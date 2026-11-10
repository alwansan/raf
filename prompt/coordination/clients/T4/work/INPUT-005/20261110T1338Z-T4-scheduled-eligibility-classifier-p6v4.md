# T4 INPUT-005 scoped experiment
session_id: 20261110T1338Z-T4-scheduled-eligibility-classifier-p6v4
origin: scheduled
base_head: 36661a7ccbc8bd2279eb89a19ad4dfff9fd005a4
experiment_key: T4-INPUT005-ELIGIBILITY-TRACE-20261110
files: scripts/t4_diagnose_mouse_eligibility.py; tests/test_t4_diagnose_mouse_eligibility.py; this work file; own session file
hypothesis: existing capture gate telemetry distinguishes no authored lock / no Input System physical mouse / blocked focus / request without callback; existing escape classifier does not consume eligibility markers.
shared_resource: none; no Unity, APK, workflow, CL writes
nonoverlap: separate new analyzer and tests; no AndroidPhysicalMouseCapture.cs or T5 Resolution edits.
owner_device_fact: artifact 42058825739 entered/saved/exited/reopened world, not generalized.
validation: local Python unittest; static source-only and log-only, never device proof.
