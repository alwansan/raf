# T4 — Android physical mouse bridge evidence boundary

- session_id: 20261107T0740Z-T4-scheduled-mouse-bridge-boundary-q9r2
- origin: scheduled
- base_sha: f89296d58efec8b1e55e7b50b085144564e664f8
- scope_commit: db666d14d21b9800bec60832e786b7bd60a7fff4
- resumed_from_session: 20261107T0635Z-T4-scheduled-owner-artifact-priority-r8m2.md; T4 chat/scheduled checkpoints in clients/T4/sessions
- issue: INPUT-005; LOCAL-005 remains OPEN for regression; work: prompt/coordination/work/INPUT-005/20261107T0740Z-T4-scheduled-mouse-bridge-boundary-q9r2.json

## Read-only engineering result

The existing `android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs` **already implements** Android API26+ `View.requestPointerCapture`, a generation-bound `OnCapturedPointerListener`, historical relative-motion accumulation, `hasPointerCapture` probes, release/focus safeguards, original `Cursor.lockState` intent, and fallback to original `Input.GetAxis` when native capture is unavailable. `PhysicalMouseMotionSource.cs` separates SOURCE_MOUSE_RELATIVE from touchpad AXIS_RELATIVE_X/Y. `AndroidImmersiveSystemBars.cs` already uses WindowInsetsController for Android 11+ with sparse rehide and lifecycle guards. `scripts/t4_adapt_original_mouse_axes.py` applies a SHA-gated original axis bridge to exactly four X/four Y and two lock assignments; `scripts/t4_original_mouse_routing.py` is a read-only authenticated source census. These are source observations **not** a claim that this shim was staged in owner-tested APK or works on a physical mouse.

**Decision:** do not add duplicate capture injection, change original keyboard/Mouse0/Mouse1 or touch ownership, or edit T5's three buttons and Resolution. Next decisive evidence is to check the exact immutable build staging manifest for the bridge, and then compare device logs `physical_mouse_capture_requested`, `physical_mouse_relative`, `physical_mouse_capture_lost`, `physical_mouse_capture_view_changed` while switching world/menu, unplugging the mouse, moving across screen edges and pressing Escape. Verify camera relative rotation and Raft's menu cursor with keyboard retained. The owner-tested world entry/save/exit/reopen on run 42058825739 remains confirmed only for that build; do not reopen APK86's world failure or mutate .rgd.

## Artifact urgency verified again (2026-11-07)

GitHub Actions API for run 42110297871 reports retained owner-tested delivery artifact 13454900880 (5,948,243,834 bytes, sha256 archive digest 41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef), expired=false, expires **2026-11-08T21:12:40Z**. Run 42296450023 retains signed checkpoint 13550196498 and delivery 13549514149, both expired=false, expiring **2026-11-09T23:48:15Z** and **23:49:06Z** respectively. The older owner-tested delivery must be archived first by T5; connector cannot stream these multi-GB binary artifacts. Release HTTP403 remains a distinct publishing failure; archive SHA does not validate extracted APK/OBB.

## Result, limits and next step

A source-path audit eliminated the need for a redundant mouse-capture implementation; no source edit, CI launch, binary download, phone test or release was performed. This session's work is bounded and complete; INPUT-005 remains OPEN, device mouse behavior unconfirmed, and full readiness NOT_READY. T4 next should inspect exact staging evidence for the physical-mouse bridge and add a focused missing contract test only if a specific source/runtime defect is demonstrated; T5 owns button relocation/Resolution and artifact recovery. No B workers restarted; no original files or secrets published.
