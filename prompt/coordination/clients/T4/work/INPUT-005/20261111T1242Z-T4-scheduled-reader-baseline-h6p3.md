# T4 INPUT-005 — same-process baseline diagnostic

session_id: 20261111T1242Z-T4-scheduled-reader-baseline-h6p3
origin: scheduled
issue_id: INPUT-005
base_sha: a07a9cde89c75994b137ef4e999c082ead427c9c
status: active
intended_files: scripts/t4_capture_reader_summary.py; tests/test_t4_capture_reader_summary_boundary.py; prompt/coordination/clients/T4/sessions/20261111T1242Z-T4-scheduled-reader-baseline-h6p3.md
experiment_key: t4-reader-baseline-v1-a07a9cde-single-process-cumulative
resource_key: none (source-only, no Unity)

Hypothesis: current diagnostic stores only final and maximum cumulative counts, so a reader counter that was already nonzero before the first captured action can be incorrectly interpreted as evidence of consuming that action. Record first observed values and per-counter monotonic increases only; never claim gameplay proof. This is complementary to T5 display/build and T4 physical-input runtime investigations. Preserve world/.rgd, keyboard, audio and Settings. No native build.

Owner baseline: artifact 42058825739 entered world, saved, exited, and reopened; release packaging failed. Mouse click/scroll still unproven.
