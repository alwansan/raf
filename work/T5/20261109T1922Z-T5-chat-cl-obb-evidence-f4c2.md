# T5 work: original OBB vs owner SAF hash provenance (read-only)
session_id=20261109T1922Z-T5-chat-cl-obb-evidence-f4c2
origin=chat
status=active
base_sha=7697c28fa0d93302ffcecb0e589f9e7b53c29be6
resumed_from_sessions=20261109T1855Z-T5-chat-obb-contract-b1d7;20261109T1750Z-T5-scheduled-obb-json-a9e4
issue_id=INTEGRATION-001-OWNER-OBB-EVIDENCE
scope=Reconcile actual CL/test T5-02 SHA256/bytes with SHA-verified old version89 OBB reference; ensure DIFFERENT_BYTES is not misreported as corruption or installed OBB.
intended_files=scripts/t5_reconcile_owner_saf_obb.py,tests/test_t5_reconcile_owner_saf_obb.py,.github/workflows/raft-t5-owner-saf-obb-provenance.yml,docs/T5_OWNER_OBB_DEVICE_CHECK_2026-11-09_AR.md,work/T5/20261109T1922Z-T5-chat-cl-obb-evidence-f4c2.md,clients/T5/sessions/20261109T1922Z-T5-chat-cl-obb-evidence-f4c2.md,prompt/coordination/B_TEAM/events/T5/20261109T1922Z-T5-chat-cl-obb-evidence-f4c2.json
experiment_key=t5-saf-obb-identity-cl-main-24a677fc-summary-3a5bdc24-original-v89-2301256312-sha660b6c0909ae-v1
resource_key=source-only-cl-saf-provenance-no-native
owners=T5 new script and CI only, no scheduled T5 scripts/t5_classify_obb_guid_logs.py, no shared Mini/Unity paths, T1-T4 unaffected
start_actions=2026-11-09 ~19:22UTC: T2 Foam and Android platform CI42680030121/42680030029 in_progress, no relevant T5 duplicate.
source_provenance=CI42117471172 APK+OBB actual match, CI42228262902 real APK signature, CI42230326050 actual OBB SHA, CI42119428667 original CL optional patch warnings.
input_cl_commit=24a677fc8fa4749c0bcf8a3cac01fa80b1641c86
input_cl_blob=3a5bdc24f365259ba6753f133205ee7c7432f48a
input_cl_path=test/shared-20261108-230157-466487336/summary-20261108-230157-466487336.json
observed_t5_02=EVIDENCE_READY bytes2301280507 SHA256_prefix911a53bc1dd4 ; filename/location NOT LOGGED
original_v89_obb=main.89.com.alwansan.raft.androidtest.obb bytes2301256312 validated SHA256_prefix660b6c0909ae
hypothesis=Owner SAF selected bytes do not match immutable v89 OBB, but selection filename/version/location missing so no corruption claim.
next=Run isolated source-only GitHub Actions with source-free tests and authenticated pinned CL blob, report strictly bounded fields, publish Arabic owner steps.

## Executed results and release of scope
status=completed
real_ci_first=https://github.com/alwansan/raf/actions/runs/42680558991 (failure due to CL summary.session lacking shared- folder prefix; 14 synthetic tests and both pinned Git blob hashes PASS)
root_cause=CL summary session id is 20261108-230157-466487336, directory is shared-20261108-230157-466487336. Reconciler now checks both without losing strict folder binding.
fix_commit=384fef37b8250a74ff5d985a5a635dd007bef7d6
latest_test_commit=fd8cd4603f77c0f80560afc232875db200db58dd
latest_real_ci=https://github.com/alwansan/raf/actions/runs/42680745095 SUCCESS (16/16 tests; 2 authenticated real CL/test summaries)
actual_observed_first=EVIDENCE_READY bytes2301280507 SHA-prefix911a53bc1dd4, +24195 bytes vs old v89 OBB2301256312 SHA-prefix660b6c0909ae: DIFFERENT_FROM_OLD_REFERENCE; filename/location unknown; no corruption proven.
actual_observed_later=T5-02 NEEDS_INPUT, NO_COMPLETED_DIGEST; does not undo previous evidence.
owner_guide=docs/T5_OWNER_OBB_DEVICE_CHECK_2026-11-09_AR.md
phone_step=Get selected file basename/location and installed versionCode for older SHA; if unknown, optionally use latest shared Arabic portrait Mini T5-02 SAF on known file, export only summary/events JSON to CL/test. Do not send 2GB OBB/game assets, no new Unity/mini build.
limits=No real Android installed OBB mount, no comparison against same-version reference for unknown OBB, no new device install. Full XAPK NOT_READY 0/3.
finished_at_utc=2026-11-09T19:11Z
