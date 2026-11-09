# T5 scheduled — preexisting APK/OBB verifier discovered, duplicate avoided
session_id: 20261109T1459Z-T5-scheduled-obb-pair-a7c2
origin: scheduled
baseline_sha: bca32f1a88004047e9fa7df473b85a1c1f93e1d9
work: prompt/coordination/clients/T5/work/20261109T1459Z-T5-scheduled-obb-pair-a7c2.md
experiment_key: t5-apk-obb-pairing-static-v1
status: EXISTING_IMPLEMENTATION_FOUND / DEVICE_UNVERIFIED

## Verified live
Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, current requirements/status and T_TEAM protocol, plus T5 20261109T0209Z chat and 0153Z scheduled checkpoints. Artifact 42058825739 exposes four small diagnostics (IDs 13431563116, 13431483005, 13431363060, 13431142944); owner references delivery 13441227298 and signed 13441766832, which are not among that run's first-page artifacts. No inference of deletion, absence or installation identity is justified.

Before implementing the scoped checker, fetched scripts/t5_verify_apk_obb_pair.py at blob 3de6c79b9efd0b89cab34a36a8fa0c6fb53b5f1f. Existing source ALREADY checks delivery.json schema, exact APK/OBB/XAPK records, part SHA/size totals, aapt package/versionCode, main OBB naming, full APK/OBB SHA/size, ZIP local/central metadata and ARM64 IL2CPP headers. A duplicate create_file returned GitHub 422 (existing file), and no existing source was overwritten. The proposed smaller checker would regress coverage, so intentionally abandoned. This is a source audit, NOT actual APK/OBB verification.

## Next concrete step
Acquire completed delivery.json, signed Raft-Android-Test.apk and main.<versionCode>.com.alwansan.raft.androidtest.obb from same delivery lineage (not just diagnostic artifacts). Run `python scripts/t5_verify_apk_obb_pair.py --delivery delivery.json --apk Raft-Android-Test.apk --obb main.<code>.com.alwansan.raft.androidtest.obb --aapt aapt` with exact real paths; save digest report and signer certificate fingerprint separately. Confirm on-device OBB mount and assets; do not infer from static check. T4 owns mouse; game UI Resolution/right buttons still require device verification. No Unity/build/action triggered; no device claim; no other worker files edited. World/save/reentry remains 42058825739-only. Full game NOT_READY.
