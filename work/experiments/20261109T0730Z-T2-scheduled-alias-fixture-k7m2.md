# T2 WATER-001 — isolated receiver identity regression
session_id: 20261109T0730Z-T2-scheduled-alias-fixture-k7m2
origin: scheduled
issue_id: WATER-001
baseline_sha: 3160a7a8ccd6b3d8b0dda55d9aba23242c437f09
status: active
intended_files: android-port/Experiments/T2/alias_identity_reference_test.py; clients/T2/sessions/20261109T0730Z-T2-scheduled-alias-fixture-k7m2.md; work/experiments/20261109T0730Z-T2-scheduled-alias-fixture-k7m2.md
experiment_key: T2-FOAM-CFG-ALIAS-SYNTHETIC-RECEIVER-DISTINCTION-20261109
resource_key: none (CPU-only, source-free, no Unity, no original binaries)
hypothesis: field token equality does not imply object instance alias; conservative path join should distinguish known same, known different, and unknown references.
acceptance: synthetic tests for same receiver, different receivers, uncertain join, and differing field tokens; never infer original Foam pass equality from synthetic success.
resumed_from: clients/T2/sessions/20261109T0620Z-T2-scheduled-return-join-a91c.md; clients/T2/sessions/20261109T0212Z-T2-chat-return-value-flow-n7x3.md
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (world save/re-entry phone only; water OPEN).
