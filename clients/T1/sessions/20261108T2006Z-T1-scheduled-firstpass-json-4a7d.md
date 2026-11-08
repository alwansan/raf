# T1 WATER-001 scheduled session
session_id: 20261108T2006Z-T1-scheduled-firstpass-json-4a7d
origin: scheduled
baseline_sha: 20766ed850c16bc18bfab37ed5c6913c64c9d3f0
last_checked_head: 09eada01575a640d1e0cabf6bdaa23e3d82e90f7
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, source e9c358eda01785b65e4eb14f18723da426635628; world save/re-entry proven from Artifact, publication failed. CL sessions 220911-559: 23884 water/3850 FFT; 230108-327: 39132 water/6026 FFT. Distinct sessions, no normalized regression claim.
work: clients/T1/work/20261108T2006Z-T1-scheduled-firstpass-json-4a7d.md
fix: https://github.com/alwansan/raf/commit/3ee2e1ac5727f29485d14db28b846540576058bf
test: https://github.com/alwansan/raf/commit/a9e5b9bd9efd2862bd28f515824c4f665b984aab
result: JSON duplicate keys in private first-pass capture manifest rejected before pixel read. Four new regression cases. Tests not run locally because DNS for GitHub failed. No Unity or APK build launched; no modification of T4 physical mouse/T5 UI/Resolution scope.
next: run regression and compare actual original-derived FFT GUID->FindKernel->Dispatch and first divergent Vulkan/Unity pass, using isolated private captures.
readiness: WATER-001 OPEN; NOT_READY 0/3; no device water success asserted.
