# T3 session 20261110T2030Z-T3-scheduled-guid-multiline-k4v9
origin=scheduled
issue=RENDER-002
baseline_head=8550bfdf7d453b57e74c14cb268afe02e11ae35d
work_commit=56482c6e14e9cc110ec4a19776db13a0041fe71f
test_commit=a2b73efb5836a4627ea63205c5b74362ab9d7c1b
scope=prompt/coordination/work/RENDER-002/T3-20261110T2030Z-scheduled-guid-multiline-k4v9.md
status=SOURCE_REGRESSION_ADDED_CI_UNVERIFIED
origin_report=docs/DEVICE_FEEDBACK_42058825739_AR.md

## Evidence
Read owner phone report: world entry/save/exit/reentry is device-confirmed on artifact 42058825739 only; white hand/raft, square smoke, lighting defects open. Read T3 earlier 1931Z source regex fix 993f36ad and current source script, tests, owner requirements and T_TEAM instructions. Branch HEAD was 8550bfdf at inspection. Recent Actions includes T5 PERF gate failure 42889557850 and successful runner guard 42884997711, unrelated to T3 smoke parity. No duplicate native/Unity build requested.

## Work performed
Registered a separate scope, then added a source-free regression fixture to tests/test_t3_guid_audit_regression.py using actual multiline Unity YAML-style inline object references: guid-before-fileID, embedded line breaks, and adjacent partial blocks that must not be stitched. No production shader, asset, scene, .meta, save, Settings, audio, mouse or resolution changed. The current parser appears capable of handling the new fixture; this is a new guard against future silent undercount, not a confirmed runtime defect. No test runner executed in this environment; CI not claimed successful.

## Next
Run python3 -m unittest discover -s tests -p test_t3_guid_audit_regression.py on current HEAD and record result. Prioritize real authenticated ZIP2/export audit and exact smoke particle renderer -> material -> shader -> texture/Blend/Alpha/ZWrite join; compare to actual phone images and CL logs. Coordinate T1/T2 shader and T4/T5 UI, avoid duplicate builds. NOT_READY 0/3. Do not claim visual restoration from this fixture.
