# T3 scope 20261107T1126Z-T3-scheduled-drift-coverage-k4p8
origin=scheduled; baseline_head=9e74072faf383c6ca395ad759e9efae4dfeb0925

Track RENDER-002. Prior evidence: CI41968665857 30 RGB-drift/76 exact among 106; aggregated artifact lacks per-pair metadata. Previous T3 classifier commit integrated; previous T3 chat Shader48 work is separate. Device report docs/DEVICE_FEEDBACK_42058825739_AR.md read; real phone world save/reentry does not prove graphics.

Hypothesis: --require-metadata currently accepts 106 known values for exact group and zero for 30 drifting pairs; stratification then appears metadata-complete although causal group is UNKNOWN. Improve fail-closed per-class coverage and tests, without game resources or external assets.

Owned files: scripts/t3_rgb_drift_strata.py, tests/test_t3_rgb_drift_strata.py, this work file, independent session. Experiment key T3-rgb-drift-group-coverage-20261107. No shared CI/GPU resource; no Unity build. T4 mouse and T5 UI/Resolution untouched. Recheck HEAD before each write, preserve other agents' edits.
