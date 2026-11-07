# T3 — 20261107T2130Z-T3-scheduled-full-coverage-p6n8
origin: scheduled
track: RENDER-002
status: SOURCE_FIXED_PENDING_TEST; NOT_READY
resumed_from_session: 20261107T2030Z-T3-scheduled-unique-pair-v2k7
base_sha: 65548eb01c755ed9d6234a49224c900439dec062
scope_commit: 7deef69d5647a63aec074bf201f9952fb6d83ec3
source_commit: 82dea22c5a7a7a48ffd34ee59295e159eb8ba543
test_commit: 3339fe1eabf5146d6332fc2173c4de3cd48bf8c5
origin evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pin 520c4cf409aa20a4db54ff80ed87d8807d9cba57; authentic 106 pairs/30 RGB drifts in CI41968665857.

## Actual work
Added opt-in `require_all_metadata` and CLI `--require-all-metadata` to reject incomplete format/source_srgb/importer_srgb coverage across *all* 106 original/export pairs, including padded UNKNOWN sentinels. Existing `--require-metadata` (nonzero coverage only) and `--require-drift-metadata` semantics unchanged. Added source-level regression test for 1/106, 105/106 and 106/106 known metadata.

## Verification boundary
Published code and regression test via GitHub connector; tests NOT executed: local git cannot resolve github.com (DNS), and no matching dedicated test CI has been run for this commit. Existing Actions latest list included 42412029095 success and 42412029098 failure, unrelated to this test. No original ZIP2 extraction, private manifest, CL pixel inspection or Unity/phone test performed. No game assets, .meta/GUID, .rgd, audio, Settings, touch or build requests changed.

## Next
Run `PYTHONPATH=scripts python -m unittest discover -s tests -p test_t3_rgb_drift_strata.py` on published source. Generate authenticated per-pair original/export metadata privately from ZIP2 and require `--require-unique-pairs --require-drift-metadata --require-all-metadata`. Trace white raft/hand and square smoke from CL image to actual Renderer/Material/Shader PPtr, texture/alpha/Blend/keywords and lighting. Do not claim a graphics fix from a metadata classifier. RENDER-002 OPEN / NOT_READY.
