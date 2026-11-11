# T2 — 20261111T0224Z-scheduled-publish-atomic-p7m4
origin: scheduled
resumed_from_sessions: 20261111T0120Z-T2-scheduled-foam-numeric-ci-f8q2; 20261110T2315Z-T2-scheduled-producer-contract-k7m2
base_sha: da188e77dc04495dc158dc1ae0e8080a990f97e5
scope_commit: 3c1ac753986c40b49186b6f80ec71ca9401f8c88
issue: WATER-001 OPEN; NOT_READY 0/3

Read owner device feedback 42058825739: actual world/save/re-entry succeeds; water/FFT errors remain. Previous original Foam 6 resource pairs and original RT return-local provenance are source-only. CI 42930033780, 42930033819 and 42930033811 previously succeeded on ea6b818; do not repeat.

Engineering: new opt-in publication adapter reads at most 65537 bytes, invokes the strict aggregate parser, then writes only canonical allowlisted JSON via fsync + same-directory atomic os.replace. It rejects invalid UTF-8, raw paths, malformed JSON and symlink destinations without emitting private data to stdout. Subprocess regression tests cover success, rejection, no partial file, preservation of prior report, symlink output, and private-field rejection. Existing workflow producer_integration=UNKNOWN remains accurate; this adapter is NOT wired into any legacy producer or GitHub upload step. CI status pending until workflow integration; no Unity/phone evidence. No shader, meta, GUID, save or game file modified.

Next: verify test results on immutable SHA, integrate adapter into actual Foam report production/upload boundary with an explicit fail-closed test; separately prove original RenderTexture crosspass identity and CB0 before ShaderLab. Coordinate T3 effects and T4/T5 input/resolution; do not touch their files.

Checkpoint: CI workflow path filters and test step integrated in 5dd745975089b10bc02c18cb51636506c054b063; run not yet visible (waiting_ci). Local py_compile performed for initial equivalent draft; committed version must be verified in CI. New tests are not claimed passing. Original water still OPEN.
