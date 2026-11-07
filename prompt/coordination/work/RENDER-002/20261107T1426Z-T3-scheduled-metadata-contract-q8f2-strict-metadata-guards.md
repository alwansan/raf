# T3 RENDER-002 isolated work scope
session_id: 20261107T1426Z-T3-scheduled-metadata-contract-q8f2
origin: scheduled
base_sha: 855a4c4b6a88eef216e4186b7c6094f300aedba4
owner: T3
scope: tests/test_t3_rgb_drift_strata.py (negative metadata controls only); own work and session markdown.
question: Can malformed per-pair metadata or unverified alpha parity pass the private RGB drift classification despite the 106/30 baseline?
experiment_key: T3-RGB-METADATA-NEGATIVE-20261107T1426Z
resource: local Python only; no ZIP2, Unity, GPU or native CI.
collision: no shared source files, no build request; T4 mouse and T5 resolution untouched.
acceptance: negative tests reject malformed srgb types and invalid alpha; do not expose raw textures; run against exact live source when available.
owner feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; world/save/reopen verified only on artifact 42058825739; white raft/hand and square smoke remain OPEN.
