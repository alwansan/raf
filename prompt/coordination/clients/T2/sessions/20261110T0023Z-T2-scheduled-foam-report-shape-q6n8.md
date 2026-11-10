# T2 — 20261110T0023Z-T2-scheduled-foam-report-shape-q6n8

- origin: scheduled; date_utc: 2026-11-10T00:23Z; branch: feature/android-native-port.
- resumed_from_sessions: 20261109T2323Z-T2-scheduled-writer-rhs-scope-m7q2; 20261109T2040Z-T2-chat-foam-writer-census-z4m7.
- owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 owner entered/saved/reentered world from artifact, packaging publication failed; this supersedes APK86. CL snapshot 520c4cf4 reports 23,884 water-pass/3,850 FFT errors in 220911 and 39,132/6,026 in 230108. No new phone run in this session.
- scope plan commit: 8d8c12fcd2364fc4dcb135cc947ecdde29d8aca2.
- source fix: 86a19cab5e53c3cde067b535d5bb0b5db06679b2; malformed private Foam report rows now rejected with ValueError before private-field dereference. Explicit shape, type and boolean checks; no original names in errors. Regression: df11e0e3fc36c7d053756e34d820b8e1519be88a; two new test methods with malformed row and reflection inputs.
- evidence boundary: source-only code change; no verified Python test execution, no CI dispatch, no Unity/ShaderLab/FFT original integration, no device pixels. DNS from container to github.com unavailable; connector GitHub writes succeeded. WATER-001 OPEN, NOT_READY 0/3.
- next: verify test suite on immutable SHA, then implement original Mono.Cecil writer RHS/receiver classification under separate scoped work; T3 owns fire/smoke effects, T4 physical mouse, T5 Resolution/packaging. Preserve audio, Settings, .meta/GUID/.rgd.
