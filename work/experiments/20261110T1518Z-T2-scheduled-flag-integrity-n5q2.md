# T2 WATER-001 scope — 20261110T1518Z-T2-scheduled-flag-integrity-n5q2
origin: scheduled
baseline_sha: 829ffd9f64dfcf5ba248242a1210a63b1061c7cc
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; run 42058825739; CL 520c4cf
resumed_from: clients/T2/sessions/20261110T1316Z-T2-scheduled-utf8-gate-p8k2.md
experiment_key: T2-FOAM-RESOURCE-REPORT-READINESS-FLAG-INTEGRITY-20261110
hypothesis: verify_genuine_texture_sampler_pair_count accepts caller-mutated report with fabricated Unity/device verification flags, then returns it as authenticated numeric ABI evidence.
files: scripts/t2_foam_resource_abi.py; tests/test_t2_foam_resource_abi.py; this scope; own clients/T2/sessions entry.
shared_resource: none; source-only; no Unity/GPU/CI; no T3/T4/T5 edits.
verification_plan: reject fabricated readiness flags on root and each stage; preserve exact original six texture/sampler numeric ABI and fail-closed status.
status: scoped; not device validated; WATER-001 OPEN / NOT_READY 0/3.

source_commit: 45df93a457811593a829aee86623046293495002
test_commit: 1fdb768e89a5ab5a4c8ad66a7dc989962234fc91
result: verify_genuine_texture_sampler_pair_count now rejects fabricated/missing root and stage Unity/device/authenticity flags; 2 new regression methods cover 30 invalid mutations and missing keys. Exact numeric ABI remains unchanged.
verification: source reviewed, tests committed but NOT RUN. Existing CI 42842633300 in_progress at earlier source SHA; do not count it as validating test commit. No phone/Unity/pixel proof.
next: run pinned tests/test_t2_foam_resource_abi.py on 1fdb768e or later, then pursue original Foam texture identity/CB0 Unity upload proof and coordinate T3 material bindings.
