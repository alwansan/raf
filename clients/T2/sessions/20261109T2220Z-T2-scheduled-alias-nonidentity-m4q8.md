# T2 scheduled session — 20261109T2220Z-T2-scheduled-alias-nonidentity-m4q8
origin: scheduled
baseline_sha: bdae2ce33a3088c9e5e32333d46829807dfec8be
scope: work/experiments/20261109T2220Z-T2-scheduled-alias-nonidentity-m4q8.md
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (world enter/save/re-entry confirmed on artifact; water and FFT still failing).
resumed_from: clients/T2/sessions/20261109T2020Z-T2-scheduled-crosspass-receiver-gate-r8v3.md; prompt/coordination/clients/T2/sessions/20261109T2116Z-T2-scheduled-foam-alias-guard-k7m2.md
result: identified unsound distinct-object inference in source-free alias model: two disjoint SSA value tokens can reference one runtime Texture. Changed different_instance_proven to conservatively return False pending object-level provenance, and added a regression for two field loads potentially aliasing one RenderTexture.
commits: scope d15a979a65eb9c8d94ab75002330c4ab5f124a04; source 7c4c88b1ec7d9889bcf5ea01d323165302e9bd9a; regression 30ba7d6c1055c4314630d7923c1668e32b88eb69
verification: code and tests published, but local unittest could not run because raw.githubusercontent.com DNS resolution failed. No claim of CI success, Unity integration, original Foam runtime identity or device rendering.
next: run python -m unittest -v tests.test_t2_foam_alias_dataflow in CI or networked checkout, then add actual CIL object-identity provenance/receiver analysis before allowing a nonalias verdict. WATER-001 OPEN / NOT_READY.
