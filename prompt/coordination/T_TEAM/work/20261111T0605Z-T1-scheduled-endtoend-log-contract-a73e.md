# T1 WATER-001 independent scope
session_id: 20261111T0605Z-T1-scheduled-endtoend-log-contract-a73e
origin: scheduled
baseline_sha: acaa8cb0fb661ee69be5ee1273aa970f3b8b465b
branch: feature/android-native-port
experiment_key: T1-KERNEL6-E2E-SYNTH-20261111
files: scripts/test_t1_kernel6_pipeline_endtoend.py; this work record; own session record
hypothesis: scanner JSON --errors-only and cross-session comparator need an end-to-end test on independent physical-line logs, including privacy and noncausality; isolated synthetic fixture can detect integration regressions without proprietary CL data.
shared_resource: none; no CI, Unity, native build or testpack. T4/T5 mouse/Resolution/right-controls untouched.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL fixed 520c4cf409aa20a4db54ff80ed87d8807d9cba57. World/save/re-entry success from artifact; water and FFT remain open. 2026-11-08 unified mini lab policy takes precedence.
taken_over_from: prior T1 kernel context and comparator scripts; no B worker reactivation.
acceptance: Python unittest synthetic two logs; counts/deltas; no raw message strings in serialized result; index 16 and 6.1 excluded; physical-line context bounded; original identity unproven.
status: scoped; tests not yet executed in repository (local Git DNS unavailable).
