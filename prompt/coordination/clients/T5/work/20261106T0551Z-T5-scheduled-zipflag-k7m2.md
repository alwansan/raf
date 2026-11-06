# 20261106T0551Z-T5-scheduled-zipflag-k7m2
origin: scheduled
status: active
base_head: 9584c243958f69c38c77ae67c6605d75c8fd1cad
issue: INTEGRATION-001
experiment_key: T5-APK-OBB-ZIP-ENCRYPTED-FLAG-CI42164665929
scope: tests/test_t5_verify_apk_obb_pair.py only; independent of T5 chat performance/Resolution and T1-T4.
hypothesis: CI failure is synthetic fixture using literal backslash escape in ZIP signature rather than raw PK signature, not a verifier failure.
evidence: https://github.com/alwansan/raf/actions/runs/42164665929 job 127718305743: 20/21 pass, test_obb_encrypted_flag_rejected pos=-1.
shared_resource: none; source-only CI on ordinary push; no Unity build.
plan: change b"PK\\\\x03\\\\x04" and b"PK\\\\x01\\\\x02" source literals to binary ZIP signature; run local 21 tests; verify new CI. Do not modify actual APK/OBB.
