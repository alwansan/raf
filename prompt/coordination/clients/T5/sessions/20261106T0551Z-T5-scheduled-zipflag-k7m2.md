# 20261106T0551Z-T5-scheduled-zipflag-k7m2
origin: scheduled
role: T5
status: source_fixed_waiting_ci
branch: feature/android-native-port
initial_head: 9584c243958f69c38c77ae67c6605d75c8fd1cad
scope: prompt/coordination/clients/T5/work/20261106T0551Z-T5-scheduled-zipflag-k7m2.md

## Actual finding
Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, CURRENT_OWNER_REQUIREMENTS.md, STATUS.md and live T team protocol. Owner phone confirms world/save/reopen only on artifact 42058825739. Inspected Actions 42164665929 completed failure, job 127718305743. 20 of 21 synthetic APK/OBB tests passed; encrypted-flag fixture failed *before* verifier because it searched literal ASCII backslash sequences rather than ZIP PK header signatures.

## Change
Commit 4a0ae4077c790d4f32ba9b7a35ebc80bad287807 changed only tests/test_t5_verify_apk_obb_pair.py: replace b\"PK\\\\x03\\\\x04\" and b\"PK\\\\x01\\\\x02\" with correct Python byte escapes. This restores negative test's ability to set flag bit 0 in local and central ZIP headers. The production verifier was already checking info.flag_bits & 1; no production code changed. No game files, Unity, releases, physical device or actual signed files were tested. CI confirmation pending; do not claim 21/21 until observed.

## Next
Inspect fresh Actions for commit 4a0ae407 and validate 21/21; if workflow path filter doesn't run, coordinate one cheap targeted run without duplicating active jobs. Then apply verifier to real signed checkpoint with aapt, delivery.json, and OBB SHA when safely accessible; separately track Resolution and device performance in T5 chat. Keep INTEGRATION-001 OPEN and NOT_READY 0/3. Preserve T4 mouse scope and T1-T3 graphics scope.
