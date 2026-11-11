# T5 scheduled checkpoint — 2026-11-11T03:51:10Z

- session_id: 20261111T035110Z-T5-scheduled-delivery-evidence-k7m2
- origin: scheduled
- scope: original APK89/OBB delivery provenance vs shared Mini R5; no T4 mouse or Unity files.
- scope-plan commit: 9f714e99a1bafaaa478da11f9de85aeae56b0db4
- latest prior checkpoint supplied in scheduled chat: c200ec56a5e369d9fe4e9f740bb34e185779db20 (original package artifacts unavailable). Older T5 state.json is 2026-11-08; not authoritative over independent session files.
- Source: docs/DEVICE_FEEDBACK_42058825739_AR.md blob 756d6b3f9d0846255994fd0fe619d52f17594825, source build e9c358eda01785b65e4eb14f18723da426635628. Owner confirms world enter/save/exit/reenter on artifact from run 42058825739. Delivery publish step failed; artifact IDs reported 13441227298 / 13441766832.
- Independent old delivery metadata audit run 42222494746 (prior sessions): APK versionCode89 size672853870, OBB size2301256312. These metadata values do NOT establish SHA256/signature or match an installed phone copy.
- Separate shared Mini R5 readiness blob 6b06bc706c632735fe4f9c4b62d827da09570f3e: CI42691609924 SUCCESS, package com.alwansan.raft.lab.shared, versionCode17, APK110042 bytes SHA256 272d4ce9a199c5876b179926c9f27ed0d7a8c4db34b2a3993de2c44a94e323cf; this is NOT game APK89. R5 adds Android15 SAF Download/logs tree inventory and explicit APK/OBB91 SHA256 buttons. Thus no new Mini driver is needed merely to collect file hashes. Crucially OBB91 from owner Download/logs is not automatically OBB89; require versionCode, package, size, full SHA and source manifest before linking performance samples.
- LogRaft gate CI42909115184 was reported SUCCESS by prior T5 session (190 pinned CL samples); this establishes parser/gate validation only, NOT FPS/GPU performance improvement or phone comparison.
- Device 5 Nov report: 220911-559 57 estimated display-frame samples mean22.29 FPS minimum3.02, screenshot HUD18.27 FPS p95 82.82ms; these are distinct measurement methods and must not be pooled. CL source commit 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
- Actionable gate: (1) Obtain APK and OBB bytes from same original signed checkpoint, (2) independently compute sha256sum and APK signature/certificate/versionCode/package; inspect APK manifest OBB expected main.<versionCode>.<package>.obb and compare actual OBB name/size/hash; (3) compare against device export from R5 SAF without assuming OBB91 belongs to APK89; (4) only then label CL performance cohorts with binary provenance. Never use Mini's debug cert for the game.
- Files changed: isolated scope and this checkpoint only. No source code, UI, signed package or device test changed. No CI triggered; readiness NOT_READY 0/3.
- Next: prioritize actual Resolution and three right-side buttons on game source, after inspecting latest T4 overlap; validate signed game bytes if accessible. Do not duplicate already shipped R5 SHA buttons.
