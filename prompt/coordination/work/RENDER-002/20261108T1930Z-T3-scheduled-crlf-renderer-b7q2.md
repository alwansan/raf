# T3 RENDER-002 scope
- session_id: 20261108T1930Z-T3-scheduled-crlf-renderer-b7q2
- origin: scheduled
- baseline_sha: d1f6635838df341d88a832ffe2b6bf4943847f31
- resumed_from: 20261108T1852Z-T3-chat-png-integrity-k8m2 and 20261108T1826Z-T3-scheduled-ledger-id-r4c9
- hypothesis: Unity YAML CRLF document headers are missed by DOC regex anchored to '$', silently undercounting ParticleSystemRenderer and local Material anchors. This is a source audit integrity issue, not a claimed phone graphics fix.
- experiment_key: T3-particle-crlf-boundary-v1
- resource: T3 particle YAML audit only, no shared Unity/GPU/mini APK.
- intended files: scripts/t3_particle_renderer_yaml_audit.py, tests/test_t3_particle_renderer_yaml_audit.py, own scope/session.
- coordination: no changes to T1/T2 water, T4 input, T5 resolution or shared mini lab. CI currently active on platform workflow; no new workflow request.
- evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; prior T3 synthetic particle tests; source DOC regex inspected at baseline.
- status: scoped; expected head recheck before edit.

## Observed outcome
- CRLF-only hypothesis rejected: original DOC regex already consumes CR via its optional whitespace branch. No unsupported claim of CRLF failure.
- Independent boundary defect found: UTF-8 BOM at the start of a file prevents first DOC header matching, losing a first ParticleSystemRenderer silently. Fixed by utf-8-sig decoding (eff0e67f8e5a2ab3a23e8e975871507e170269ad) and added BOM+CRLF regression (21c07e7027f176ae31d7e68f584973aff056c201).
- This only affects diagnostics; no original Raft material/shader was changed. CI test completion pending; no Unity/mini APK launched.
- next: confirm test run, then inspect authentic ZIP2 particle chain and CL visual evidence, not more synthetic changes without source proof.
