# T4 session — 20261111T1538Z-T4-scheduled-x7q2
origin: scheduled
baseline_sha: eea74b7c1142ce7ce823047fd02f335443f8dd8e
latest_observed_sha: 748b8fc9693928f732645ddb9ec0f5a97cdc3322
scope: INPUT-005, counter integrity classifier only
work: prompt/coordination/clients/T4/work/INPUT-005/20261111T1538Z-T4-scheduled-classifier-validation-x7q2.md

## Evidence
Owner device feedback: Artifact 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628) enters local world, saves and reopens .rgd; packaging publication failed. This is not proof of physical mouse acceptance.
Previous T4 work: scripts/t4_capture_reader_summary.py and scripts/t4_capture_gap_classifier.py, latest preceding session 20261111T1439Z-T4-scheduled-evidence-gap-v4q7.md.
Changes: d1565fd3b2b937a465c5a6d8b648a450556d0020 rejects negative, boolean and non-integer growth/baseline samples instead of misclassifying as evidence; 748b8fc9693928f732645ddb9ec0f5a97cdc3322 adds four regressions.
Tests: NOT RUN; CI not claimed. No Unity build, device verification, input runtime, keyboard, .rgd, Settings, audio or T5 resolution/layout change.
Remaining: inspect new CI results and capture paired callback/reader events from the same device process and build; fix runtime mouse LEFT/RIGHT/MIDDLE/SCROLL based on evidence. Preserve Raft menu cursor, pointer capture lifecycle and keyboard. INPUT-005 OPEN.
