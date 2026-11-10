# T3 20261110T1431Z-T3-scheduled-pair-ci-coverage-k8r2
origin=scheduled
issue_id=RENDER-002
resumed_from_session=20261110T1328Z-T3-scheduled-source-byte-verify-r6n4
base_sha=961b8c94ee5646671bb6e3980faf8790f574bc08
scope_commit=133da601a290fe5044be7ceee7c948d2047e67bb
source_commit=172842bd6a764b432bc830cd655eea39f40c11b8
work=prompt/coordination/T_TEAM/work/20261110T1431Z-T3-scheduled-pair-ci-coverage-k8r2.md

## Verified finding and action
Owner report docs/DEVICE_FEEDBACK_42058825739_AR.md confirms phone world/save/reentry only for artifact 42058825739; white hand/raft, square smoke, lighting unresolved. The previous workflow tested only test_t3_render_state_pair_diff.py, despite later identity and source-byte suites. Updated the existing lightweight workflow to trigger on identity source and both test suites, and execute diff, byte provenance, and identity suites with PYTHONPATH=scripts. No Unity or APK build. No raw game material changed. Latest inspected branch HEAD after scope was 133da601; source commit 172842bd. No CI result for that commit was visible at last check: waiting_ci. Earlier green run 42799750403 is on ef457271 and does not verify this change.

## Limitations and next
CI tests check source contracts only, not actual ZIP2 provenance or render pixels. Follow https://github.com/alwansan/raf/actions/workflows/raft-t3-render-state-pair-regression.yml for commit 172842bd. If failed, inspect test import path and fix without rerunning equivalent workflows. Next independently acquire private original/export material-pass pair, compare real blend/alpha/zwrite/texture linkage, then device visual proof. Keep RENDER-002 OPEN, NOT_READY 0/3. T4 mouse; T5 resolution; T1/T2 water.
