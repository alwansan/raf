# T3 session 20261111T2238Z-T3-scheduled-fileid-k7m4
origin=scheduled
issue_id=RENDER-002
resumed_from_sessions=20261111T2133Z-T3-scheduled-texslot-identity-v9k2; 20261111T2026Z-T3-scheduled-pair-audit-q8n4
base_sha=4ee7f5a6dfec0a7e88ceedd0f3e6c873aeb57664
scope=isolated Python serialized material texture reference identity; no resource/build overlap
source_change=5ca91a8ec973641c32260f8f3bd1a4418c3da818
regression_change=9930a38dd09147c80561676f7d670b3c7e6e4dda
evidence=Prior comparison used only (slot, GUID); same GUID may point to distinct Unity subassets by fileID or type. New comparator uses canonical (fileID,guid,type) within each slot. Added two source-free controls: changed fileID with same GUID must differ; reordered reference fields must match.
verification=Code and tests committed; actual Python unittest not executed in this environment. No original ZIP2 paired tree or device test. Source-level hypothesis only; no visual repair claim.
actions_observed=43112757300 GT scene inventory failed at 4ee7f5a6; 43112754830 runner guard succeeded; 43098764336 T5 Settings workflow queued. None is proof for this change; do not duplicate or cancel.
owner_feedback=42058825739 entered/saved/reentered world; white raft/hand and square smoke remain open. CL fixed pin 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
next=Run python -m unittest tests.test_t3_material_dependency_pair_audit (or unittest discover) in checked-out repository; then compare authenticated same-export original/export material pointers including fileID/type and investigate external 25 references. Keep RENDER-002 OPEN/NOT_READY.
