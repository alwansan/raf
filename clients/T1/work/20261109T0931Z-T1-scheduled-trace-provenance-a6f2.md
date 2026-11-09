# T1 independent work — 20261109T0931Z-T1-scheduled-trace-provenance-a6f2
origin=scheduled
baseline_sha=b66b28121d8394800e87609d251dce648e9c27b1
issue=WATER-001
hypothesis=Dispatch before/return traces from different device sessions or builds can currently pair if bounded sequence and kernel fields coincide. This is a provenance-integrity gap, not GPU evidence.
files=scripts/t1_fft_dispatch_pair_audit.py;tests/test_t1_fft_pair_provenance_a6f2.py;clients/T1/sessions/20261109T0931Z-T1-scheduled-trace-provenance-a6f2.md
experiment_key=T1-DISPATCH-PAIR-PROVENANCE-A6F2
shared_resource=none; no Unity/Actions requested
scope=only optional provenance fields; preserve legacy sequence-only traces with explicit non-proof flags.
owner_device=42058825739 world save/re-entry proven from Artifact; water/FFT open; signed packaging publish failed.
taken_over_from=clients/T1/sessions/20261109T0718Z-T1-scheduled-pair-presence-b8e4.md
