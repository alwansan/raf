# T4 scheduled session 20261107T1843Z-T4-scheduled-multi-rearm-f6k2

- origin: scheduled; track: INPUT-005; branch: feature/android-native-port.
- Starting HEAD: 79669c6f8ecfa1f2863971b47df3543c7becad4b; scope commit e370ef0552c392a7d44de57631cd4e68861b99aa.
- Owner-confirmed phone result: artifact run 42058825739 at e9c358eda01785b65e4eb14f18723da426635628 entered local world, saved, exited and reopened. This is limited device evidence, not a proof of mouse success or APK file hash.
- Source finding: classifier previously chose min(eligible) for all lock attempts, so an initial released request hid a later valid request+relative event in the same Escape cycle. This is a classification error, not a demonstrated Android runtime failure.
- Fix df72b524c10a4d3d122f2d3dc5551f4e142cf054: inspect each lock interval bounded by release/unlock/next Escape and accept relative movement only within a valid request window. Regression 5037b77bfb86c106b12e76084f9522517933c831 adds second-attempt success and stale post-release request tests; total 15 tests in source.
- Verification: static source review only; Python execution/CI on these commits NOT verified in this session. Prior mouse CI 42373576554 succeeded at older 27fc3baf. Do not claim current 15/15 or device success. No Unity build or workflow triggered; no concurrent build canceled.
- Shared scope: T5 owns Resolution and three right-side buttons; T4 did not modify them. No .rgd, keyboard, audio, touch, Settings, Unity source or original game assets changed. Existing T4 diagnostic scope continued with separate test cases and isolated files.
- Next: run python3 -m unittest tests.test_t4_classify_mouse_capture_log (or unittest discover), validate 15/15, inspect CL new physical mouse event traces for escape -> lock -> capture -> relative and check Raft cursor/menu/keyboard on a signed candidate. Confirm source and package manifest with T5. Keep INPUT-005 OPEN, LOCAL-005 OPEN, NOT_READY.
