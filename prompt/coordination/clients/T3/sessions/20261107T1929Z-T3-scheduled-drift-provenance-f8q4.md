# T3 scheduled — 20261107T1929Z-T3-scheduled-drift-provenance-f8q4
origin: scheduled
track: RENDER-002
status: SOURCE_PATCHED_TEST_PENDING; NOT_READY
initial_head: 71b440d93b74c7236beef75119d15f29881ad67c
scope_commit: 35a279979c8696693df524c47a7689040f9e24f4
source_commit: b86ca8caffa86a54807e4ea3c904a408337481f2
test_commit: 1a5ba511f5ee2cfd35cf7ed022fcaeae37986f4a
head_before_session: 1a5ba511f5ee2cfd35cf7ed022fcaeae37986f4a

## Read and retained evidence
Owner phone report 5 Nov: artifact 42058825739 entered/saved/re-entered world; packaging failed; white hand and raft, lighting, square smoke still open. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 and photo links are referenced, not visually reverified in this cycle. Earlier authentic texture comparison 106 pairs, 30 RGB drift, lacks individual format/source_srgb/importer_srgb. T3 prior scheduled session 20261107T1835Z-T3-scheduled-format-normalization-j9x2 restored; stale state.json is not authoritative. T4 mouse, T5 controls/resolution, T1/T2 water untouched.

## Source change
scripts/t3_rgb_drift_strata.py now checks the authenticated 106/30 cohort BEFORE optional metadata gates. Previously 105 pairs / 29 drift with absent sRGB was reported as missing RGB-drift metadata rather than wrong baseline provenance. tests/test_t3_rgb_drift_strata.py adds two assertions: strict baseline reports provenance mismatch, exploratory strict_baseline=False reports metadata failure. This does not repair rendering or claim individual texture provenance.

## Verification and constraints
Fetched exact source/test and updated by blob SHA via GitHub connector; repository local git ls-remote failed DNS 'Could not resolve host: github.com', so exact published Python tests were NOT executed. No Actions dispatch, native Unity build, phone test, raw assets, .meta/GUID, .rgd, audio, Settings or touch edits. Existing Actions latest inspected: T4 mouse and T5 integration source-only jobs successful; no duplicate launch. Do not infer device restoration.

## Next
Run PYTHONPATH=scripts python -m unittest discover -s tests -p test_t3_rgb_drift_strata.py against published SHA; acquire private per-pair original/export metadata from SHA-verified ZIP2; trace white hand/raft and square smoke through actual Renderer/Material/Shader PPtr, keywords, alpha blend and particles, comparing CL images. No trial build vote change; RENDER-002 OPEN, NOT_READY.
