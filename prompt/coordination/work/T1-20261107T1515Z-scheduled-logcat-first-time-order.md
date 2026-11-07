# T1 scope — 20261107T1515Z-T1-scheduled-order-6f2c
origin: scheduled
baseline_sha: 786abc86ec337acf4d98bc8b4ee92f7ab9d17d39
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md (phone world/save/reopen; packaging failure)
taken_over_from: prompt/coordination/clients/T1/sessions/20261107T1415Z-T1-scheduled-logroot-k6a2.md
scope: scripts/t1_water_logcat_first_roots.py and tests/test_t1_water_logcat_first_roots.py; new T1 session only.
hypothesis: segmented Logcat files may be supplied out of chronological order, so first_by_category currently returns first *encountered*, not earliest timestamp; missing timestamps may mask later valid timestamps.
experiment_key: T1-logcat-earliest-order-6f2c
shared_resource: none; CPU-only Python; no Unity/CI.
coordination: T4 physical mouse, T5 Resolution/buttons and T2 shader sources untouched. No raw CL assets or logs published.
plan: add regression with reversed segment order and unstamped first hit, then choose minimum parsed month-day timestamp. Document year-rollover limitation; do not infer true wall-clock chronology across years.
