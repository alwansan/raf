# T3 20261109T1537Z-T3-scheduled-json-duplicate-k8p3
origin=scheduled
baseline=1cd9524e12344ad205d9459937bedd9edd701e37
latest_head_before_session=86bb46b99386b93832a9b3a7186e3cbd26733acd

## Verified reads
Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM live instructions and T3 MEMORY; checked recent T3 session list through 20261109T1450Z. Owner phone artifact 42058825739 entered/saved/reopened world; graphics issues remain. Historical real original/export source checks: 41 Material / 227 TexEnv internal parity CI41939404454, 150 RGBA parity CI41940350604. No proof of original smoke Pass/Blend/Alpha; avoid confusing smoke 34-slot Shader48 with fire 108-slot. Read-only CL test directory listed; binary screenshot pixels not analyzed this cycle.

## Scope and changes
Work plan: prompt/coordination/work/RENDER-002/20261109T1537Z-T3-scheduled-json-duplicate-k8p3.md, published 5142333fe7788ee5255cadf056fa1240f5e68514.
Source patch a18963122d744c7f36fa0a58a4cae02925b6dad6 adds json object_pairs_hook rejecting duplicate keys before audit; test patch 86bb46b99386b93832a9b3a7186e3cbd26733acd adds 3 controls (nested duplicate pass key, top-level duplicate side, valid JSON). Prevents silent last-value-wins metadata ambiguity, but does NOT authenticate shader provenance.

## Validation and boundaries
Static code inspection only; local git clone/test blocked by DNS 'Could not resolve host: github.com'. Regression tests added but NOT executed; no CI request made and no Unity/APK/OBB, shader, .meta, save, Settings, audio, or CL changes. Latest observed Actions 42645204502 T2 Foam completed success; no duplicate run launched. No game-device or pixel proof. RENDER-002 OPEN, NOT_READY 0/3.

## Next
Execute python tests/test_t3_smoke_pass_state_gate_v2.py with scripts on PYTHONPATH in available isolated CI or networked checkout; then extract authentic smoke Shader48 parsed Pass/Blend/Alpha metadata from verified ZIP2 and same-instance export, record owner file SHA and immutable provenance, compare with gate v2, and correlate original CL smoke image. Coordinate T1/T2 fire and T4 mouse/T5 Resolution without touching their scopes.
