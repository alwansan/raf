# T3 scheduled — 20261108T1529Z-T3-scheduled-neg-fileid-q7m2

- origin: scheduled
- issue: RENDER-002 (OPEN / NOT_READY)
- resumed_from_sessions: 20261108T1430Z-T3-scheduled-particle-yaml-k6d2; 20261108T1326Z-T3-scheduled-audit-ci-n4q8
- owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md and apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md (newer).
- work: prompt/coordination/work/RENDER-002/20261108T1529Z-T3-scheduled-neg-fileid-q7m2.json
- scope commit: 8fce0e65bbce68a8c73b806503da58038cb23af8
- code commit: b4f7d645589399ec6f1d6e354f66064b697c2928
- test commits: f73d066c95656a24e546a81fe412a2ded9aa946a; fixture corrected 3825975d59cb62f0ff8dd6c6338e67ab4fdf38a5

## Verified source finding
The newly added aggregate ParticleSystemRenderer audit parsed a negative fileID as a valid local material PPtr. This is an invalid reference category for the audit's intended material-link accounting. Changed classification to invalid_negative_fileid_slots, with a regression fixture containing one negative and one positive local reference. The parser still counts both material slots; only one is local.

## Evidence and limitations
GitHub connector successfully read current source and wrote scoped changes using content-blob SHA guards. No Python test execution, ZIP2 original scan, Unity import, APK or on-device graphics validation in this run. Earlier genuine original/export results: CI41939404454 227 UV slots matched, CI41940350604 150 color slots matched in the bounded selection. CI42485092438 previously passed 40/40 tests *before* this new change; do not treat it as verification of this patch.

Owner Nov 8 CL LogRaft-20261108-164850-270: 74,359 water invalid passes, 11,165 FFT kernel errors, 7,372 cursor RGBA warnings, two OBB GUID warnings. These are owner-report counts, not T3's own reproduction. T4 owns mouse click/scroll, T5 packaging/resolution, T1/T2 water. Device 42058825739 world/save/reentry success is bounded to that artifact.

## Next
1. Run `python -m unittest discover -s tests -p 'test_t3_particle_renderer_yaml_audit.py' -v` in isolated CI or available source checkout.
2. Obtain authenticated original/export Unity YAML tree from ZIP2 pinned source; run audit read-only and compare particle renderer PPtrs against material/shader/texture source and export.
3. For smoke-square, compare particle shader blend/alpha, UV and texture alpha with phone screenshots; for white hand/raft compare shader variant, texture import/sRGB and lighting. No resource edits without identified mismatch.
4. Maintain RENDER-002 OPEN; no device-ready claim.
