# 20261108T0445Z-T5-scheduled-fps-package-7b2e
origin: scheduled
baseline_sha: be2a7065144e9300a8932dba278838636ba27789
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md
scope: scripts/t5_lograft_presented_fps.py and tests/test_t5_lograft_presented_fps.py only
hypothesis: a native lograf_shell row with another Android package may be accepted if SurfaceFlinger quality fields are plausible; package identity must be checked before attributing FPS to Raft.
experiment_key: t5-lograft-package-identity-20261108
shared_resource: none; source-only Python; no Unity/native CI dispatch.
coordination: T4 owns physical mouse; no edits to T4 files. Three right buttons and Resolution remain separate existing T5 scopes.
acceptance: reject explicitly mismatched native package, preserve legacy synthetic flat-row behavior and valid Raft native rows; add regression.
