# T5 work — 20261108T1453Z-T5-scheduled-obb-telemetry-k8p2
origin: scheduled
status: completed_source_only
base_sha: ee63cb4d9aed3331118581605e61df42d351f9b5
issue_id: INTEGRATION-001 / PERF-007
experiment_key: t5-host-testpack-v1-file-sha256-saf-android15-owner20261108
resource_key: none (source-only; no Unity/CI)
intended_files: apk-for-testing/examples/t5-package-telemetry-testpack.json; prompt/coordination/clients/T5/sessions/20261108T1453Z-T5-scheduled-obb-telemetry-k8p2.md; this work file
hypothesis: The existing mini-host file_sha256 SAF flow can capture user-selected APK/OBB hashes independently of SurfaceFlinger samples, while notes explicitly distinguish Unity FPS and GPU busy; this does NOT prove installed package identity.
taken_over_from: T5 signed OBB provenance and owner feedback 42058825739; T4 owns mouse capture and buttons.
Scope: add a declarative safe T5 testpack (no executable assets, no APK claim), validate against existing schema, preserve game and other workers.
Next: read HEAD/overlaps, validate, publish pack, record limits and checkpoint.

Result: 946d11dcc3690470e5a20bcd0f58d455b30c41bd; checkpoint a198dcf5ff81e25921aef1ba01470424e7d431e3. No APK/CI/device execution. Follow-up validation and integration outstanding.
