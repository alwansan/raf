# T3 isolated scope 20261109T1537Z-T3-scheduled-json-duplicate-k8p3
origin=scheduled; baseline HEAD=1cd9524e12344ad205d9459937bedd9edd701e37

Question: JSON parser silently accepts duplicate keys in metadata, permitting contradictory original/exported shader-pass fields to be overwritten before fail-closed audit. This is a parser-integrity fix, not an authentic source extraction or shader fix.
Files: scripts/t3_smoke_pass_state_gate_v2.py; tests/test_t3_smoke_pass_state_gate_v2.py; unique T3 session. Experiment key RENDER-002/T3-json-duplicate-k8p3. Shared resource: none. No CI request, Unity build, original game data, shader/meta or CL writes.
Hypothesis: json.loads with object_pairs_hook that rejects repeated object keys prevents ambiguous input. Tests exercise CLI parser with nested duplicate pass field and top-level duplicate original; preserve ordinary valid metadata. Verify against live HEAD before changes.
Current source proof: same-instance 41 Material/227 TexEnv and 150 RGBA slots matched in historical runs 41939404454 and 41940350604; smoke Shader48 original Pass/Blend/Alpha not extracted, so RENDER-002 OPEN NOT_READY.
