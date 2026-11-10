# T1 WATER-001 scope — 20261110T0606Z-T1-scheduled-native-provenance-3e7b
origin=scheduled
baseline_sha=9c96a135a27d249cb1a4927727ea392c1f21c98f
owner=T1
area=FFT trace evidence; source-only
files=tests/test_t1_fft_native_trace_contract.py (append-only), work/experiments/20261110T0606Z-T1-scheduled-native-provenance-3e7b-scope.md, clients/T1/sessions/20261110T0606Z-T1-scheduled-native-provenance-3e7b.md
hypothesis=Native original FFT trace must reject a return from another build or a trace with missing session provenance; existing audit supports this but the dedicated native contract suite lacks explicit cases.
experiment_key=T1-WATER-001-native-provenance-20261110T0606Z-T1-scheduled-native-provenance-3e7b
shared_resource=none; no Unity, no Actions dispatch
collision_check=T4 mouse and T5 runtime work separate; do not modify their files.
owner_feedback=docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 world/save/reopen passed, water FFT unresolved; newer 8 November lab report takes precedence where applicable.
CI=42747722414 success on 4c50a7b, does not prove tests committed later; current HEAD 9c96a135.
Acceptance=two additional native trace contract tests; source-only, not GPU proof.
