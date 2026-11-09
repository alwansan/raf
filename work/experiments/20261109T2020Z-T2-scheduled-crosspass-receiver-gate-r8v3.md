# T2 WATER-001 — crosspass receiver/alias gate
session_id: 20261109T2020Z-T2-scheduled-crosspass-receiver-gate-r8v3
origin: scheduled
baseline_sha: e39494e629fcd0100ae29552951e08a6359be45e
issue: WATER-001 OPEN / NOT_READY 0/3
status: scoped_evidence_review; no shader edits
experiment_key: T2_WATER001_original_pass0_field_vs_pass1_return_indirect_alias_gate_v1
resource_key: T2-original-FoamBlitOriginalProducers-Cecil-source-only
intended_files: work/experiments/20261109T2020Z-T2-scheduled-crosspass-receiver-gate-r8v3.md; clients/T2/sessions/20261109T2020Z-T2-scheduled-crosspass-receiver-gate-r8v3.md
shared_resource: none

## Verified before scope
Owner device feedback 42058825739 establishes world enter/save/re-entry but not water restoration. Latest T2 chat work at prompt/coordination/clients/T2/sessions/20261109T2002Z-T2-chat-foam-declared-field-flow-c9n4.md reports authenticated CI42690309016 SUCCESS (19/19 privacy tests and Cecil selftest), original relation field_no_match_with_null. Verified Actions list independently confirms SUCCESS at SHA 6f09eddcf788050035a767d21999c75a6ebebdc1. This proves only no *direct same declared field token* among analyzed return paths, not distinct heap textures. Pass1 reachable return includes explicit null literal but does not prove runtime null. T3 canonical ledger summary CI42691146976 failed at regeneration step; its historical T3 event identity is outside this T2 scope. Shared mini-lab CI42691251220 failed at Validate shared pack and readiness, unrelated to T2 original CIL acceptance; do not duplicate or interfere with T5.

## Next falsifiable engineering experiment
For original pass0 destination receiver and pass1 callee field-return receiver, extract bounded CIL producer provenance with method token + field token + receiver category (this/local/arg/field/call/unknown), preserving branch-join uncertainty. Do not compare field tokens alone across different receiver objects. Accept alias proof only with verified same receiver and complete value flow, including intervening writes and frame timing; otherwise return unknown/indirect_alias_not_proven. Add synthetic tests for same field on different receivers, distinct fields pointing to same object, conditional null, and nested getter; then run pinned original SHA in existing T2-only CI. No raw original IL in public outputs. Do not edit T3 shaders, T4 input, T5 mini APK or common status while scopes overlap.

Result this cycle: authenticated latest crosspass negative direct-field evidence reconciled with CI; no original runtime object-identity proof, no Unity/device test, no duplicate CI. Next session should implement the bounded receiver test before any ShaderLab acceptance claim.
