# T1 scope — 2026-11-11T12:10Z
session_id: 20261111T1210Z-T1-scheduled-fft-ambiguous-nearest-8e31
origin: scheduled
baseline_sha: 83a6a7d9f200640f17dbc4e81a8837ec6a283582
issue: WATER-001
experiment_key: fft-nearest-marker-ambiguity-20261111-T1
files: scripts/t1_fft_pass_proximity.py; scripts/test_t1_fft_pass_proximity_ambiguity.py; this work file; dedicated T1 session.
shared_resource: none; no CI/Unity/build.
hypothesis: alphabetical tie-breaking between equally close but distinct water pass markers fabricates a single apparent pass association. Preserve ambiguous matches explicitly without asserting program identity or causality.
owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; phone world save/reopen success; water/FFT errors remain. Later 2026-11-08 mini lab requirements also apply.
coordination: no T4 mouse or T5 resolution/right-panel edits; no changes to shared statuses.
acceptance: unique nearest remains unchanged; equal-distance different passes reported ambiguous and not counted as unique; duplicate markers of same pass not ambiguous; unit tests run locally where possible.
