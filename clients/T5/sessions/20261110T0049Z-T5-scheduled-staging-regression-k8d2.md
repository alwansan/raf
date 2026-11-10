# T5 scheduled session 20261110T0049Z-T5-scheduled-staging-regression-k8d2
origin=scheduled
start_baseline=a293d0d8ee93fc34e99fcac22effd9b398def540
scope=clients/T5/work/20261110T0049Z-T5-scheduled-staging-regression-k8d2.md
source_change=f088ec9e7dbb8ed5037cdcb6b76d6d74f7409a5d
scope_commit=787586cc63610e0d8ba6831f45aa2d028f49d20f
Evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; phone world/save/re-entry confirmed for 42058825739 only. 42696228231 failed before Unity Editor in final staging audit. Existing source verifier rejects mismatched bytes and symlinks; the new tests exercise six distinct source-only outcomes without game assets.
Implementation: tests/test_t5_runtime_staging_bytes.py (six unittest cases). No existing game files, workflows, Unity, pointer or Settings source changed. No duplicate CI/build requested. Tests have not been executed in this session; source-only static review, awaiting Python CI/local run.
Next: run `python -m unittest discover -s tests -p 'test_t5_runtime_staging_bytes.py' -v`, inspect failures, then re-check current HEAD/CI before further Unity. Separately prioritize Resolution/right-side buttons and actual signed APK/OBB/LogRaft comparison after coordination. Preserve current audio/Settings and defer general touch layout.
Read-only CL source: https://github.com/alwansan/CL/tree/520c4cf409aa20a4db54ff80ed87d8807d9cba57/raft%20log
Readiness=NOT_READY; no phone performance or GPU measurement performed here.
