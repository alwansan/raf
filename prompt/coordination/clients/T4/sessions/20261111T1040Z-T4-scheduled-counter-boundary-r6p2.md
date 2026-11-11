# T4 scheduled session — 20261111T1040Z-T4-scheduled-counter-boundary-r6p2
origin=scheduled
issue=INPUT-005
baseline_sha=aaf29d6a528e25f313797a24a0a9c0f97b543a80

## Restored facts
Owner's 5 November phone test of artifact 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628) confirmed entering, saving, exiting and reopening local world. Do not regress .rgd or treat old APK86 world failure as current. Mouse camera movement improved, but LEFT/RIGHT/MIDDLE and scroll remain unconfirmed on device. Latest previous T4 scheduled session: 20261111T0944Z-T4-scheduled-route-a6k9.md.

## Scope and execution
Work: prompt/coordination/clients/T4/work/INPUT-005/20261111T1040Z-T4-scheduled-counter-boundary-r6p2.md
- baseline HEAD aaf29d6a528e25f313797a24a0a9c0f97b543a80
- scope commit 508911a8d7186b3bf6dcfc63abdf48628ce92e8c
- source fix commit 1a9ac0ac53a9314f8ca81c7adb0c25c703e8f742
- regression tests commit af10e2c320b12ab50fa1b065fcbdd1f3e853ec5a

Hardened scripts/t4_capture_reader_summary.py: exact token marker boundary; split adjacent callback/reader reports; retain last cumulative snapshot and additionally expose per-counter maximum and observed decreases. This avoids falsely attributing unrelated counters and avoids losing peaks after a counter reset. Tests in tests/test_t4_capture_reader_summary_boundary.py cover false marker substring, reset, adjacent markers, and no-gameplay-proof. No game runtime code changed.

## Verification and limitations
GitHub commits confirmed through connector. Unit tests added but not yet executed by CI in this session; do not claim pass. No Android device run or full Unity build. Counter decreases can reflect reset/restart or instrumentation and are NOT proof of process restart. Source log marker absence is not proof that physical events never arrived.

## Next
Execute regression tests in cheap CI or local source checkout; inspect same-build same-PID device log for callback vs reader markers; prioritize fixing actual physical button and wheel delivery in Unity with keyboard preserved. T5 owns Resolution. Do not duplicate existing Unity runs. Keep INPUT-005 open until phone proof.
