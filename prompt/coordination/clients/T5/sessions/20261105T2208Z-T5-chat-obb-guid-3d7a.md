# T5 chat — original phone OBB GUID warning classification
- session_id: 20261105T2208Z-T5-chat-obb-guid-3d7a
- origin: chat
- base_sha: 01cc44242f0abcbae9cb0900eff82c8b4b27bcf8
- resumed_from_sessions: 20261105T2153Z-T5-chat-signed-pair-4e91; 20261105T2110Z-T5-chat-retain-delivery-a6f8
- issue_id: INTEGRATION-001
- status: active
- work: prompt/coordination/work/INTEGRATION-001/20261105T2208Z-T5-chat-obb-guid-3d7a.json
- experiment_key: t5-CL-pinned-520c4c-guid-warning-version89-patch-vs-main-actual-log-parity-v1
- resource_key: CL-read-only-20261105-phone-log-sha-blobs
- source CL fixed commit 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Session 220911-559 segment 1 blob d50b9fde330c425e15d444922c214a5b112bb264 contains one 'Unable to load GUID' for *patch.89...obb*, segment2 none. Session 230108-327 seg1 blob cb3a3318b604c1cfbc43583e05580a39bcb66c81 contains two same patch.89...obb; other three segments contain none.
- Actual signed source artifact of run42058825739, versionCode89 verified from aapt, signed APK cryptographic signature and pair SHA as CI42117471172 success.
- Source delivery.json logical files APK, *main.89.com.alwansan.raft.androidtest.obb*, XAPK. No *patch.89* signed artifact declared or shipped. Three warning paths are patch, not main. Does not prove phone patch file absence or mounted main path.
- planned work files: scripts/t5_classify_obb_guid_logs.py, tests/test_t5_classify_obb_guid_logs.py, .github/workflows/raft-t5-obb-guid-log-identity.yml, docs/T5_REAL_CL_OBB_PATCH_GUID_DIAGNOSIS_2026-11-05.md.
- Avoid T1–T4 and concurrent T5 scheduled Resolution code. No Unity/no game patch/no Unity warning suppression. Next: implement classification plus source-free CI, document genuine CL counted evidence and limitations.

## Completed checkpoint: real owner phone GUID lines (2026-11-05 22:13 UTC)

- [CI42119428667](https://github.com/alwansan/raf/actions/runs/42119428667), job127567590987, source `93ca7ea63c2928514bfac35608725f53a368df55`: **COMPLETED SUCCESS**; 16/16 synthetic categorization controls and all **6 real CL log Git blob SHAs** verified after downloading original pinned source read-only. NO raw logs/game files uploaded.
- Actual real owner phone observations independently reproduced (not a guess from aggregate summaries): `20261105-220911-559` 1 exact `patch.89.com.alwansan.raft.androidtest.obb` GUID warning; `20261105-230108-327` 2 exact same optional patch.89 GUID warnings; **ZERO actual `main.89` GUID warning** across all six segments.
- Signed delivery (CI42117471172) original versionCode89 includes `main.89.com.alwansan.raft.androidtest.obb` as only OBB and no patch. The original signed APK signature and main OBB hashes pass, but installed main OBB device SHA/mount remains UNKNOWN.
- Reusable read-only classifier `scripts/t5_classify_obb_guid_logs.py` and 16 adversarial tests reject conflating actual MAIN errors, foreign package/version and declared PATCH errors with optional unshipped PATCH lookups; **no Unity error suppressed** or bogus patch OBB created. Workflow `.github/workflows/raft-t5-obb-guid-log-identity.yml` runs only this exact pinned original source with no Unity.
- [Full report](../../../docs/T5_REAL_CL_OBB_PATCH_GUID_DIAGNOSIS_2026-11-05.md), experiment `prompt/coordination/experiments/T5/20261105T2208Z-T5-chat-obb-guid-3d7a.json`, event `prompt/coordination/B_TEAM/events/T5/20261105T2208Z-T5-chat-obb-guid-3d7a.json`, work `prompt/coordination/work/INTEGRATION-001/20261105T2208Z-T5-chat-obb-guid-3d7a.json` completed.
- Residual real device shader/FFT errors remain high; do not waste main build/OBB packaging time on observed optional patch warning alone. Do not claim no underlying Unity GUID defect; only observed main warning count is zero.
- No T5 scheduled Resolution, T1/T2 water, T3 materials, T4 mouse, audio, Settings, GUID source, Unity/native build, LFS or release touched. INTEGRATION-001 OPEN, overall NOT_READY 0/3.
- **next_step**: when device and matched signed APK available, compare installed main.89 exact size+SHA with released package and actual Android mount. Separately prioritize shader/FFT/white materials by actual log root counts; don't fabricate patch OBB or hide Unity warning.
- status: completed
