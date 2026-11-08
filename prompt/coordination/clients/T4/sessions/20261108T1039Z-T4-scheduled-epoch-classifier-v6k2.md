# T4 scheduled — epoch-aware mouse trace classification

- session_id: 20261108T1039Z-T4-scheduled-epoch-classifier-v6k2
- origin: scheduled
- base_sha: 7e1aced7b7086e659dadfe12abe079ff9d00dd57
- resumed_from_session: 20261108T0840Z-T4-scheduled-epoch-correlation-p4k8; 20261108T0930Z test correction (CI 42468530415)
- work: prompt/coordination/work/INPUT-005/20261108T1039Z-T4-scheduled-epoch-classifier-v6k2.json
- issue: INPUT-005 (OPEN)

## Confirmed owner/device boundary
Owner 5 November Artifact 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628) entered local world, saved, exited and reopened. Package publication failed; this does not negate the owner's narrow device success. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 contains images/logs but predates new mouse epoch telemetry. Preserve original .rgd, keyboard, audio and Settings. T5 owns buttons/Resolution.

## New independent finding and fix
After prior T4 instrumentation added epoch to capture requested/retry/relative events, the classifier still treated *any* relative marker between request and release as evidence for the request, even when its epoch differed. This can falsely associate stale motion with a later generation. Updated scripts/t4_classify_mouse_capture_log.py to correlate equal explicit epochs; retain legacy untagged-only logs but do not infer mixed tagged/untagged correlation. Added three tests to tests/test_t4_classify_mouse_capture_log.py: mismatched epoch, matching retry epoch, and mixed tagged/untagged.

- Code commit: ff432b057f8348d90848f3395bec554205898645
- Test commit: e1e7ac93cdb64af5efdf8a819b74157dfcb71497
- CI: https://github.com/alwansan/raf/actions/runs/42472339258 — pending at observation, no pass claim.
- No Android runtime, input, UI, Unity, original asset or save format changed. No duplicate workflow dispatched.

## Limits and next step
The classifier remains conservative and source-only; no phone capture proof. Check CI result for test commit, then apply classifier to new on-device capture/lock/relative/escape logs after a diagnostic build. Verify actual Raft cursor in menu, unbounded camera rotation in gameplay, capture release on focus loss/disconnect, and keyboard continuity. No readiness claim.
