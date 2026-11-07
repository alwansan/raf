# T5 scope 20261107T0953Z-T5-scheduled-zip-member-type-r8m2
origin: scheduled
base_sha: 8091829d02e5217c758a9e2c4c838ca17c0ce0d1
issue_id: INTEGRATION-001
resumed_from: 20261107T0845Z-T5-scheduled-6f2a
intended_files: scripts/t5_verify_retained_delivery_archive.py; tests/test_t5_retained_delivery_duplicate_json.py; this work record; independent session
experiment_key: t5-retained-zip-special-member-rejection-v1-script-7ffe2c8
resource_key: none (source-only)
hypothesis: authenticated outer archive and hashes should not accept Unix symlink/special-type members in transport or metadata, even if zipfile can read their data.
status: active
updated_at: 2026-11-07T09:53:00Z
No Unity/CI or release mutation; T4 mouse files untouched. Verify no conflicting T5 edits before patch.
