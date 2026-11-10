# T4 INPUT-005 — boundary evidence scope
session_id: 20261110T1835Z-T4-scheduled-mouse-boundary-q7m4
origin: scheduled
base_head: 5337664c7ba1fd813bc11a2e134e18a62e74c43f
owner_device_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md
prior_session: prompt/coordination/clients/T4/sessions/20261110T1736Z-T4-scheduled-cl-evidence-j8p2.md

## Scope and hypothesis
Independent source-only work: add a bounded native-to-Unity mouse event correlation helper under scripts/t4_mouse_boundary_trace.py. No modifications to AndroidPhysicalMouseCapture.cs, Unity, Resolution, T5 mini lab, keyboard, .rgd, assets or shared CI. Experiment key INPUT-005-BOUNDARY-TRACE-20261110T1835Z. Shared resource: none.

Hypothesis: camera relative motion already works on device while left/right/middle/wheel do not; only a time-bounded event-level trace can distinguish Android delivery from Unity legacy state and Raft consumer failure. Never infer success from missing logs. Inputs must be anonymized text logs; do not publish game payloads.

Success criterion: helper classifies presence/absence of each stage separately and flags incomplete evidence, with self-test. No phone/gameplay claim.
