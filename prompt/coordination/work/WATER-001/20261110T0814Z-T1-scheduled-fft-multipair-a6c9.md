# T1 WATER-001 — independent multi-pair provenance audit
session_id: 20261110T0814Z-T1-scheduled-fft-multipair-a6c9
origin: scheduled
updated_at: 2026-11-10T08:14:28Z
status: active
issue_id: WATER-001
intended_files: tests/test_t1_fft_multipair_provenance.py; prompt/coordination/clients/T1/sessions/20261110T0814Z-T1-scheduled-fft-multipair-a6c9.md
experiment_key: fft-native-jsonl-multipair-provenance-v1:source-hook-8aa32937d423
resource_key: none (Python source-only, no Unity/GPU/CI)
Hypothesis: an apparently valid FFT Dispatch pair cannot survive later cross-build provenance drift or a duplicate before marker in the same bounded JSONL. Exercise this independently of the existing single-pair regression suite.
Evidence: owner report docs/DEVICE_FEEDBACK_42058825739_AR.md (42058825739 world/save/reentry, water/kernel errors); scripts/t1_fft_dispatch_pair_audit.py and tests/test_t1_fft_native_trace_contract.py read on feature/android-native-port.
Boundaries: no native Unity kernel binding or GPU proof; do not modify T4/T5, Unity, assets or shared status. Existing CI results do not cover this new test. Verify run before claiming PASS.
