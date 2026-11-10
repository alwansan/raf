# T3 session 20261110T1628Z-T3-scheduled-guid-order-n7q4
origin: scheduled
track: RENDER-002 / ASSET-RESTORE-001
baseline_sha: 2af49e6615259530b5e7e39d26419f195adfac05
work: prompt/coordination/clients/T3/work/20261110T1628Z-T3-scheduled-guid-order-n7q4.md

## Verified progress
- Owner phone report 2026-11-05: world/save/reopen successful on artifact 42058825739; white materials, smoke squares, lighting remain open. CL snapshots in docs/DEVICE_FEEDBACK_42058825739_AR.md.
- Previous T3 tool scripts/t3_unity_guid_link_audit.py matched only fileID-before-guid within YAML brace; silently omitted guid-before-fileID references.
- Commit 844e33379c46a2107da9b08a076e6be1cdcbfd49 parses each brace separately, accepts either field order, and rejects incomplete references. Commit 0bda71482a60d5de803824bcb34cc253a1b2f0d2 adds reversed-order/cross-block regression fixture.
- Isolated Python regex smoke PASS for both reversed entries and no cross-brace joining. Full repository unittest and actual ZIP2 export audit NOT RUN; do not claim original asset restoration.
- No Unity/Android APK build, no changes to other agents' files, no raw assets published.

## Next
1. Run PYTHONPATH=scripts python3 -m unittest discover -s scripts -p 'test_t3_unity_guid_link_audit.py' -v on checked-out HEAD.
2. Audit authenticated ZIP2 restored .meta/YAML tree and compare counts to prior T3 audit; isolate white-hand, raft and smoke material GUIDs and shader keywords.
3. Correlate material-to-shader/texture bindings with CL screenshots and actual render-state pass comparison, not inferred from unresolved partial-tree counts.
status: OPEN / NOT_READY 0/3
