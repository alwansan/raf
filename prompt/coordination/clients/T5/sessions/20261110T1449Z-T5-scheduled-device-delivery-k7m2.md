# T5 scheduled investigation — 20261110T1449Z-T5-scheduled-device-delivery-k7m2
origin: scheduled
branch: feature/android-native-port (only writable)
UTC: 2026-11-10T14:49Z

## Source and scope
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md and T_TEAM CHAT_AND_SCHEDULE/PROMPT/OPERATING_MODEL. Separate T5 scope: delivery artifact provenance, APK/OBB pairing, HUD performance interpretation; T4 owns physical mouse capture/buttons. Do not touch T4 input source or shared Unity jobs. This file is the isolated session/work record; no shared state overwrite.

## Immutable phone evidence
Owner installed an artifact from run 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628), entered world, saved, exited, and re-entered. Publication failed separately. Source report identifies artifact 13441227298 and signed output 13441766832. CL immutable snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57, logs lf/LogRaft-20261105-220101-932, 220911-559, 230108-327. This is phone evidence for that build, not current HEAD.

## Performance analysis and limits
220911-559 summary: 57 displayed-frame samples, mean estimated 22.29 FPS, minimum 3.02 FPS; 23,884 water invalid passes, 3,850 FFT kernel errors, 1 OBB GUID warning, 1,333 RGBA32 cursor warnings. 230108-327: 39,132 invalid passes, 6,026 kernel errors, 2 OBB GUID warnings, only two valid frame samples. HUD screenshot 23:09:19 reports 18.27 FPS and frame p95 82.82 ms. Do not combine HUD p95 with 57-sample FPS average, or call either GPU time. GPU% unavailable unless LogRaft explicitly measures it. Counts are not per-second rates without exact trace durations. No fresh Android performance measurement in this cycle.

## Delivery boundary and next experiment
Prior T5 investigation identified successful artifact download and Release creation HTTP 403 Resource not accessible by integration. Do not infer APK/OBB corruption from publishing failure. Validate extracted signed APK AndroidManifest package/versionCode, OBB basename main.<versionCode>.<package>.obb, byte size, SHA256 for both, ZIP compression methods, signed manifest/delivery.json, OBB GUID warning owner path; use immutable run_attempt and source SHA. Do not claim SHA match before obtaining bytes. Verify installation and asset opening on phone separately.

## UI and interaction next step
Owner requires moving Show Xbox, Xbox layout, Test report to right-side safe region and improving existing Settings Resolution, no second menu. Screen physical pixels, window bounds, render scale, refresh rate and FPS are distinct. Landscape/aspect and saved preference must persist through Settings return. T4 independently handles real captured left/right/middle/wheel and system cursor; avoid touching those files. New 8 Nov owner note says captured clicks/wheel still fail, camera capture works; this supersedes 5 Nov priority where applicable. Source inspection and device acceptance pending.

## Outcome
Documented bounded comparison and non-overlap; no Unity build, no APK, no device test, no resource modifications. Next: obtain signed artifact bytes or delivery.json; run deterministic pair validator and pin LogRaft sessions to matching package SHA. Then source-level UI fix only after checking live T5/T4 file ownership and exact HEAD. Full game NOT_READY 0/3.
