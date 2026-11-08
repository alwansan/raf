# T4 scheduled — independent classifier and evidence boundary audit

- session_id: 20261108T1240Z-T4-scheduled-classifier-audit-r5n8
- origin: scheduled
- resumed_from_session: 20261108T1141Z-T4-scheduled-ci-epoch-proof-q8n3
- initial_head: d79bc3d703530e40733e3dc0afa8a5e03c4a0fb1
- scope registration commit: 242ee9985cbeb292a2104efb783b5b7259a2bae0
- work: prompt/coordination/work/INPUT-005/20261108T1240Z-T4-scheduled-classifier-audit-r5n8.json
- experiment_key: INPUT-005-T4-epoch-device-evidence-20261108

## Verified this cycle

Read owner phone feedback, AGENTS, owner requirements, STATUS, T_TEAM chat/schedule, prompt, operating model, T4 memory and latest session. Owner's artifact run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628, **entered a local world, saved, exited, and reopened on phone**; package publishing failed separately. This phone proof is retained, not extrapolated to newer binaries.

Read current scripts/t4_classify_mouse_capture_log.py. It counts lock, request, retry, relative, release and release-outcome markers; attempts are bounded by subsequent lock/unlock/escape/release; explicit epoch equality is required to count a relative callback as belonging to a request, while legacy entirely untagged pairs remain supported. Its output explicitly sets device_success_proven=false. This is **source inspection**, not an executed device trial. No new post-epoch device logs were provided in the pinned CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57.

The latest matching GitHub Actions run 42472339258 completed success for source e1e7ac93cdb64af5efdf8a819b74157dfcb71497. An earlier 42463928346 failed; corrected suite passed 42468530415 and 42472339258. No duplicate CI dispatched. At inspection current branch HEAD d79bc3d703530e40733e3dc0afa8a5e03c4a0fb1, with T3's recent unrelated audit. No overlap with T5's right-side three buttons/Resolution scope.

## Result and limitations

No safe runtime root-cause fix can be asserted from the old phone capture and passing source-only tests. No production changes, Unity builds, native requests, .rgd, keyboard, touch, audio, Settings, .meta or GUID modifications. INPUT-005 remains OPEN; original world/save/reopen success remains a phone-specific success. The independent audit closes only the evidence review, not the issue.

Next step: use a signed candidate manifest/source SHA containing epoch telemetry; on the phone exercise physical mouse lock during gameplay, camera rotation across edges, Escape/menu and return, focus loss and detach; collect requested/retry/relative/released epochs and confirm custom Raft cursor rather than system pointer. If a fresh log shows a missing event, trace that exact Android View/requestPointerCapture callback chain and implement a targeted source fix. Coordinate with T5 on candidate provenance; avoid another classifier-only CI rerun without a code change.
