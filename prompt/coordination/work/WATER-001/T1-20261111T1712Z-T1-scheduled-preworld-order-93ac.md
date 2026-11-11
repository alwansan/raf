# T1 WATER-001 independent scope — 20261111T1712Z-T1-scheduled-preworld-order-93ac
origin: scheduled
baseline_sha: ec333be58af2bd83d986dd415b422e23dae8ba8f
status: IN_PROGRESS
experiment_key: t1-cl-pinned-first-error-before-world-order-v1
resource: CL immutable 520c4cf409aa20a4db54ff80ed87d8807d9cba57 (read-only)
files: unique T1 session, unique experiment, scripts/t1_water_startup_order.py, tests/test_t1_water_startup_order.py
hypothesis: both owner phone sessions show first water and FFT error *before* the world-loaded milestone, which distinguishes startup-time failure from a solely post-world failure without proving cause.
overlap: no edits to T2 shaders, T4 mouse, T5 UI/Resolution, shared index, game assets, or Unity workflows.
source: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned session-summary.json for 220911-559 and 230108-327.
test: verify first-observed timestamps and full category/material partitions; five isolated synthetic regressions; never infer kernel6 Unity identity from integer.
build: none; no CI duplication; WATER-001 remains OPEN/NOT_READY 0/3.
