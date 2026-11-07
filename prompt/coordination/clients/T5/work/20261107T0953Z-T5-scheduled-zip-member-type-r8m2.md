# T5 scope 20261107T0953Z-T5-scheduled-zip-member-type-r8m2
origin: scheduled
base_sha: 8091829d02e5217c758a9e2c4c838ca17c0ce0d1
issue_id: INTEGRATION-001
resumed_from: 20261107T0845Z-T5-scheduled-6f2a
intended_files: scripts/t5_verify_retained_delivery_archive.py; tests/test_t5_retained_delivery_duplicate_json.py; this work record; independent session
experiment_key: t5-retained-zip-special-member-rejection-v1-script-7ffe2c8
resource_key: none (source-only)
hypothesis: authenticated outer archive and hashes should not accept Unix symlink/special-type members in transport or metadata, even if zipfile can read their data.
status: completed
updated_at: 2026-11-07T10:03:00Z
No Unity/CI or release mutation; T4 mouse files untouched. Verify no conflicting T5 edits before patch.

## Outcome
- Source commit 49848916b4321e5fa5378dad5d4ad35438a74e3a: reject explicit Unix symlink, device and directory members for every archive entry before metadata/payload reads; accept ordinary files and zero Unix type bits for compatibility.
- Regression commit 3037e1c597ab4bc1918f1a7f4449a9d6f118d7a4: five isolated member-type cases added alongside duplicate-key tests.
- Local isolated reproduction: five member-type assertions passed. Full repository unittest and actual retained multi-GB archive NOT executed (container GitHub DNS unavailable); no signed APK/OBB/device proof.
- No CI dispatched, no Unity shared resource touched. Next: run python3 -m unittest tests.test_t5_retained_delivery_duplicate_json -v in CI/checkout and inspect actual retained ZIP member mode bits before claiming compatible verification.
