# T2 scheduled work — JSON producer guard

origin: scheduled
session_id: 20261105T1418Z-T2-scheduled-a91c
baseline_sha: 6c2279ce8c02e8083d35726f1a0c9d7866e31e72
taken_over_from: T2 20261105T0023Z-T2-foam-texture-identity and later T2 digest sanitizer sessions (independent continuation)
scope: new tests/test_t2_foam_json_product_guard.py; no existing test or shader files modified.
shared_resource: none; no Unity/GPU CI requested.
hypothesis: the current safe report product can be validated with a strict recursive JSON allowlist that rejects future private numeric pair/digest/name fields, not just a key-level check.
experiment_key: T2-FOAM-JSON-PRODUCT-ALLOWLIST-20261105
plan: create source-only unittest invoking compare_private_names with synthetic private values, serialize to JSON and assert strict allowed keys/recursive absence of secrets. Verify with python unittest when available; if not, record unverified. Do not infer authentic shader binding from synthetic tests.
latest_evidence: Foam original CI 41941354379 (0/6 literal identity); historical 42034986678 failure in summary regeneration; current HEAD above; T3 workflow 42043583643 queued.
next_step: run source-only CI on this new test or validate locally, then move to authentic numeric-to-SPIRV mapping.
