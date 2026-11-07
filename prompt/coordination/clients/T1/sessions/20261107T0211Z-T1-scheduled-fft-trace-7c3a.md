# T1 scheduled FFT trace comparator checkpoint
session_id: 20261107T0211Z-T1-scheduled-fft-trace-7c3a
origin: scheduled
resumed_from_sessions: 20261107T0106Z-T1-scheduled-k4p8; 20261107 T1 Vulkan Phi/CFG sessions
base_sha_observed: 9b89f62772c2c61f6269fd2249f8560af1522892
owner_device_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628). Owner entered, saved, exited, re-entered world; packaging release failed. CL session 220911-559: 23884 water pass and 3850 FFT kernel errors; session 230108-327: 39132 and 6026. These counts are not GPU timestamps.
scope: isolated sanitized JSONL first-divergence checker; no Unity build, shader changes, mouse/Resolution edits or new Android claims.
work: prompt/coordination/work/WATER-001/20261107T0211Z-T1-scheduled-fft-trace-7c3a.json
commits: c1f85d54f678da83e417bf9f47e3ca95ed1547f3; 81ee4034e85d1f52a088f7d6560af335627587ca; 9900cd8e205d5fa7f61e6d55f692ad852042bc4e; 85a158120e782d91a90f1daa490f472f9cada45f
implementation: scripts/t1_fft_trace_first_divergence_7c3a.py and tests/test_t1_fft_trace_first_divergence_7c3a.py. Fail-closed for missing/duplicate JSON fields, invalid types/nonfinite numbers, duplicate invocation/read keys, nonidentical inputs, fixture, kernel or dispatch. Different translated source hashes intentionally allowed. First divergence sorted by numeric pass/invocation/read site. No proprietary data.
verification: tests published but NOT RUN by CI; avoid claiming pass. Git local network DNS unavailable; GitHub connector used for publishing.
next: execute python3 -m unittest discover -s tests -p 'test_t1_fft_trace_first_divergence_7c3a.py' in CI or checkout; obtain two independently captured traces with same fixture and input SHA, record exact first mismatch; then probe Unity FindKernel/SetTexture/Dispatch against authenticated compute resources. WATER-001 OPEN; NOT_READY 0/3.
