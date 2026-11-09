# T5 scheduled session 20261109T1356Z-T5-scheduled-artifact-run-scope-n4q8
session_id=20261109T1356Z-T5-scheduled-artifact-run-scope-n4q8
origin=scheduled
baseline_sha=3f5dfcd5e7a445dd6eb424c79e8f865ea0d650ff
work=prompt/coordination/T_TEAM/work/20261109T1356Z-T5-scheduled-artifact-run-scope-n4q8.md

Read owner phone feedback, AGENTS, current requirements, STATUS, T_TEAM protocols, previous T5 20261109T1255Z session and Resolution original policy. Latest branch HEAD 3f5dfcd5e7a445dd6eb424c79e8f865ea0d650ff; CI 42607763178 and 42607763273 SUCCESS, no redundant CI launched. CL/test main listing inspected, no new phone screenshots accepted in this run.

New verified finding: run-scoped artifact API for 42058825739 lists four small staging artifacts only (IDs and sizes in work), not the two downstream delivery/checkpoint IDs named in feedback. The IDs must be traced to downstream workflow runs before asserting APK/OBB identity. This is an API provenance distinction, not a packaging defect or proof that owner installed the wrong package. Existing T5 PNG regression CI42604230659 SUCCESS, no repeat. No original game assets, Settings, mouse, GUID or saves changed. No new Unity/mini build.

Next: trace downstream signed checkpoint artifact provenance and match manifest/OBB using same-run bytes; use existing source-fixed right-side buttons and obtain actual phone acceptance; render-scale feature requires proven Settings binding. NOT_READY.
