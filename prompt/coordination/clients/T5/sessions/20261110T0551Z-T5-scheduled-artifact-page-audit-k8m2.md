# T5 scheduled session 20261110T0551Z-T5-scheduled-artifact-page-audit-k8m2
origin: scheduled
resumed_from_sessions: previous T5 scheduled 2026-11-10 parity/CI and button-source audits (see prior commits 3349712 and 176966c)
base_reference: feature/android-native-port; scope commit 1b47873e721a3a484b94696132a9f1129b91e977
issue: DELIVERY-APK-OBB-42058825739

## Verified this run
Read AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, DEVICE_FEEDBACK_42058825739_AR.md and T_TEAM live coordination. Owner phone proof remains limited to run42058825739, source e9c358eda01785b65e4eb14f18723da426635628. Report identifies delivery artifact 13441227298 and signed checkpoint 13441766832, not an attested installed APK/OBB pair.
GitHub Actions artifact listing through the available first-page-only connector for run42058825739 returned exactly four early diagnostic entries: 13431563116 (833 bytes), 13431483005 (1990), 13431363060 (3242), 13431142944 (2095). The two reported signed/delivery artifact IDs were not included in that limited response. This is a **pagination/coverage limitation**, not evidence they are missing. Avoid false claims about APK versionCode, OBB name/size/SHA or signed-pair matching.
Cross-checked CI42745684716 jobs: job129597087706 offline SUCCESS; steps compile adapted local gameplay and local RPC, **not** T5 Python parity suite or Unity editor. Source parity checker scripts/t5_validate_runtime_staging_parity.py still fail-closed on name drift, symlinks, and bytes, but this inspection is not a test execution.
Read latest shared Mini readiness: r5 delivered CI42691609924, v0.2.17 debug signed; unrelated to full Raft XAPK. T4 owns physical mouse captured buttons. No build, dispatch, source mutation or phone execution occurred.

## Result and limits
Result: identified an actionable verification blind spot: first-page artifact listing must not be used to conclude APK/OBB absent or matching. Full artifact enumeration or exact artifact-ID download with manifest extraction is required; then compare versionCode, OBB filename/bytes/SHA and APK signature. No phone FPS or GPU timing was measured in this run. Historical LogRaft mean 22.29 FPS/57 samples and HUD 18.27 FPS/p95 82.82ms remain historical only.
next_step: use paginated GitHub REST or exact artifact IDs 13441227298/13441766832; extract manifest and SHA256SUMS, attest signed APK/OBB, compare CL session build identity; coordinate any Unity request with T4/T1–T3 and avoid duplicate build. Continue Resolution existing Settings only, not a second selector; buttons right-side source present but device confirmation pending.
status: completed_read_only_audit; game NOT_READY 0/3.
