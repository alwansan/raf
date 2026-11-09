# T5 chat device OBB provenance reconciliation
session_id=20261109T1922Z-T5-chat-cl-obb-evidence-f4c2
origin=chat
base_sha=7697c28fa0d93302ffcecb0e589f9e7b53c29be6
work=work/T5/20261109T1922Z-T5-chat-cl-obb-evidence-f4c2.md
resumed_from=20261109T1855Z-T5-chat-obb-contract-b1d7,20261109T1750Z-T5-scheduled-obb-json-a9e4
scope=New isolated source-only CL/test T5-02 evidence verifier and phone check guide. No modification of scheduled classifier or Unity, no APK build.
source_cl=test/shared-20261108-230157-466487336/summary-20261108-230157-466487336.json @ CL main 24a677fc8fa4749c0bcf8a3cac01fa80b1641c86 blob SHA 3a5bdc24f365259ba6753f133205ee7c7432f48a
baseline=Old signed v89 APK and main OBB already FULL SHA verified CI42117471172, CI42228262902, CI42230326050; 2026-11-05 raw CL warning three patch.89 optional no main warning CI42119428667.
new_finding=Real owner mini T5-02 EVIDENCE_READY bytes=2301280507, SHA256 prefix 911a53bc1dd4, vs old signed main.89 bytes=2301256312 prefix 660b6c0909ae. Exact size delta +24195. SAF does not record selected basename/location => different selected bytes NOT OBB corruption or installed-file mismatch.
status=active
next=Implement and validate independent source-only parser/CI against pinned CL blob with fail-closed ambiguity handling; document exact on-phone filename/version/site steps.

## Engineering result (completed)
- Wrote new independent read-only parser `scripts/t5_reconcile_owner_saf_obb.py` (commit 1e25434bb851643ef7d0e4abb09e25e9b4def90b), source-free adversarial tests `tests/test_t5_reconcile_owner_saf_obb.py` (final fd8cd4603f77c0f80560afc232875db200db58dd), source-only CI `.github/workflows/raft-t5-owner-saf-obb-provenance.yml` (f04f50bd9758c9d84c5a7257770a1cbe2eb7d07a).
- First CI [42680558991](https://github.com/alwansan/raf/actions/runs/42680558991) failed after 14/14 synthetic tests and 2/2 raw CL git blob checks, only because test directory `shared-...` differs from internal summary.session `...`. Source fix [384fef37](https://github.com/alwansan/raf/commit/384fef37b8250a74ff5d985a5a635dd007bef7d6) normalized the single expected prefix; added two negative/positive tests for this exact real schema.
- Final source-only CI [42680745095](https://github.com/alwansan/raf/actions/runs/42680745095) **SUCCESS** on `fd8cd4603f77c0f80560afc232875db200db58dd`: **16/16 unit controls**, authenticated both CL report Git blob SHAs `3a5bdc24f365259ba6753f133205ee7c7432f48a` and `a4f2255e49039fbdd96df1aec8c0ca424d24c36f` pinned to CL commit `24a677fc8fa4749c0bcf8a3cac01fa80b1641c86`.
- Actual first report `T5-02 EVIDENCE_READY`, observed `bytes=2301280507` SHA256 begins `911a53bc1dd4` while original authenticated version 89 OBB `bytes=2301256312` SHA256 begins `660b6c0909ae` (+24195 bytes). Classifier **DIFFERENT_FROM_OLD_REFERENCE**, not corrupted installed OBB. Actual later report `T5-02 NEEDS_INPUT` no measured digest; previous reading still valid evidence for its distinct session.
- Published owner steps and limitations in [Arabic guide](../../../docs/T5_OWNER_OBB_DEVICE_CHECK_2026-11-09_AR.md). Only owner-supplied selected filename/location and version information can bind T5-02 SAF hash to installed file; ask for no 2GB upload and do not repeat old byte comparison. Android15 may block Android/obb SAF.
- Original v89 APK+OBB pair full SHA/authentic signature verified in prior CIs 42117471172,42228262902,42230326050; original 3 GUID warnings patch.89 only CI42119428667. None proves current phone mount/graphics.
- No changes to scheduled T5 classifier scripts, T1-T4 paths, original game, CL repo or full/native/mini build request. Readiness NOT_READY 0/3.
status=completed
next_step=Review new CL/test event/summary only after owner provides file provenance; if game version !=89 identify same-version signed manifest, do not mark OBB corrupt due old-version mismatch. Await independent T3 v13 screenshot proof and T4 actual physical mouse button/scroll phone verification separately.
