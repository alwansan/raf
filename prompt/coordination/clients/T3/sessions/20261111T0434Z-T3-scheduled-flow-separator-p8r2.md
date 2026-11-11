# T3 scheduled session — 20261111T0434Z-T3-scheduled-flow-separator-p8r2
origin=scheduled
identity=T3
issue=RENDER-002 OPEN; NOT_READY 0/3
baseline_sha=1d4040b08d40520bd678ac5f5af98fcc1509887d
scope_commit=6e30f95befc0710bceedf09a690d751b21d36383
code_commits=3f94014a1128df4fabd802b1eee1f73cddc32b27,5d71b3b80a5dd5653b4df35bc079c7b705d6f1fb
test_commit=66d5ee2bf270cc3ec6b7d9e3504c1749bbd99aaf
experiment_key=T3-PARTICLE-FLOW-SEPARATOR-003
resumed_from=20261111T0330Z-T3-scheduled-inline-material-j7q4
owner_report=docs/DEVICE_FEEDBACK_42058825739_AR.md
cl_source=alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57
work=prompt/coordination/clients/T3/work/20261111T0434Z-T3-scheduled-flow-separator-p8r2.md

## Finding and change
Inspected current parser: its regex extraction plus stripping of brace maps accepted malformed adjacent flow mappings `[{...}{...}]` as if valid two material slots. Replaced with ordered scanner requiring comma delimiters and rejecting trailing comma. Added three synthetic regressions for missing separator, trailing separator and valid two-entry list. Existing tests retained.

## Verification
A standalone equivalent parser-loop smoke test executed locally in Python, five cases passed (valid two maps, adjacent maps, trailing comma, invalid token, single map). Full repository unittest not run: local container cannot resolve raw.githubusercontent.com, and no duplicate Actions triggered. Changes are source-only; no original asset or exported comparison and no phone proof.

## Coordination and next
T4 mouse and T5 Resolution untouched. World/save/re-entry remains confirmed only for artifact 42058825739. No resources, scenes, .meta, GUID or .rgd modified. Run `python3 -m unittest discover -s scripts/tests -p 'test_t3_particle_material_chain_audit.py' -v` in checkout/CI, then audit pinned ZIP2 original and verified export side by side. Focus on ParticleSystemRenderer material GUID -> Material Shader -> Texture -> blend/alpha/ZWrite, comparing CL screenshots. Do not treat parser improvements as visual repair.
