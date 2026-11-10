# T3 RENDER-002 — comparator CI resolution
session_id: 20261110T0932Z-T3-scheduled-render-state-ci-verified-v6n3
origin: scheduled
baseline_sha: 0ba8582d8e38ae4f2d3db1190aeda41b2bc1818d
experiment_key: T3-render-state-regression-42782959918
scope: evidence-only CI closure; no game resources, shader, shared workflow, T4 mouse, T5 resolution edits.
files: this independent work record and matching independent T3 session.
resource: none; reuse existing Actions run, no new CI.
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; original phone world/save success remains scoped to run 42058825739.
result: GitHub Actions 42782959918 completed success at 2026-11-10 08:28 UTC, head 652a03ec62ef5ac39d126536d7f8582708ea8c7c. This closes waiting_ci for comparator source regression only.
limits: comparator input is manually supplied authenticated summary; no actual source/export pair, DXBC provenance, particle Blend/Alpha mismatch, Unity compile, pixels or device fix proved. RENDER-002 OPEN NOT_READY 0/3.
next: extract a same-material original/export render-state pair with provenance and hashes; compare blend/alpha/zwrite/ztest/queue, then relate mismatch to CL smoke square and white surfaces. Do not rerun synthetic-only CI without code change.
