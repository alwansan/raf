# T4 INPUT-005 scoped plan

session_id: 20261110T2042Z-T4-scheduled-r6p8
origin: scheduled
base_HEAD: 828e41cc7249eaf6632508f6c24546f366decd3e
experiment_key: INPUT-005-MOUSE-TRACE-SESSION-ISOLATION
scope: scripts/t4_mouse_boundary_trace.py; scripts/test_t4_mouse_boundary_trace.py; this work record; unique session record.
shared_resource: none; no Unity/CI build.

Hypothesis: T4_MOUSE_STAGE markers from separate app sessions may reuse Time.frameCount; current classifier groups by frame only, collapsing independent events and potentially creating false cross-stage correlation. Add optional session field, preserve legacy no-session behavior, and test collision isolation. This is source-only instrumentation analysis, not a phone fix. Keep keyboard, .rgd, audio, Settings, T5 Resolution unchanged.

Owner phone evidence: Artifact 42058825739 world entered/saved/reopened; physical mouse camera motion but clicks/scroll not proven. Do not overwrite this acceptance.
