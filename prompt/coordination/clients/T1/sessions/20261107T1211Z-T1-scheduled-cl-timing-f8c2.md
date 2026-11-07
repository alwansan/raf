# T1 session — 20261107T1211Z-T1-scheduled-cl-timing-f8c2
origin: scheduled
baseline_sha: 8a0236b31a502bb8d28e7519b38679b165d065ec
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; world enter/save/exit/reopen confirmed by owner on run 42058825739 artifact, publishing failed.
resumed_from: prompt/coordination/clients/T1/sessions/20261107T1005Z-T1-scheduled-first-mismatch-b4e9.md; earlier T1 chat and scheduled records retained.
work: prompt/coordination/work/WATER-001/20261107T1211Z-T1-scheduled-cl-timing-f8c2.md
result: analyzed pinned CL 220911-559 and 230108-327 session-summary JSON. Both water pass and FFT kernel errors first appear 2ms apart. Final counts and sample undercounts recorded in docs/T1_WATER_FFT_CL_TIMING_2026-11-07.md.
checks: branch baseline 8a0236b31a502bb8d28e7519b38679b165d065ec; current comparator blob 96f8e148223b78a591bad163b78f4f75514e9f75; existing test suite source reviewed; no duplicate CI or build requested. T4 owns physical mouse; T5 owns three buttons and Resolution. No touching shared files.
limitations: summaries only, no raw first-message extraction, no verified original kernel binding, no Vulkan/Unity paired numeric trace, no Unity/GPU/device test, no new APK. WATER-001 OPEN; readiness NOT_READY 0/3.
next: isolate first unique error strings from pinned raw CL logs and tie to kernel/material names and actual Unity FindKernel/Dispatch; do not interpret aggregate category counts as GPU execution counts.
