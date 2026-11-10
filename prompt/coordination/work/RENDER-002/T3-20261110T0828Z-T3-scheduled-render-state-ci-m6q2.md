# T3 scoped work — 20261110T0828Z-T3-scheduled-render-state-ci-m6q2
origin=scheduled
baseline_sha=710de00e7a560c7694e41d5fedc7a2d31bcc514d
experiment_key=T3-RENDER-STATE-REGRESSION-20261110
scope: .github/workflows/raft-t3-render-state-pair-regression.yml; tests/test_t3_render_state_pair_diff.py (read only); scripts/t3_render_state_pair_diff.py (read only); unique session markdown.
Hypothesis: recent JSON integrity and known-mismatch fixes have no full repository CI execution evidence; execute 12 existing source tests in isolated lightweight workflow rather than altering game assets.
Shared resources: GitHub Actions ubuntu runner only; no Unity, APK, ZIP2, CL writes. No existing equivalent workflow found at targeted name; check before launch.
Constraints: fail-closed source tests only; no phone/GPU/alpha authenticity claim. T4 mouse, T5 resolution, T1/T2 water untouched.
