# T1 WATER-001 — timestamp type integrity

session_id: 20261111T2007Z-T1-scheduled-chronology-timestamps-c83f
origin: scheduled
baseline_sha: 9ab95c3a0ac7a2d1c8ebf972fc35ed6b15afa9d2
scope: scripts/t1_water_startup_order.py and isolated regression tests only
hypothesis: `int(first_observed_unix_ms)` silently truncates floats, accepts bool and numeric strings; ordering and 2ms separation may be fabricated from malformed CL summary data.
experiment_key: T1-CL-CHRONOLOGY-TIMESTAMP-TYPES-20261111
shared_resource: none; no Unity, APK or Actions requested.
evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57; prior T1 Actions 43084365164 success.
coordination: T4 physical mouse and T5 resolution/three controls remain separate. Do not modify those files. Avoid shared status edits unless required.
plan: reject malformed/non-integer/non-positive timestamps and add bounded tests. No claim of new GPU evidence.
