# T5 scheduled checkpoint
session_id: 20261106T0654Z-T5-scheduled-pair-ci-a7k2
origin: scheduled
base_sha: fb248da6263c5199289f834f6a973921798a023b
resumed_from_sessions: prior scheduled 4a0ae407/d9daaeea pair test correction; chat 20261106T0248Z-T5-chat-native-delivery-retention-e8a3; chat 20261106T0214Z-T5-chat-scene-window-attribution-8d91
scope: isolated INTEGRATION-001 paired-archive synthetic regression follow-up; no shared Unity resource.

## Verified executable evidence
- [Run 42164665929](https://github.com/alwansan/raf/actions/runs/42164665929): completed FAILURE on 12c52c9e64632a5c524fdcbf781d72bb02bc9131; preceding test fixture ZIP signature failure.
- [Fix 4a0ae407](https://github.com/alwansan/raf/commit/4a0ae4077c790d4f32ba9b7a35ebc80bad287807) corrects test-only ZIP byte signature.
- [Run 42170921976](https://github.com/alwansan/raf/actions/runs/42170921976): completed SUCCESS on exact fix SHA 4a0ae4077c790d4f32ba9b7a35ebc80bad287807, job 127738284655. Read raw job logs: **Ran 21 tests in 0.025s, OK**, including test_obb_encrypted_flag_rejected, test_obb_unix_symlink_entry_rejected, traversal, duplicate, wrong version, matching SHA but malformed ZIP and same-size corruption. py_compile passed. Summary explicitly synthetic_only=true, real_signed_files=false, unity=false, phone=false.
- Current HEAD at initial read fb248da6263c5199289f834f6a973921798a023b; CI runs at that time showed T2 Foam latest 42173824517 SUCCESS and T1 FFT 42167120994 SUCCESS; not equivalent to APK/OBB phone test.

## Outcome and limits
The previously failing regression is now verified green on its exact immutable source SHA. No additional CI was dispatched. This closes only test-fixture regression, **not** real signed APK/OBB pairing, actual Android OBB read or native delivery 403. Original owner world/save/reopen remains phone-confirmed only on artifact 42058825739; graphics water/FFT and full readiness remain open, NOT_READY 0/3.

Next: obtain preserved signed APK/OBB manifest and hashes (avoid downloading >6GB unless needed), verify package versionCode, OBB name/size/SHA and original Unity assets from the same delivery artifact; investigate release HTTP403 separately. Resolution callback/hardware rendering choices still require source/IL proof. Do not conflate FPS with refresh or stale SurfaceFlinger.
