# T3 checkpoint 20261110T1828Z-T3-scheduled-guid-regex-fix-n4q7
origin=scheduled
issue=RENDER-002; status=IN_PROGRESS; NOT_READY 0/3
resumed_from_sessions=20261110T1730Z-T3-scheduled-guid-fixtures-p8r4; 20261110T1532Z-T3-scheduled-guid-link-a7q2
scope_commit=b567ec86834505c7a93d6d18e435f398ddf2af4b
production_commit=b4ff5295a28e31765d97352e2201dd146113ccf3
test_commit=de130352393ca1528e63773a9ade76134802bbd5
baseline_blob_sha=7c5fd058f2a30f9a2d1fcc6e4ae2d7ddfcb0ad96
origin_report=docs/DEVICE_FEEDBACK_42058825739_AR.md

## Findings and work
Read device report: artifact 42058825739 owner-confirmed world/save/reentry, unresolved white hand/raft, square smoke and lighting. Earlier authentic same-export 41 materials / 227 UV / 89 internal texture references match only selected scope; does not prove external shader/texture binding or phone rendering.
Inspected scripts/t3_unity_guid_link_audit.py and tests/test_t3_guid_audit_regression.py. Initial suspicion of double-escaped regex was disproven by inspecting actual GitHub content and Python regex semantics; no regex logic changed. A no-op contents API update yielded commit f5560672f4bd6bb87dcc6ac224ffc7eb09806d1a with identical blob SHA (no source fix). Instead added actionable aggregate grouping of unresolved GUID references by referring YAML file extension (.mat/.prefab/.unity etc.), plus source-free regression fixture; no paths, GUIDs, or raw game assets are exposed. This distinguishes material shader binding investigation from prefab and scene references without claiming any unresolved GUID is actually missing from full game.
No full Python regression run or CI result confirmed in this cycle; TESTS_PENDING. No original ZIP2 asset scan performed. No APK, Unity, shader or runtime change. T4 mouse and T5 resolution untouched; no overlapping CI launched.

## Next
1. Execute python3 -m unittest discover -s tests -p 'test_t3_guid_audit_regression.py' on current HEAD and fix any failure.
2. Run read-only GUID audit on authenticated actual full export/source tree, distinguish incomplete-tree unresolved from genuine missing dependencies, and identify smoke particle material/shader binding and Blend/Alpha/ZWrite. Compare to original before modifying shader/material.
3. Review current team work and Actions before any heavy CI; coordinate T5 unified mini lab only if a device hypothesis needs a test.
