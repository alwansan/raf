# T3 scope reservation — original smoke34 semantic→SPIR-V location provenance

session_id: 20261109T2035Z-T3-scheduled-semantic-location-gate-m6q8
origin: scheduled
base_sha: 5f4fde66ac41a721f2c5e09016928efc21c0178a
issue: RENDER-002 OPEN / NOT_READY 0/3
experiment_key: t3-smoke34-provenance-bijection-failclosed-v1
resource_key: none; source-free Python only

## Prior authenticated evidence
CI42692895633 original DXBC 22 read vs 28 declared lanes; SPIR-V 28 reflected lanes, not a data-loss proof. CI42691211652 source VS/PS 7/7 semantic-index matches. Generated SPIR-V variable names did not preserve original names (CI42689814110). No original semantic→SPIR-V location map exists.

## Independent scope
Create scripts/t3_smoke34_location_provenance_gate.py and tests/test_t3_smoke34_location_provenance_gate.py. Accept only explicit authenticated per-stage mapping records and reject duplicate semantic/index/component or SPIR-V location/component, missing original used lanes, unknown original semantic IDs, and ambiguous multi-candidate mappings. Fail closed; never infer mapping from reflected widths or compiler-generated names. Tests synthetic only. No original shader code or raw resource publishing. Avoid touching T3 chat scripts/workflows, T1/T2 water, T4 mouse, T5 display/mini APK.

## Gate
This validator is preparatory; no real provenance supplied => INCONCLUSIVE. No game build, Unity/OBB, CI duplication or READY claim. Next authenticated source extraction must provide actual mapping evidence.
