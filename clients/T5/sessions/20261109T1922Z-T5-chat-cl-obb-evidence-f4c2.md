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
