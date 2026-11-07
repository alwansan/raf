# T1 scheduled FFT provenance preflight
session_id: 20261107T0312Z-T1-scheduled-provenance-order-f6k2
origin: scheduled
base_sha_observed: 480c3285b3f66e571cc453e50dda9ce5706165aa
owner_phone: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner world/save/reopen confirmed on 42058825739 artifact, packaging failed. CL water pass/kernel counts 23884/3850 and 39132/6026; not GPU timings.
resumed_from: prompt/coordination/clients/T1/sessions/20261107T0211Z-T1-scheduled-fft-trace-7c3a.md
work: prompt/coordination/work/WATER-001/20261107T0312Z-T1-scheduled-provenance-order-f6k2.json
source_fix: 8b41b84b745331b5984871b246eb4c58e431de98
regression: 58b8c0d7950f89610050847be24a45e20071aed9
finding: prior comparator returned early coordinate divergence before checking provenance on later keyed rows, allowing different input_sha256/fixture/kernel/dispatch to masquerade as numeric parity experiment. Now all provenance fields are validated before coordinate/value comparison. Adversarial two-row test added.
verification: not executed; source-only review, no Unity/GPU/phone build or fresh original capture. No shader or T4/T5 files changed. T1 trial vote remains لا يحتاج; WATER-001 OPEN; NOT_READY 0/3.
next: run python3 -m unittest discover -s tests -p 'test_t1_fft_trace_first_divergence_7c3a.py' -v (expected 10 tests); then compare independently captured original Vulkan and Unity keyed reads, and prove FindKernel/SetTexture/Dispatch binding.
