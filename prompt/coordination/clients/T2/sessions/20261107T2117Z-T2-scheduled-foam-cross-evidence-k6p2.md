# T2 scheduled — Foam independent evidence reconciliation
session_id: 20261107T2117Z-T2-scheduled-foam-cross-evidence-k6p2
origin: scheduled
status: source_integrated_tests_unverified
baseline_sha: 3b32b338c0783a1def74151b60cc36cb59e1f1dc
scope: prompt/coordination/work/WATER-001/20261107T2117Z-T2-scheduled-foam-cross-evidence-k6p2.md

Read owner 5 Nov device feedback first: run 42058825739 owner entered/saved/reentered world from artifact, packaging Release failed; CL 220911 had 23884 water-pass and 3850 FFT errors, CL 230108 had 39132 and 6026. These are source-specific, not current HEAD GPU proof. Read AGENTS.md, CURRENT_OWNER_REQUIREMENTS, STATUS, T_TEAM chat/schedule, prompt, operating model and trial votes; prior T2 role gate, aggregate and 81 matrix.

Implemented scripts/t2_foam_pass_crosscheck.py and tests/test_t2_foam_pass_crosscheck.py on feature/android-native-port. Existing independent safe report validators run first (including original source schema); per-pass identities must match exactly, else fail closed. CLI parses both reports rejecting duplicate keys and nonfinite JSON. Result exposes only pass0/pass1 classifications and classification_only, no private IL or asset data. 81-way and 4 role/pass negative fixtures plus original-validator enforcement committed.

Commits: scope 60fe3345b94fb33bf4af24ff6ef3699d5d9b73ad; code ffae74c64ab3e0631d4020d5c2317b458a7018c9; tests 9f592fe6ff253a58a7ae41c7fdc17ac4f62dc76f. Latest HEAD after tests: 9f592fe6ff253a58a7ae41c7fdc17ac4f62dc76f. Tests were NOT executed against original checkout: local git DNS failed and no CI requested. Source inspection only. This gate is independent from original Mono.Cecil producer and cannot establish actual pass1 origin, CB0, ShaderLab, rendered water or Android GPU. No Unity, game shader, T3 files, trial vote, native request or Actions changed.

Next: execute python -m unittest tests.test_t2_foam_pass_crosscheck on immutable checkout; feed two genuine source-original sanitized reports with independently verified SHA and investigate any disagreement. Continue original pass1 producer IL, Spectrum/Blur CB and ShaderLab integration with T1/T3. WATER-001 OPEN; no APK requested.
