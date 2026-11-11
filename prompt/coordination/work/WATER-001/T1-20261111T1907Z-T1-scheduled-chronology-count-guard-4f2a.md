# T1 WATER-001 independent count-integrity gate
session_id: 20261111T1907Z-T1-scheduled-chronology-count-guard-4f2a
origin: scheduled
issue_id: WATER-001
base_sha: c3dae350e80e377faaa4c626cf27609326c05149
scope_commit: 236dfa0ce20d69ab02bd3e1c03b307bc2723f195
fix_commit: 8af78a8fb9b4ba9e480eee06b6872c53f19938cc
status: completed_source_ci
intended_files: scripts/t1_water_startup_order.py; tests/test_t1_water_startup_order.py; this work file; separate T1 session
experiment_key: chronology-count-nonnegative-integral-gate|pinned-CL-61f71ceb|python3.12|synthetic-malformed-counts
resource_key: none; source-only GitHub Actions, no Unity or APK
hypothesis: negative balanced material/kernel partitions, bool and fractional counts can be accepted as legitimate CL event counts.
change: strict nonnegative integral counts, reject zero first-observed category, five adversarial tests. No original game/shader changes.
prior_ci: https://github.com/alwansan/raf/actions/runs/43074969754 completed SUCCESS; verified live.
new_ci: https://github.com/alwansan/raf/actions/runs/43084365164 completed SUCCESS at 2026-11-11T19:08:43Z; no duplicate dispatch.
local_test: unavailable due to container DNS raw.githubusercontent.com resolution failure; CI success.
owner_baseline: 42058825739 world enter/save/reenter confirmed; package publication failure independent. Later CL 8 Nov is separate pinned sample.
next: integrity gate passed in CI; then prioritize original FFT .compute GUID/FindKernel/Dispatch mapping and Vulkan-vs-Unity first divergence. Preserve T4 mouse and T5 Resolution scope.
