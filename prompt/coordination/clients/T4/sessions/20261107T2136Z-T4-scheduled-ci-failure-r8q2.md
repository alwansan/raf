# T4 scheduled session 20261107T2136Z-T4-scheduled-ci-failure-r8q2

- origin: scheduled; worker: T4; issue: INPUT-005; base HEAD: `5c7e44ef5f130525edcb33d0f8adf0ce78413b97`.
- Owner evidence: 5 November Artifact 42058825739: entered world, saved, exited and reopened. This remains phone-confirmed for that artifact only; .rgd compatibility preserved; LOCAL-005 open.
- Previous T4 checkpoint: `af8ee90a` added source-only mouse classifier workflow, waiting_ci. Work: `prompt/coordination/work/INPUT-005/T4-20261107T2136Z-classifier-ci-failure.json`.
- New evidence: [CI 42412029098](https://github.com/alwansan/raf/actions/runs/42412029098) failed on source `b1b3d66a`: 16/17 tests passed. Sole failure `test_superseded_lock_with_no_new_request_does_not_borrow_old_request`: expected REQUEST_WITHOUT_RELATIVE_OBSERVED, observed RELEASED_BEFORE_RELATIVE_OBSERVED.
- Root cause: classifier treats next authored_lock (supersession) as release merely because its boundary precedes the next Escape. No actual authored_unlock, capture_released or escape_release occurred.
- Fix: [95ac67c2](https://github.com/alwansan/raf/commit/95ac67c2a2e42359b9f315598cd171bf2578f370) requires explicit release/unlock/escape boundary for RELEASED_BEFORE_RELATIVE_OBSERVED; supersession alone stays REQUEST_WITHOUT_RELATIVE_OBSERVED. The 17th regression test already exists and is the direct negative control.
- Validation: GitHub CI had not yet reported a new run at final read; status waiting_ci. Do not claim 17/17 or phone success until observed. No Unity build or cancellation.
- Shared-resource coordination: only T4 classifier source modified, no T5 UI/Resolution files, no touch/keyboard, FMOD, Settings, .meta, .rgd, scene changes. Follow-up: read fresh Actions run and apply classifier to fresh CL logs containing explicit lock/release/relative markers; distinguish log gaps from runtime defects. Preserve mouse cursor menu and keyboard behavior.
