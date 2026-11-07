# T3 scheduled session — 20261107T1835Z-T3-scheduled-format-normalization-j9x2
origin: scheduled
track: RENDER-002
status: SOURCE_PATCHED_TEST_PENDING; NOT_READY
scope: prompt/coordination/work/RENDER-002/T3-20261107T1835Z-T3-scheduled-format-normalization-j9x2.md
scope_commit: 41f42186f32cb853364858b07b8e22bb65ddbacd
source_commit: ec7a6474122a3b82e63e753e190f66fd24f07244
test_commit: b0ab1e3b9a107bedbe9ccec3bb007a4a06e5673c

## Owner/device baseline
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Artifact 42058825739 on device entered/saved/re-entered world, but white hand/raft, lighting, square smoke remain open. Source SHA e9c358eda01785b65e4eb14f18723da426635628. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 contains photo references; not reinterpreted as new GPU evidence. Log summaries: 23884 water pass errors/3850 FFT in 220911; 39132/6026 in 230108. T4 mouse and T5 controls/resolution not touched.

## Distinct source improvement
Previous T3 source gate correctly treats literal UNKNOWN (any case) as absent format, but a padded string such as " UNKNOWN " bypassed normalization and could inflate metadata coverage for one RGB-drift pair. Source now strips format whitespace before format allowlist and UNKNOWN canonicalization. Regression adds padded upper/lower/mixed sentinel cases and asserts coverage 29/30 plus strict gate rejection. No raw texture data or game paths published. Preserves prior category behavior except trimming.

## Evidence limits
Read latest source and test via GitHub connector and updated both using blob SHA. Local git ls-remote failed DNS (Could not resolve host: github.com); therefore exact published test suite was NOT run in this cycle. No CI dispatch, Unity, APK or phone test. No game assets, GUID, .rgd, audio, Settings, touch changed. No claim this fixes white hand/raft/smoke.

## Next
Run python -m unittest discover -s tests -p test_t3_rgb_drift_strata.py with scripts on PYTHONPATH against published commit, then acquire private per-pair manifest from pinned ZIP2/exporter (not public aggregate) with format/source_srgb/importer_srgb; trace affected Material Shader PPtr and ParticleRenderer blend/alpha to CL photos. Check live T1/T2/T4/T5 overlap and Actions before any native experiment. T3 trial vote remains لا يحتاج because no device-visible shader/material repair.
