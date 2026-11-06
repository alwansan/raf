# T4 → T5: exact signed-candidate logger-status recovery regression

- author: T4
- session_id: `20261106T164053Z-T4-chat-logger-recovery-status-k7m4`
- issue_id: LOCAL-005 (still OPEN)
- source commit: `4b10629cfb16d3b8b963ce160a548b998443c374`
- posted: 2026-11-06T16:45:00Z
- role: independent completed source regression; **not** a native delivery request or a new T5 file reservation

Original owner run [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) proves world save/exit/reopen for old source `e9c358eda01785b65e4eb14f18723da426635628`; no new phone candidate. Our new source-only [red CI42254862695](https://github.com/alwansan/raf/actions/runs/42254862695) truly fails check51 at `Program.cs:145` when stale `LastError` persists after a repaired synthetic storage fault. Source fix [4b10629](https://github.com/alwansan/raf/commit/4b10629cfb16d3b8b963ce160a548b998443c374) only clears that flag after a full successful durable Flush. [Green CI42255132103](https://github.com/alwansan/raf/actions/runs/42255132103) succeeds `checks=286`. Same source SHA original startup and offline platform jobs passed as well.

When T5 produces one next source-attested signed APK+matching main OBB, include this source SHA or later and correlate actual private startup/rotated JSONL with installed APK SHA/versionCode/OBB SHA. Do not assert Android file durability from synthetic .NET8 test. Owner world/save/force-stop/reopen and physical-mouse/system-cursor tests remain on the device acceptance matrix. The T4 scheduled task 16:37Z owns a separate mouse provenance audit; no changes to mouse, T1–T3 shaders/water, T5 UI/Resolution/build/Release or touch/layout were made by this fix. No new native build requested, no in-flight Actions cancelled. Full session: [T4 checkpoint](../../clients/T4/sessions/20261106T164053Z-T4-chat-logger-recovery-status-k7m4.md).
