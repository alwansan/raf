# 20261108T0133Z-T3-scheduled-material-chain-h7m2
origin: scheduled
identity: T3
issue_id: RENDER-002
base_sha: 614c81662f08294638fce1d471a1823f132e5677
resumed_from_sessions: 20261108T0029Z-T3-scheduled-first-session-a7c3; 20261107T2330Z-T3-scheduled-cl-root-audit-r8v2
scope: prompt/coordination/work/RENDER-002/20261108T0133Z-T3-scheduled-material-chain-h7m2.md

## Verified inputs
Owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md: owner successfully entered, saved and re-entered world on artifact run 42058825739; packaging publication failed. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. No assertion of pixel repair. Earlier T3 106 original/export Texture2D pairs, 30 RGB drift, 227 TexEnv slots parity; none proves actual Android shader output. Current HEAD at start 614c81662f08294638fce1d471a1823f132e5677. Recent Actions 42431115115 and 42431115086 completed successfully, unrelated to T3 device rendering; no Unity build requested.

## Work and result
Registered isolated scope before code commit a1d693211fabce8f1d484fb52f3274079d578a56. Added scripts/t3_material_shader_link_audit.py (deee68b960e5300cef36afc67fb6382e8dcc27a6), corrected escaped regexes (6d19fb4ebbbd0ab55ee9303f088695958e9eda7f), added tests/test_t3_material_shader_link_audit.py (e999521019253fa931b4053da0d726c100edee29), closed scope (38b18f34294a6b4965c0542f9754f54abcdc7e7c). Tool counts Material m_Shader GUID resolved/unresolved in a scanned Unity text export, null/builtin pointers, malformed pointers, and shader .meta coverage; output is aggregate only and does not expose private paths/GUIDs.

Two isolated Python regex probes on synthetic Shader .meta and Material YAML passed locally. Full committed unit test suite NOT executed: local git checkout cannot resolve github.com DNS; GitHub connector used for reads/writes. No genuine export scan performed; no screenshot pixel inspection; no shader fix or GPU/device evidence. An unresolved-in-scan reference does not prove a missing asset globally. No changes to Unity game assets, .meta, GUID, saves, Settings, audio, mouse or resolution; no Actions dispatch.

## Resume
First execute python -m unittest tests.test_t3_material_shader_link_audit on actual checkout, then scan a verified complete actual exported Unity Assets/Packages tree and privately map white hand/raft and square smoke renderer material pointers to shader/texture/alpha states; correlate screenshots and CL logs. Coordinate with T1/T2 for shader and T4/T5 for input/UI. RENDER-002 OPEN — NOT_READY. Trial vote remains no-need until actual integrated render fix.
