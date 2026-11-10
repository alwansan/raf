# 20261110T1312Z-T1-scheduled-capture-alias-4f8d
origin=scheduled
role=T1
baseline=9dd04b325b32e84ba470ee0382099171c0a99307
issue=WATER-001 OPEN
experiment=T1-FFT-CAPTURE-ALIAS-20261110
files=scripts/t1_fft_capture_integrity_gate.py; tests/test_t1_fft_capture_alias.py; clients/T1/sessions/20261110T1312Z-T1-scheduled-capture-alias-4f8d.md
hypothesis=Current capture gate permits the same inode for Vulkan and Unity via different relative paths/hardlinks; this can falsely present one backend capture as two independent measurements.
method=Reject duplicate resolved capture file identity across backend/pass entries, add isolated regression tests; retain source-only/not GPU proof.
shared_resource=none; no Unity/CI build; T4 mouse and T5 Resolution untouched.
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md: world/save/reentry success, 220911-559 water=23884 kernel=3850; 230108-327 water=39132 kernel=6026, not unique faults.
status=planned
