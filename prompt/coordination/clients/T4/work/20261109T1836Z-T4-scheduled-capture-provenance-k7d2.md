# T4 INPUT-005 — capture provenance scope
session_id: 20261109T1836Z-T4-scheduled-capture-provenance-k7d2
origin: scheduled
baseline_HEAD: 55b2475e7cef2a59321ba30d8f11b6b2f7cad16f
experiment_key: INPUT-005-captured-vs-legacy-consumer
Files: this work record and a separate T4 session only; no game/Unity/T5-owned file edits.
Hypothesis: source-only acceptance gate success cannot establish Unity consumption; captured callback and original legacy consumer evidence must be paired from the same signed game build.
Shared resources: none; no CI or APK launch. Prior successful runtime gate CI 42657857161 is not repeated.
Owner phone invariant: Artifact 42058825739 world creation/save/reopen PASS, limited to that artifact. The later 8 November mouse observation is camera capture functioning, buttons and wheel not functioning in Raft.
Next engineering step: obtain matching captured Android event and frame-latched legacy consumer trace on a single immutable signed candidate; compare source epoch, focus-loss reset and mouse keyboard continuity. Do not infer phone success from mini APK or source-only tests.
