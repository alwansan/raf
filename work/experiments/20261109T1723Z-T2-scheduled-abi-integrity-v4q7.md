# T2 WATER-001 independent scope
session_id: 20261109T1723Z-T2-scheduled-abi-integrity-v4q7
origin: scheduled
baseline_sha: ae69a9380f730ff7d595389533fdf055ada8ea6f
issue: WATER-001 OPEN NOT_READY
experiment_key: T2-FOAM-REPORT-INTEGRITY-20261109
files: scripts/t2_foam_resource_abi.py; tests/test_t2_foam_resource_abi.py; clients/T2/sessions/20261109T1723Z-T2-scheduled-abi-integrity-v4q7.md; this work file
hypothesis: verify_genuine_texture_sampler_pair_count trusts source row descriptor totals and numeric SHA metadata after combine; tampered report can claim cardinality while these source fields drift. Enforce exact structural integrity and reject malformed hashes and totals, without implying original resource identity.
shared_resource: none; no Unity, no private payload, no native build. T3 materials and T4/T5 input/Resolution untouched.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; world save/re-entry on artifact confirmed, water failures remain.
previous_proof: Actions 42653175246 succeeded at c24317d8; no duplicate dispatch.
next: add fail-closed source metadata checks and regression fixtures, run source-only tests, record result.
