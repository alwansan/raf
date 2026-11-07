# T3 scope — 20261107T1929Z-T3-scheduled-drift-provenance-f8q4
origin: scheduled
track: RENDER-002
baseline_head: 71b440d93b74c7236beef75119d15f29881ad67c
experiment_key: T3-RGB30-BASELINE-VALIDATION-20261107-f8q4
shared_resource: none; no Unity/ZIP2/CI dispatch

## Read-only evidence
Owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md: world/save/re-entry accepted only on artifact 42058825739; white hand/raft, lighting and square smoke remain. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Source-only 106 texture pairs / 30 RGB drift; no per-pair authenticated sRGB data yet. Current T3 tests/test_t3_rgb_drift_strata.py has 14 source tests, and script currently checks optional metadata gates before validating the 106/30 baseline.

## Scope and hypothesis
Only scripts/t3_rgb_drift_strata.py and tests/test_t3_rgb_drift_strata.py plus unique session records. Move strict baseline provenance validation ahead of optional metadata gates, so a wrong 106/30 cohort is reported as provenance failure, not misleading missing-metadata diagnosis. Add regression for simultaneous wrong cohort + missing metadata. Preserve existing valid-pair output and safety guards. No game assets, .meta, GUID, .rgd, shaders, touch, Settings, audio, or other T worker files. No native CI. This is diagnostic correctness, not visual restoration.

## Coordination
T4 owns physical mouse, T5 owns three controls/Resolution, T1/T2 water. Avoid overlapping their files and CI. Recheck HEAD and blob SHA before source write; do not force. No proprietary game content in public records.
