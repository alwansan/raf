# T2 independent scheduled work
session_id: 20261105T2124Z-T2-scheduled-stackcap-6c2e
origin: scheduled
issue_id: WATER-001
baseline_sha: 79fc823532812d44f6e4d8c4881d9bba284ad043
resumed_from_session: 20261105T2017Z-T2-scheduled-retfix-7c3a.md; 20261105T2107Z-T2-chat-writer-call-ab1c.md
owner_device: docs/DEVICE_FEEDBACK_42058825739_AR.md (world save/reentry confirmed, water pass errors remain)
status: active
intended_files: scripts/t2_rt_return_cfg.py; tests/test_t2_rt_return_cfg.py; this work; new session file
experiment_key: t2-cfg-synthetic-unbounded-stack-growth-cap-v1
resource_key: none (CPU-only, no Unity/CI dispatch)
hypothesis: synthetic CIL loop that repeatedly pushes can inflate memory despite max_states; cap stack height and return unknown without misclassifying valid short methods.
validation: run existing unittest and a synthetic backedge growth case; source-only, not original DLL/ShaderLab/device evidence.
other_team: T1 FFT, T3 materials, T4 mouse, T5 UI/delivery; no overlapping files.
