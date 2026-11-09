# T3 scheduled — semantic/location provenance structural gate
session_id: 20261109T2035Z-T3-scheduled-semantic-location-gate-m6q8
origin: scheduled
base_sha: 5f4fde66ac41a721f2c5e09016928efc21c0178a
resumed_from: 20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7; 20261109T1935Z-T3-scheduled-dxbc-handoff-k7m4
issue: RENDER-002 OPEN NOT_READY 0/3

## Latest evidence
Authentic CI42692895633: original PS DXBC 22 used lanes/28 declared, SPIR-V reflection 28 declared. The six-lane difference is not a translator failure. CI42691211652 7/7 genuine VS↔PS semantic-index matches. CI42689814110 compiler-generated names not usable as original semantic identifiers. Original ShaderLab restoration and Android pixel verification absent.

## Scope and change
Work: prompt/coordination/work/RENDER-002/20261109T2035Z-T3-scheduled-semantic-location-gate-m6q8.md; reserved commit b73451f51d47c21db1bd3afdc49f009723c56aa7. New source-free structural bijection validator scripts/t3_smoke34_location_provenance_gate.py and nine tests tests/test_t3_smoke34_location_provenance_gate.py. Requires explicit original-lane→SPIR-V lane provenance; does not infer mappings from vector widths/names. Rejects missing, duplicate, ambiguous, malformed mappings and never emits opaque identifiers. A structurally complete mapping returns STRUCTURAL_BIJECTION_ONLY, not PASS/READY. No authentic mapping available, so real smoke34 outcome INCONCLUSIVE. No game resources, APK, OBB or Unity changed.

## Actions
Checked 12 newest runs: CI42692895633 SUCCESS; T2 latest 42693951346 FAILURE unrelated to this scope, 42693501006 SUCCESS. No new CI launched or duplicate native build.

## Next
Run source-free unit tests and connect only to authenticated original DXBC↔SPIR-V per-stage instruction provenance, with private source data and aggregate-only outputs. Verify independently on controlled GPU pixels before claiming visual fix.
