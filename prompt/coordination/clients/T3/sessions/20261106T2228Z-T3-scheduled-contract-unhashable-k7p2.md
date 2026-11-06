# T3 independent scheduled checkpoint
session_id: 20261106T2228Z-T3-scheduled-contract-unhashable-k7p2
origin: scheduled
issue_id: RENDER-002
resumed_from_sessions:
- 20261106T2133Z-T3-scheduled-contract-schema-9a2f
- 20261106T2035Z-T3-scheduled-local-contract-test-f4b2
base_sha: c87d072ae24df0bc0d81f2c77620b2195e025b0d
last_observed_head: ba686e59f8f4ca5484dae464f6c0693db837ce4f
status: SOURCE_FIXED_PENDING_TEST
scope: prompt/coordination/clients/T3/work/20261106T2228Z-T3-scheduled-contract-unhashable-k7p2.md
changes:
- dc395792: fail closed for non-string stage/family before tuple hash/Counter.
- ba686e59: 24 synthetic negative subcases + valid control in independent regression file.
test_status: NOT_RUN (no new CI launched; tests require execution)
reproduce: PYTHONPATH=scripts python3 -m unittest scripts/test_t3_dxbc_spirv_contract_malformed.py
owner_phone_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md confirms world save/reopen for artifact 42058825739 only. White hand/raft, square smoke remain OPEN. Not proof of Shader48 causality.
next: run synthetic tests and existing join tests; inspect authentic DXBC RDEF to SPIR-V contract with pinned ZIP2 and safe summary; do not modify game resources until mismatch proven.
limits: No Unity, phone, original shader, APK or OBB run. No evidence of visual fix. T4 mouse and T5 Resolution/buttons untouched.
