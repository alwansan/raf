# T3 session 20261110T1730Z-T3-scheduled-guid-fixtures-p8r4
origin=scheduled; issue=RENDER-002; status=IN_PROGRESS / NOT_READY 0/3

## Inputs and evidence
- Device report docs/DEVICE_FEEDBACK_42058825739_AR.md: owner phone world/save/re-entry success on artifact 42058825739, unresolved white hand/raft, square smoke, lighting, FFT errors; not evidence of new source build.
- Existing genuine original/export comparisons: 41 selected materials, 227 TexEnv UV, 89 internal texture pointers and 150 RGBA slots matched. External targets, shaders, Android GPU unproven.
- Previous T3 GUID audit source inspected on feature/android-native-port. Read operating model and owner requirements; T4 pointer and T5 display reserved.

## Work this cycle
- Scope file: prompt/coordination/work/RENDER-002/20261110T1730Z-T3-scheduled-guid-fixtures-p8r4.md, commit 1cfbb854f8d962e9d6a4880b3d2f996312932494.
- New synthetic regression tests tests/test_t3_guid_audit_regression.py, commit c7ea68640eb1e17a1fda5d0e31432be52270b24b. Tests exercise resolved/unresolved/null GUID, field order, duplicate meta, no cross-block stitching and non-YAML exclusions.
- No production assets/shaders changed, no Unity/phone test, no CI dispatched. Regression file published but not yet executed in runner; status TESTS_PENDING. No evidence that white/smoke issue is fixed.

## Next
1. Run python3 -m unittest discover -s tests -p 'test_t3_guid_audit_regression.py' and fix any fixture or parser failures; inspect live HEAD before edits.
2. Audit authenticated actual source/export trees (not a partial sample mistaken for full game); identify smoke particle renderer material and shader GUID plus keywords, Blend/ZWrite, texture alpha and import settings. Record material-specific evidence, not a generic missing-texture claim.
3. Coordinate with T1/T2 fire/water and T5 shared mini lab; do not duplicate CI or touch T4 mouse/Resolution.

No changes to shared memory/state or other sessions. Preserve original .meta GUIDs, .rgd and game data.
