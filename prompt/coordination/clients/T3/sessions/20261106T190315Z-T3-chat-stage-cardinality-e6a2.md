# T3 chat — Particle108 per-stage DCL/SPIR-V resource cardinality

- session_id: 20261106T190315Z-T3-chat-stage-cardinality-e6a2
- origin: chat
- issue: RENDER-002 OPEN / NOT_READY
- base_sha: 322908960532923deb0f16c359885fc9c423bdb2
- resumed_from_session: 20261106T185041Z-T3-chat-dcl-spv-family-census-a91d
- related scheduled session: 20261106T1828Z-T3-scheduled-contract-fixture-b6e1 (its resource-binding mapping files were not modified)
- reservation: prompt/coordination/work/RENDER-002/20261106T190315Z-T3-chat-stage-cardinality-e6a2.json; published before edits.

## Completed code

Updated scripts/t3_particle108_dcl_spv_family_census.py, commit dd2580e25c1959a066ce597b6b6397dd5d1ae622. Original DCL constant-buffer, SRV, sampler and UAV declarations are compared against translated SPIR-V descriptors *inside each stage and keyword*, not just in global sums. Combined image/sampler descriptors count toward both categories. Only aggregate stage mismatch counts and absolute deltas are reported; no register numbers or per-stage private identities are exposed.

Updated tests/test_t3_particle108_dcl_spv_family_census.py, commits 44341ce5761db7242900bdac0334dc35a783b391 and 6d584b6aee43b1e8decee12e5c5c2c0649d00c79. New negative controls prove that offsetting source-to-SPV stage differences cannot hide behind matching global totals.

## Verification

- Source-only CI 42276342223: SUCCESS, original 10 tests.
- Source-only CI 42276412595: FAILED 1 of 14 tests, because a synthetic fixture double-counted combined and separate sampler representations; no original-game failure.
- Source-only CI 42276510557: SUCCESS, 14/14 tests after correcting fixture. Test job 128094092039.
- Last authentic ZIP2 test remains CI 42274933802 (global source DCL CB24/SRV10/sampler10 versus SPV UBO24/image10/sampler10, 8 stages; no family-absence signals). No authentic *per-stage numerical equality* result yet.

The updated original-source workflow remains manual-only. No new original Action run was dispatched in this session. Do not claim Shader48 functioning, graphics color recovery, resource slot provenance, Unity/Android pixels or APK delivery.

## Handoff

Work is paused pending an authorized new original-source test using existing workflow raft-t3-particle108-dcl-spv-family-census.yml. Check current HEAD and running Actions first. Inspect stage_<family>_cardinality_mismatch and stage_all_four_resource_family_cardinalities_equal; equality still does not prove exact DXBC register to SPIR-V descriptor mappings. The scheduled T3 resource-provenance code remains independent. No game assets, scenes, .meta, GUID, save data, FMOD, Settings or native build requests changed. Trial vote T3 remains «لا يحتاج» in trial-20261106-r1.
