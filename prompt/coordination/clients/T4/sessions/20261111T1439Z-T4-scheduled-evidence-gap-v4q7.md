# T4 scheduled session 20261111T1439Z-T4-scheduled-evidence-gap-v4q7
origin=scheduled
baseline_sha=a62b152d2cc37b1600355685388555c2e73b2535
scope=INPUT-005 aggregate callback/reader evidence classifier
owner_feedback=https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md
device_result=Artifact 42058825739 successfully entered local world, saved, exited, reentered; delivery publish failed. Not a mouse acceptance result.
previous_session=20261111T1337Z-T4-scheduled-zip-log-input-k9r2.md
work=clients/T4/work/INPUT-005/20261111T1439Z-T4-scheduled-evidence-gap-v4q7.md
changes:
- scripts/t4_capture_gap_classifier.py: classify per-button positive counter growth without implying event causality.
- tests/test_t4_capture_gap_classifier.py: four regression cases for missing baseline, callback-only growth, paired growth and no growth.
commits:
- scope 2c30938d8b81a39df43d2ffda33b098851918fab
- implementation 43861a5caec8e7cad4f5c9e405a777e1fa9e38c1
- tests 7176cf288c201835ac9b1e64587500b57620c18f
verification=GitHub contents accepted; no Python/CI execution yet. No Unity build or phone execution.
CI_observation=43028966025 T2 evidence summary failed; not a T4 mouse runtime test. No duplicate action launched.
limits=Aggregate logs cannot prove a click reached gameplay, especially without same-process build and baseline. No keyboard, save, .rgd, Resolution, Settings, touch, audio or game source modified.
next_step=run python -m unittest discover -s tests -p 'test_t4_capture_gap_classifier.py'; use same-build same-process capture and reader JSON; T5 unified lab if device-only verification needed. Implement actual Android/Unity mouse routing fix only once lost stage is proven.
status=INPUT-005 OPEN, LOCAL-005 device scenario passed only for artifact 42058825739.
