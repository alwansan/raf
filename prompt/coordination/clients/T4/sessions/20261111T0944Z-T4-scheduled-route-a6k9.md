# T4 session 20261111T0944Z-T4-scheduled-route-a6k9
origin=scheduled
role=T4
branch=feature/android-native-port
baseline_sha=402dc2cfef0d322611f1903b301b5ab2a004be5e
scope_commit=3db1d6598b5654d579c13a5d6664ef2fcb75b149
implementation_commit=4582baa585b90a7841f8a24d3e5fe8d9b1299fc5

## Evidence
Owner phone Artifact 42058825739 source e9c358eda01785b65e4eb14f18723da426635628: world entered, saved, exited and reopened. Package publication failed; do not infer mouse acceptance. Owner 8 Nov: physical camera mouse improved, LEFT/RIGHT/MIDDLE and wheel unconfirmed. Prior source CI 42974039265 succeeded; not device proof.

## New work
Added scripts/t4_capture_reader_summary.py to summarize real existing physical_mouse_captured_action_callbacks and physical_mouse_legacy_reader_evidence markers in a single process log. Does not sum cumulative snapshots, claims no gameplay success, distinguishes missing callback versus missing reader reports. Local smoke with two synthetic cases passed. No new Unity or Android source changes, no CI launched. Existing captured listener records buttons, and Legacy fallback readers exist; exact game consumption remains unknown.

## Constraints and next
Keep keyboard, original .rgd, audio, Settings and Unity scenes intact. T5 owns Resolution and shared mini build. Obtain same-build/process log from current shared test APK, run python3 scripts/t4_capture_reader_summary.py LOG, compare callback/reader aggregate fields, then inspect unpatched Raft Input call sites and implement targeted runtime fix with device acceptance. This parser is evidence triage, not the actual mouse repair. Avoid duplicate Unity builds and do not treat absence of markers as proof of missing callbacks.
