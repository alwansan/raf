# T3 RENDER-002 independent scope — 2026-11-09T17:28Z
session_id: 20261109T1728Z-T3-scheduled-smoke-v2-ci-result-r5n2
origin: scheduled
issue_id: RENDER-002
base_sha: ac3a78b2986536820d4eac88877f14588a70f33c
status: completed
intended_files: [this unique work record, unique T3 session record]
experiment_key: smoke-v2-metadata-regression-c652bc377eebb56bcdc3b453bd5bbe2abadd3178
resource_key: none (read-only Actions verification)
updated_at: 2026-11-09T17:28:00Z

Hypothesis: previously waiting CI for the 14 synthetic metadata controls has completed; distinguish passing metadata regression from authentic original smoke shader recovery.
Evidence: https://github.com/alwansan/raf/actions/runs/42656207137 completed success on c652bc377eebb56bcdc3b453bd5bbe2abadd3178. No current running or queued runs in most recent 12 Actions; latest T2 42664209077 failure, earlier 42664186862 success. No need to dispatch duplicate.
Conclusion: source-only gate CI is GREEN, not device or original-shader proof. Do not alter material/shader assets without original Shader48 pass state and actual export parity. Next experiment requires SHA-pinned ZIP2 original, same-instance export, metadata-only output; distinguish blend/alpha state, program presence, texture alpha, and phone pixels. No Unity/APK requested.
