# T4 — Android Load<T> filename-argument read-only classification (2026-11-05)

## Hypothesis and bounds
The SHA-authenticated original Load<T> has an internal catch, so the existing operation wrapper can report an unfailed return even if opening/deserializing the original file failed. T4's earlier Load.caughtException distinguishes that original catch. This change classifies the *same filename argument* as absent, zero-length, nonzero-length, or probe-unavailable at the wrapper's finally boundary.

The generated Android-only Load.argumentFileSnapshot event records existence and length class; it does not print the filename, read any bytes, write files, change the original catch/Deserialize/return, alter saves or network flags, or claim deserialization/real .rgd success. A missing/zero file is not automatically proof of a game bug, and a nonzero file is not proof of a valid RGD.

## Source and tests
Source: scripts/instrument_android_runtime_operations.py with unchanged production source SHA gate config/runtime-operation-traces.json. Test: tests/test_t4_android_load_snapshot.py; synthetic C# under actual UNITY_ANDROID conditional from scripts/t4_verify_android_load_snapshot.py; bounded independent workflow .github/workflows/raft-t4-android-load-snapshot.yml. Existing Save.argumentFileSnapshot, B50 Steam guards, original GameManager and source .meta/GUID untouched.

Status at file creation: source and tests integrated for CI, no reported CI result yet. Update with immutable run SHA and assertion results from live Actions. For device handoff, correlate Load.caughtException and Load.argumentFileSnapshot alongside Save.argumentFileSnapshot and genuine create/play/save/quit/relaunch/load. Global LOCAL-005 OPEN, NOT_READY 0/3; latest real Raft phone APK86 predates instrumentation.
