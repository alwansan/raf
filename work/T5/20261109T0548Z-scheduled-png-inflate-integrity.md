# T5 independent PNG integrity scope
session_id: 20261109T0548Z-T5-scheduled-png-inflate-k8r2
origin: scheduled
baseline_sha: 0044c27256418394594110566b21d243c94b355e
scope: scripts/t5_verify_png_bytes.py and isolated T5 test; no Unity, no T4 mouse files.
hypothesis: current PNG validator checks CRC but accepts IDAT with invalid zlib compressed image payload, giving false confidence about image integrity.
experiment_key: T5-PNG-IDAT-INFLATE-20261109
shared_resource: none
acceptance: invalid IDAT compression rejected; valid PNG preserved; this is not a visual pixel comparison.
provenance: prior T5 PNG verifier bdd8142 and tests 3b192f2; owner device feedback 42058825739; T4 source changes untouched.
