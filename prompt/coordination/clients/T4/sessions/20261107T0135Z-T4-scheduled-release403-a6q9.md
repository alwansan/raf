# T4 scheduled — release authorization boundary

- session_id: 20261107T0135Z-T4-scheduled-release403-a6q9
- origin: scheduled
- scope: read-only release 403 audit; independent of concurrent mouse, water, and UI edits.
- starting HEAD: db7b14afeeb08c3b653604280222a26d1d3928c3; work scope commit: 2106fa8103d401ed2ca0942ba8217002bc241c4d.
- previous T4 checkpoint: [20261107T0042Z-T4-scheduled-delivery403-k7m4.md](20261107T0042Z-T4-scheduled-delivery403-k7m4.md).

## Verified finding

[Native run 42296450023](https://github.com/alwansan/raf/actions/runs/42296450023), immutable build source a1737bd736e276d53df808442cfae3b1eea0d488: native-request-gate SUCCESS, unity-license-preflight SUCCESS, reconstruct SUCCESS, publish-early-test FAILURE, delivery-result FAILURE. Artifacts: signed-output checkpoint 13550196498 (2,974,171,581 bytes) and android-test-delivery 13549514149 (5,948,365,703 bytes). Their existence does not establish device install, content parity or Release publication.

Read current .github/workflows/raft-unity-editor-android-import.yml: top-level permissions contents:read; publish-early-test overrides contents:write and actions:read. Its GH_TOKEN is secrets.RAFT_RELEASE_TOKEN || github.token; comment explicitly records previous HTTP 403 on Release POST. Therefore adding a second contents:write YAML line is not a justified fix. Effective repository/organization workflow-token policy, selected secret validity/scope, release ruleset or installation restrictions remain unknown. The job should diagnose permission context without exposing token; T5/owner should inspect policy and optionally perform a tightly scoped publish-only retry with already-verified artifacts rather than repeat a 2.9GB Unity build. Never claim that the token policy is definitively the cause without an authorized test.

## Device evidence and next step

Owner-confirmed on-phone world entry, SaveGame/SaveWorld/SaveUser, exit and reopen belongs to artifact 42058825739 and source e9c358eda01785b65e4eb14f18723da426635628. Preserve original .rgd compatibility; LOCAL-005 remains OPEN. [Device feedback](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md) links CL screenshots/logs showing black system cursor and white raft/hand, plus water errors; these do not prove current physical pointer capture. INPUT-005 remains OPEN. After a signed, provenance-verified candidate, test physical mouse relative movement and Raft cursor, three mouse buttons, keyboard and focus/edge transitions, and save/reopen regression on device. T5 owns resolution and three on-screen buttons.

No Unity run, release mutation, device test, gameplay source modification or shared-file overwrite in this session. NOT_READY 0/3 unchanged. Next T4 task: if phone data remains unavailable, audit independent pointer capture behavior against source with bounded tests, avoiding overlap with concurrent T4 chat changes.
