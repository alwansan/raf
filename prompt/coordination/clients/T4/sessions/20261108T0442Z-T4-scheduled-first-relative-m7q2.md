# T4 — first relative mouse observation checkpoint
session_id: 20261108T0442Z-T4-scheduled-first-relative-m7q2
origin: scheduled
resumed_from_sessions:
- 20261108T0336Z-T4-scheduled-ci-verified-h8p3
- 20261108T0237Z-T4-scheduled-retry-classifier-gap-n4q8
base_sha: 778a885eeeefeb8a2cab49315d3f7491dac8c3b5
issue_id: INPUT-005
status: waiting_ci

## Owner/device evidence
Owner-confirmed Artifact run 42058825739 source e9c358eda01785b65e4eb14f18723da426635628 entered, saved, exited and reopened the same local world on phone; failed packaging/publishing is separate. CL pinned snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57; no evidence that this old APK emits newer physical_mouse_capture_retry. Do not downgrade LOCAL-005 or mutate .rgd. T5 owns three-button reposition and Resolution.

## Independent scope and change
Work: prompt/coordination/work/INPUT-005/T4-20261108T0442Z-first-relative-observation.json, registered first in commit 20cb85b2. Source commit 8d52dd6ea6cd011986956f94afd029b6da9b77c6 changes AndroidPhysicalMouseCapture.Update: previous relative event diagnostic emitted only after 120 accepted packets, making a brief phone test with 1–119 packets indistinguishable from zero packets. Now emits once at first accepted packet and retains 120-packet intervals thereafter. No input, camera, keyboard, pointer, focus or capture behavior changed. Test commit 125efe37c834fa521cfabc289c01d72b6e42757c adds source-contract and 0..250 packet throttle check (expected 1,121,241). No heavy Unity request, no raw game assets.

## CI/limits
On source commit 8d52dd6e GitHub automatically queued 42447918736 (classifier), 42447918743 (capture bridge), 42447918737 (offline adapter), 42447918738 (T5 staged equality). Do not cancel/duplicate. These initial queued runs predate test commit 125efe37; check later runs for that SHA and full new test. This is source-only telemetry: cannot claim device cursor/camera success or prove native capture acceptance. INPUT-005 remains OPEN.

## Next
Read latest HEAD and current T4 CI result, check all tests including new first-event test, then correlate with a newly installed APK containing telemetry: Escape -> authored lock -> request/retry -> first relative event -> menu release; verify physical mouse + keyboard and Raft menu cursor on phone. Preserve T5 ownership, audio/Settings and original saves.
