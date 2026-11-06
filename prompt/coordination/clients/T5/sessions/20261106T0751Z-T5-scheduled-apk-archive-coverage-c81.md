# T5 scheduled engineering checkpoint
session_id: 20261106T0751Z-T5-scheduled-apk-archive-coverage-c81
origin: scheduled
base_sha: df106c4e5caa21925cb6c420fd227d9fe2249a86
resumed_from_sessions: 20261106T0654Z-T5-scheduled-pair-ci-a7k2; 20261106T0248Z-T5-chat-native-delivery-retention-e8a3
issue_id: INTEGRATION-001
scope_file: prompt/coordination/clients/T5/work/20261106T0751Z-T5-scheduled-apk-archive-coverage-c81.md
status: waiting_ci

## Changes
- Scope committed at 71045e2; APK archive-specific regression tests committed at a14d9f1ef5f2b8c347c6c830c159e29b84f78b6f.
- Two new synthetic negative controls: Unix symlink entry in APK; encrypted ZIP member in APK. Existing OBB checks already cover these, and the production verifier applies _zip_structure to both archives. No change to verifier, assets, runtime, Settings, mouse or Unity.
- Last *proven* 21/21 tests: CI 42170921976 on 4a0ae407, before this change. The two newly added cases have NOT yet been CI-verified. Check workflow `.github/workflows/raft-t5-apk-obb-pair.yml` (or workflow name 'T5 INTEGRATION-001 APK OBB paired-file controls') for a run at a14d9f1 or descendant. If no run appears, use isolated cheap test after confirming no equivalent run.
- Latest observed HEAD before this work df106c4e; T4 platform controls 42182264431 and 42182264435 succeeded on d234b10; T1/T2 source tests are separate.
- Owner's artifact 42058825739 world/save/re-entry is owner-only phone evidence, not this source patch. Real signed APK/OBB manifest, OBB GUID, LogRaft GPU metrics and device mount remain unverified in this scope.
- Next: check 2 new regression tests with CI, fix any fixture error, then locate real signed APK/OBB delivery manifest and compare versionCode/name/size/SHA without republishing original game bytes. No duplicate Unity run.
