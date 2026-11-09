# T5 work — 20261109T1154Z-T5-scheduled-ci-confirm-6f2c
origin=scheduled
baseline_sha=71dcd321b1a4db9d2b006f2795390f195ae4c840
scope=CI verification of existing PNG byte regression fix, no shared Unity resource.
files=clients/T5/sessions/20261109T1154Z-T5-scheduled-ci-confirm-6f2c.md; prompt/coordination/T_TEAM/work/20261109T1154Z-T5-scheduled-ci-confirm-6f2c.md
hypothesis=90d3d08 repairs failing synthetic Adam7 fixture from run 42597471313.
experiment_key=T5-PNG-CI-90d3d08
Evidence: run 42604230659 completed success on exact SHA 90d3d08959e9ddb9f07829c3771a94e55977c9e1; earlier run 42597471313 failed on 9d5d26baef64cc1eb8efed4f0ed51e4d41cc787a.
No new build requested, no overlapping T4 mouse files touched. This verifies source-only regression, NOT real CL images/device pixels.
Next: shift from PNG tool changes to right-side buttons, Resolution and APK/OBB manifest/provenance after current T-team scope review.