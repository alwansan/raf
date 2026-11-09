# T5 scheduled — PNG byte-level evidence boundary (2026-11-09)
origin: scheduled
scope: independent T5 evidence tooling only; no Unity/Java/Mouse T4 edits
baseline: last observed HEAD 830bd8b4101736a47038c4a63efbcce3cb3ba796 (historical, NOT live HEAD)
experiment_key: T5-PNG-BYTES-20261109
hypothesis: scripts/t5_verify_shared_device_summary.py validates PNG metadata (png_sha256, png_bytes, URI) but not the image bytes; a corrupt or black PNG could pass metadata-only checks.
files: this work record; independent scripts/t5_verify_png_bytes.py; clients/T5/sessions/T5-20261109T0353Z-scheduled-png-bytes.md
shared_resource: none; no CI or Unity request.
prior_evidence: b6bd8599d8e2587af3002c929fb65d6ac040d793, 81f2eff9e0b677395b38aad4db959a36d04e5f03; CL/test/shared-20261108-232759-468049775. Test phone original 42058825739 remains the only confirmed world-save-reload run.
Non-goals: do not equate Mini Lab PNG with Raft runtime rendering, do not assert GPU timing or APK/OBB identity.
