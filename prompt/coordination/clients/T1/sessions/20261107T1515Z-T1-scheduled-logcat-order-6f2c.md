# T1 — 20261107T1515Z-T1-scheduled-logcat-order-6f2c
origin: scheduled
baseline_sha: 786abc86ec337acf4d98bc8b4ee92f7ab9d17d39
head_after: 5cca885240f75b26b03cc349b559841bd60ef466
resumed_from: 20261107T1415Z-T1-scheduled-logroot-k6a2
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; original phone world/save/reopen successful from artifact; package publication failed.
scope: prompt/coordination/work/T1-20261107T1515Z-scheduled-logcat-first-time-order.md
result: fixed heuristic first_by_category to select lexicographically earliest MM-DD HH:MM:SS.mmm timestamp among matching log lines, regardless of segment order. Missing timestamp no longer masks later timestamp. Added synthetic regression with reversed segment order and unstamped initial line.
commits: scope f0acbbea4b950ed4c74eaeb48c05b562e0cb8966; code f28c4e9b631689023bf0ea03b3caf1b177ca2709; regression 5cca885240f75b26b03cc349b559841bd60ef466.
validation: source reviewed and HEAD rechecked; test added but NOT executed (container DNS failure resolving raw.githubusercontent.com). CI in_progress count 0 at read. No Unity build launched. Synthetic expected counts not proof of raw CL compatibility.
limitations: month-day timestamp ordering is only meaningful within same calendar year, and timestamp ties do not establish causal ordering. Classifier not yet calibrated to CL raw logs. No FindKernel/Dispatch or original FFT numeric proof; WATER-001 OPEN; NOT_READY 0/3.
next: execute python3 -m unittest tests.test_t1_water_logcat_first_roots (or discovery equivalent) in checkout; then run on pinned CL raw segments privately, compare roots/counts to session summaries, trace Unity kernel index 6 to ComputeShader.FindKernel/Dispatch with real import and authentic paired Vulkan/Unity captures. Keep T4 mouse and T5 Resolution/buttons untouched.
