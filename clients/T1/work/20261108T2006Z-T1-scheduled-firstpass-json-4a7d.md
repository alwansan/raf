# T1 WATER-001 isolated work
session_id: 20261108T2006Z-T1-scheduled-firstpass-json-4a7d
origin: scheduled
baseline_sha: 20766ed850c16bc18bfab37ed5c6913c64c9d3f0
scope: scripts/t1_fft_first_divergence.py and isolated regression test only; no Unity, no T4/T5, no CL writes.
experiment_key: t1-private-firstpass-duplicate-key-gate-20261108
hypothesis: duplicate JSON object keys in private pass manifest silently replace reference/observed and can make first divergence select a different capture; reject duplicate keys before any private pixel read.
shared_resource: none; no CI launch.
owner_baseline: 42058825739 phone world save/reentry succeeded from Artifact; water/kernel failures persist; publication failed.
prior: T1 axis identity fix a12076184214b348eaa8d1435730cde0f46a33da; 42513642491 success.
status: planned
