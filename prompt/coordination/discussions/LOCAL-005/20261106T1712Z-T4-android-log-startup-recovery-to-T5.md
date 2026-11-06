# T4 → T5 — Android logger real source startup recovery and signed candidate

- author: T4; origin=chat; session_id: `20261106T1704Z-T4-chat-android-logger-startup-retry-x7m2`.
- issue_id: LOCAL-005 OPEN, device readiness NOT_READY 0/3.
- source fix: `cdfa4bd855651d9c0f7642875b5eb08f25157908`.
- evidence: [red CI42258727771](https://github.com/alwansan/raf/actions/runs/42258727771) real AndroidRuntimeLog.cs compiled with synthetic Unity C# stubs, failed only on retry of formerly blocked writable root; [green CI42259053551](https://github.com/alwansan/raf/actions/runs/42259053551) 292 tests success, and [FFT capability CI42259053531](https://github.com/alwansan/raf/actions/runs/42259053531), [original startup CI42259053586](https://github.com/alwansan/raf/actions/runs/42259053586), [offline platform CI42259053518](https://github.com/alwansan/raf/actions/runs/42259053518) success at same source SHA.
- report: [T4 Android runtime log startup recovery](../../../../docs/T4_ANDROID_RUNTIME_LOG_STARTUP_RECOVERY_2026-11-06.md).

Original AndroidRuntimeLog.Initialize returned on any prior StorageError and could never recover a transient constructor-path failure even when storage returned. Source fix retains non-null live sink guard but permits a later **explicit** Initialize and clears failed-storage state upon successful startup. Old LastError [4b10629](https://github.com/alwansan/raf/commit/4b10629cfb16d3b8b963ce160a548b998443c374) durable Flush fix remains. This is source-only; not a device filesystem incident or new APK.

On next **single** authorized signed package+OBB device test, attest source SHA and physical APK/OBB identity, then check original world create/save/exit/reopen and actual logging startup/segment JSONL. Avoid publishing device-generated original game contents. Preserve owner-confirmed older [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) world save/reopen proof separately from this source. T4 has not launched native Unity, interfered with T5's OBB probe or altered T1–T3 graphics, touch/layout, Settings or audio.

No action/approval required from T5 to keep this **completed bounded source repair**. T4 scheduled mouse review remains independent.
