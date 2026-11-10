# T3 session 20261110T1532Z-T3-scheduled-guid-link-a7q2
origin=scheduled
issue_id=RENDER-002
resumed_from_session=20261110T1431Z-T3-scheduled-pair-ci-coverage-k8r2
scope_commit=3f830c2f2fe54e5bfb3bb03d29ce9d2b473113c0
source_commit=cbac1555c1dcce10bc3ce59279925464e23df204
tests_commit=af3c0f5c5f9490a68a4db9c5d5ae51b6d264bb86
work=prompt/coordination/T_TEAM/work/20261110T1532Z-T3-scheduled-guid-link-a7q2.md
origin_report=docs/DEVICE_FEEDBACK_42058825739_AR.md

## Work and evidence
Reviewed owner phone report: world/save/re-entry verified only for artifact 42058825739; white hand/raft and square smoke remain. Reviewed live owner requirements, T-team protocol/operating model, prior T3 scheduled checkpoint and old state/MEMORY. The earlier same-instance ZIP2 Material/TexEnv comparison [41939404454](https://github.com/alwansan/raf/actions/runs/41939404454) established 227/227 UV slot parity and 89/89 internal texture pointers; do not assume these 41 materials have missing internal texture identities. 25 external references were not established.

Added independent source-only `scripts/t3_unity_guid_link_audit.py`: read-only static inventory of serialized Unity YAML reference GUIDs and local .meta identities. Emits counts only; avoids proprietary paths and raw material payload. Added two isolated regression tests in `scripts/test_t3_unity_guid_link_audit.py`. **Tests are written but not executed in CI or device in this cycle**. No original/export files were acquired here; no evidence that white materials/square smoke are fixed. No Unity or APK dispatch; T4 mouse and T5 Resolution left untouched.

## Next
Run `PYTHONPATH=scripts python3 -m unittest scripts/test_t3_unity_guid_link_audit.py -v` then inspect source/export partial trees privately and distinguish unresolved-in-tree from truly missing. Cross-check specific material/prefab/particle/shader/texture graph against CL images and true Android pixel evidence. Continue same-pass Blend/Alpha/ZWrite comparison, not another synthetic-only regression cycle. Avoid duplicate CI, check branch HEAD and team scopes first. RENDER-002 OPEN, NOT_READY 0/3.
