# T1 WATER-001 scope — 2026-11-11T02:17Z
session_id: 20261111T0217Z-T1-scheduled-kernel6-false-positive-4c9a
origin: scheduled
baseline_sha: 983ace0c53611b994ad5d114e082c4495223e56d
scope: scripts/t1_kernel6_log_context.py, scripts/test_t1_kernel6_false_positive_4c9a.py; own session/work only.
hypothesis: the current KERNEL6 regex treats `kernel 6.0` and `kernel 6_extra` as index 6 because `\b` accepts punctuation/underscore boundaries differently; verify and reject ambiguous suffixed tokens without hiding canonical kernel #6 and index (6).
experiment_key: T1-KERNEL6-LEXICAL-4C9A
shared_resource: none; no CI or GPU run.
taken_over_from: prior T1 kernel6 context and marker boundary work; no T4/T5 files.
owner baseline: 42058825739 device save/re-entry succeeds; water remains open; later mini-lab feedback is newer.
