# T4 — Android Load<T> filename-argument read-only classification (2026-11-05)

## Hypothesis and bounds
The SHA-authenticated original Load<T> has an internal catch, so the existing operation wrapper can report an unfailed return even if opening/deserializing the original file failed. T4's earlier Load.caughtException distinguishes that original catch. This change classifies the *same filename argument* as absent, zero-length, nonzero-length, or probe-unavailable at the wrapper's finally boundary.

The generated Android-only Load.argumentFileSnapshot event records existence and length class; it does not print the filename, read any bytes, write files, change the original catch/Deserialize/return, alter saves or network flags, or claim deserialization/real .rgd success. A missing/zero file is not automatically proof of a game bug, and a nonzero file is not proof of a valid RGD.

## Source and tests
Source: scripts/instrument_android_runtime_operations.py with unchanged production source SHA gate config/runtime-operation-traces.json. Test: tests/test_t4_android_load_snapshot.py; synthetic C# under actual UNITY_ANDROID conditional from scripts/t4_verify_android_load_snapshot.py; bounded independent workflow .github/workflows/raft-t4-android-load-snapshot.yml. Existing Save.argumentFileSnapshot, B50 Steam guards, original GameManager and source .meta/GUID untouched.

## Verified results (2026-11-05)

- Original adapted-source integration [42030693004](https://github.com/alwansan/raf/actions/runs/42030693004) SUCCESS at source commit a88000086d973adfcb05a85a7ecd0b12133cbf81: 14 SHA-gated original sources staged privately; original managed C# compile exit=0, errorCodes={}. Existing Save postcheck [42030692728](https://github.com/alwansan/raf/actions/runs/42030692728) SUCCESS on same script.
- Initial synthetic run [42030692961](https://github.com/alwansan/raf/actions/runs/42030692961) FAILED at C# runtime after all 5/5 Python controls passed. Diagnostic retry [42031209988](https://github.com/alwansan/raf/actions/runs/42031209988) exposed a synthetic fixture expectation for Load.exit instead of the real generic Load<T>.exit operation key. No game failure was implied.
- Fixture-only correction [e1ff457](https://github.com/alwansan/raf/commit/e1ff457c8b4723bba5e53b944fe97cbbf898a3e4) passed final [42031436693](https://github.com/alwansan/raf/actions/runs/42031436693) SUCCESS: Python 5/5 plus actual compiled and executed synthetic C# UNITY_ANDROID; absent, zero-length, corrupt nonzero, successful synthetic read, nonfatal probe logger all verified. No original game RGD used.
- Production script blob remains d6960b8ffbd39ad114db17213ef14ae8c1d535d0 after fixture-only correction. Original adapted SaveAndLoad SHA gate daf835fc2926d138483462d2ebe7ca627efcec6a9b9829dbcc7466b368317a08 unchanged; no Unity/IL2CPP/Android phone acceptance.
 For device handoff, correlate Load.caughtException and Load.argumentFileSnapshot alongside Save.argumentFileSnapshot and genuine create/play/save/quit/relaunch/load. Global LOCAL-005 OPEN, NOT_READY 0/3; latest real Raft phone APK86 predates instrumentation.
