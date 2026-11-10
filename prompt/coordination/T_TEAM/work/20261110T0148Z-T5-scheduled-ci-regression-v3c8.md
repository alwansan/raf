# 20261110T0148Z-T5-scheduled-ci-regression-v3c8
origin=scheduled
issue_id=INTEGRATION-001
base_sha=8b024174edc797653a3d607b2294069de234166c
status=completed
intended_files=prompt/coordination/T_TEAM/work/20261110T0148Z-T5-scheduled-ci-regression-v3c8.md; clients/T5/sessions/20261110T0148Z-T5-scheduled-ci-regression-v3c8.md
experiment_key=source-only-runtime-parity-42715257589-vs-42723946943
resource_key=none; Unity build NOT requested
hypothesis=The source manifest mismatch fixed by fb0bfea is covered by newer offline integration CI, avoiding another expensive Unity run.
Evidence: 42715257589 failed; 42723946943 completed success (2026-11-09 23:52 UTC); 42723947226 and 42723947160 success for T4 mouse/immersive source checks. This is CI evidence only, NOT staged Unity editor/device acceptance.
No game sources or shared workflows modified. Recheck six new tests from f088ec9 separately; not proven executed by this integration run.
Next: run six Python tests in isolated CI or local environment; then prioritize owner-requested right-side controls/Resolution and signed APK/OBB comparison with T4 coordination.
