# T3 — 20261107T2030Z-T3-scheduled-unique-pair-v2k7
origin: scheduled
track: RENDER-002
status: SOURCE_PATCHED_TEST_PENDING; NOT_READY
base_sha: ddd9a65ab76f0a6c93ecf3fffe41c562bdd8e01e
scope_commit: fe7fbbdf689a49953e800c423f178019b1dd462b
source_commit: eebfae98ec1c24833155f0ac5712ce67da6e8786
test_commit: 2ad51ecb714c529baa5013831aa9af5db4344987
resumed_from_session: 20261107T1929Z-T3-scheduled-drift-provenance-f8q4
origin_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57; 41968665857 original/export 106 pairs, 30 RGB drifts.

## Actual change
The 106/30 aggregate cohort could pass even if the same original/export pair appeared twice and another was absent. Added optional `require_unique_pairs` / CLI `--require-unique-pairs` requiring private integer `pair_ordinal` within 0..105, rejecting duplicate/missing/bool/out-of-range values. Ordinals never appear in classifier output. Added regression test for valid cohort, duplicate and missing/boolean ordinal. Existing callers remain compatible until their private exporter supplies verified ordinals. An ordinal alone is NOT proof of original source identity; private exporter must assign it after independently verifying distinct original/export keys.

## Evidence and limitations
Read phone feedback: artifact 42058825739 entered/saved/re-entered world; publishing failed; white hand/raft and square smoke remain. Water pass and FFT failures reported in CL. Reviewed exact current classifier and tests via GitHub connector. Local git cannot resolve github.com; published Python tests NOT run. No private original/export pair manifest accessible; no pixel/Shader PPtr verification or device test. No Unity/native build dispatched; no changes to assets, .meta/GUID, .rgd, audio, Settings or T4/T5 files.

## Next
Run `PYTHONPATH=scripts python -m unittest discover -s tests -p test_t3_rgb_drift_strata.py` on the published commit. In the private ZIP2-authenticated exporter assign pair_ordinal only after distinct identity verification; then run `--require-unique-pairs --require-drift-metadata`. Trace CL white hand/raft and square smoke to actual Renderer/Material/Shader PPtr, texture alpha, blend and lighting; do not claim visual fix from aggregate statistics. RENDER-002 OPEN / NOT_READY.
