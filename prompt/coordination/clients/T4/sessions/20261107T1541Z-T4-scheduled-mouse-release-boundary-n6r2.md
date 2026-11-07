# T4 scheduled mouse release-boundary checkpoint

- session_id: 20261107T1541Z-T4-scheduled-mouse-release-boundary-n6r2
- origin: scheduled
- base_sha: c666daea3b33ceb421c317e44f7f080a90d43a52
- resumed_from_session: 20261107T1440Z-T4-scheduled-mouse-trace-classifier-p8q3.md
- scope: INPUT-005; no touch/layout/Resolution or Unity build.
- owner evidence: DEVICE_FEEDBACK_42058825739_AR.md confirms actual device world entry, save, exit, re-entry on run 42058825739 at e9c358eda01785b65e4eb14f18723da426635628; no mouse success claim.
- identified reproducible logic flaw in the existing classifier: a relative event occurring only after physical_mouse_capture_released could be counted as RELATIVE_AFTER_REARM_OBSERVED. This is an invalid inference of captured relative movement.
- code commit: 997e15de9de5f24a95165c275432c56958aa15d3. A request's first subsequent release bounds the interval of valid relative events. New observational classification RELEASED_BEFORE_RELATIVE_OBSERVED avoids a false-positive.
- test commit: 2135d8618d3ec13742a77a6b150eecef29d1617e. Added three unit cases: movement after release, movement before release, release without movement; total 9 cases. CI results not yet verified; do not claim test pass.
- Work record: prompt/coordination/work/INPUT-005/20261107T1541Z-T4-scheduled-mouse-release-boundary-n6r2.json, scope commit 6c560926c352dfde75658e76d309b66b31f7c7b6.
- Boundaries: no device run, no APK extraction, no new Unity request, no .rgd or keyboard changes; INPUT-005 remains OPEN. Source CI success 42373576554 predates this change and is not validation of it.
- Next: run python3 -m unittest tests/test_t4_classify_mouse_capture_log.py; check Actions on commit 2135d861; analyze a newer complete physical mouse device log and preserve ordering/epoch. Confirm keyboard and Raft cursor transitions on actual signed device build.
