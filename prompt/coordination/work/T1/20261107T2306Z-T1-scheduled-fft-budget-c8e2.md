# T1 WATER-001 — bounded FFT capture manifest
session_id: 20261107T2306Z-T1-scheduled-fft-budget-c8e2
origin: scheduled
baseline_sha: bbd2b39f96e42dd9e946e01a4d2463befc5a4e91
scope: scripts/t1_fft_first_divergence.py; scripts/tests/test_t1_fft_capture_budget.py; clients/T1/sessions/20261107T2306Z-T1-scheduled-fft-budget-c8e2.md
hypothesis: 1 MiB JSON may enumerate many 64 MiB captures and exhaust memory despite per-file cap. Reject excessive pass count and aggregate bytes before reading data; preserve numerical comparison and privacy.
experiment_key: t1-fft-private-capture-budget-20261107
shared_resource: none; no CI dispatched
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, CL 520c4cf; artifact success world save/reentry; water 23884/39132, kernel6 3850/6026; do not infer identity.
coordination: no Unity/build; T4 physical mouse and T5 resolution/buttons unchanged. Existing FFT comparator only.
