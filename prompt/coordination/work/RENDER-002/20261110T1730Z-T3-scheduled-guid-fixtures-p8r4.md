# T3 scope — 20261110T1730Z-T3-scheduled-guid-fixtures-p8r4
origin=scheduled; owner=T3; issue=RENDER-002; experiment=T3-GUID-FIXTURES-01

Read device report docs/DEVICE_FEEDBACK_42058825739_AR.md first. Phone world/save/re-entry proven only for artifact 42058825739. White hand/raft and square smoke remain open. Existing original/export evidence 41 materials, 227 TexEnv, 150 RGBA matches rules out blanket internal UV/tint loss on that scope, not shader or external texture issues.

## Scope
New independent file: tests/test_t3_guid_audit_regression.py. Existing scripts/t3_unity_guid_link_audit.py is read-only in this cycle. Hypothesis: static audit must distinguish same-tree resolution, omitted external targets, duplicate .meta GUID, null GUID, reversed fileID/guid order, and cross-reference contamination. This is a synthetic contract only, not real ZIP2 export or phone validation.

No shared build resources; no Unity/OBB/CI dispatch. T4 pointer and T5 resolution out of scope. Check newest branch before any subsequent edit, no force.

## Resume
Run python3 -m unittest discover -s tests -p 'test_t3_guid_audit_regression.py' on branch HEAD; then audit SHA-pinned actual source/export trees, classify unresolved GUID with full provider graph, link specific smoke particle renderer/material/shader. Preserve .meta/GUID and raw assets.
