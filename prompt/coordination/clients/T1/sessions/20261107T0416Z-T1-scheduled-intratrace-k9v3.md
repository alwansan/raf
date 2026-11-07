# T1 scheduled FFT intra-trace provenance validation
session_id: 20261107T0416Z-T1-scheduled-intratrace-k9v3
origin: scheduled
base_sha: dacaef28c0d1ac028c19b1c6134b5786bbb1560e
resumed_from_sessions: 20261107T0312Z-T1-scheduled-provenance-order-f6k2; 20261107T0211Z-T1-scheduled-fft-trace-7c3a
owner_phone: 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628); world/save/reopen confirmed, packaging failed. CL 220911-559: 23884 water passes / 3850 FFT kernel errors; 230108-327: 39132 / 6026. No GPU timing inference.
work: prompt/coordination/work/WATER-001/20261107T0416Z-T1-scheduled-intratrace-k9v3.json
finding: pairwise provenance validation could accept identical mixed-input traces (input SHA or dispatch changed inside each capture). Added fail-closed intra-trace invariant for fixture_sha256, input_sha256, kernel and dispatch; two regression controls.
verification: source reviewed; Python tests not executed in this connector environment (network DNS prevents checkout). No Unity, Vulkan or Android test; no new game shader changes.
next: run python3 -m unittest discover -s tests -p 'test_t1_fft_trace_first_divergence_7c3a.py' -v; then obtain independently captured identical-input Vulkan/Unity keyed traces and verify FindKernel/SetTexture/Dispatch against original resource bindings. WATER-001 OPEN, NOT_READY 0/3. Preserve T4 physical mouse and T5 UI/Resolution work.
