# T4 — original Android captured mouse channel ↔ Unity Legacy reader evidence

Date: 2026-11-09, source-only; session: `20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3`. Issue: **INPUT-005 (OPEN)**.

## Verified reason for this engineering step
The earlier same-`session` / capture-`epoch` classifier could pair a physical LEFT captured callback with a different RIGHT Unity fallback getter and report an aggregate positive, even though no LEFT getter had been proven. The original producer is more detailed:
- `AndroidPhysicalMouseCapture.LogCapturedActions` emits `pressMask`, `releaseMask`, `heldMask`, `pressCallbacks`, `releaseCallbacks`, `verticalScrollCallbacks`, `horizontalScrollCallbacks` and monotonically increasing totals.
- `PhysicalMouseLegacyReaderEvidence.Report()` in `PhysicalMouseMotionSource.cs` emits exactly 11 per-channel `<name>Calls=N,legacy=N,fallback=N` groups: `held0/1/2`, `down0/1/2`, `up0/1/2`, `scrollAxis`, `scrollVector`.
- Authored C# `Record` counts each getter, with native preferred and fallback applied only after source checks. Down/Up and Scroll positive counts are separate. This is **getter evidence, not gameplay actions**.

## Change
`scripts/t4_correlate_mouse_runtime_epochs.py` now reads those optional original slot triplets, rejects duplicate/inconsistent complete slot ledgers, checks that the sum of slot calls/native/fallback hits and Down/Up/scroll subtotals equals the aggregate counter envelope. If an old/abbreviated text excerpt omits one or more slots, it may still contribute to the **legacy aggregate** classifier, but its channel-specific counters stay at **zero** rather than becoming guessed channel evidence. Source captures lacking an explicit mask likewise cannot produce press/release channel-specific co-observations.

Output fields added:
- `complete_per_channel_scoped_attempts`: matched attempts with valid complete source masks and 11-slot reader counters.
- `captured_press_with_matching_fallback_down`: per LEFT/RIGHT/MIDDLE count of same-epoch press-mask bit plus matching `down0/1/2` fallback evidence.
- `captured_release_with_matching_fallback_up`: per LEFT/RIGHT/MIDDLE release-mask bit plus matching `up0/1/2` fallback evidence.
- `captured_vertical_wheel_with_fallback_scroll_axis_attempts`: vertical callback plus `scrollAxis` fallback co-observation.
- `captured_wheel_with_fallback_scroll_vector_attempts`: V or H callback plus `scrollVector` fallback co-observation. A nonzero `scrollVector` fallback does **not** identify whether its X component was nonzero, so `horizontal_wheel_getter_independently_proven=false` always.

All fields count only eligible same-logger-session / capture-epoch attempts after existing provenance and producer checks. They **do not** assert one-to-one gesture causality, pixel/playable control, Unity gameplay or Android phone acceptance. Down/up may be observed from ambiguous ACTION_DOWN/UP without an explicit pressMask; such cases are intentionally not upgraded to mask-based candidate evidence. Captured callbacks and consumers can occur in the same epoch for unrelated gestures.

## Reproducible evidence and limitations
- Implementation commit [9aab2f7f](https://github.com/alwansan/raf/commit/9aab2f7f7ec4445382c1a335616627a8f2341a69).
- Twelve independent source regression tests commit [efbbd593](https://github.com/alwansan/raf/commit/efbbd593f0f390e4bc220e759f618c76f2b4b016) covering left/right/middle matching, a left-to-right mismatch control, V/H axis honesty, missing slots, impossible counter sums, duplicate slots, a bogus mask, and mask rollback.
- Original [CI42689746931](https://github.com/alwansan/raf/actions/runs/42689746931) after implementation: SUCCESS, pre-existing **30/30**.
- Final [CI42689914245](https://github.com/alwansan/raf/actions/runs/42689914245): SUCCESS on source SHA `efbbd593f0f390e4bc220e759f618c76f2b4b016`, job `129406623136`, **42/42** Python tests, no Unity heavyweight build.
- Fresh authentic owner upload [CL/test/shared-20261109-225506-552476830](https://github.com/alwansan/CL/tree/main/test/shared-20261109-225506-552476830) was inspected; app `0.2.14-shared`, pack with 30 cases, owner device Android 15, nine `T4-01..09` entries **NEEDS_INPUT**, not PASS or FAIL; this upload contains no T4 captured physical mouse child session. Synthetic T1-05 passed (1024 float readback) but cannot be used to prove original Raft gameplay or captured mouse.
- No new Raft full-game signed XAPK was built by T4. Previous game world/save evidence 42058825739 predates the newest mouse adapter source. The independent mini APK built by T5 is not the full game.

## Next owner / T5 cooperation
When the **separately authorized** full game XAPK containing current original mouse adapter source exists, collect a chronological `PersistentDiagnosticLog` JSONL from a single app process without duplicated startup segments. Test LEFT/RIGHT/MIDDLE press and release plus vertical and horizontal wheel with pointer capture ON, preserve camera/focus/keyboard/touch, offline world and .rgd save, audio, Settings. Run:

```bash
python3 scripts/t4_correlate_mouse_runtime_epochs.py /path/to/one-process-raft-log.jsonl
```

Report the per-channel co-observation counts **and** separately the owner-observed in-game effect. This script returns `device_pass=false` and `unity_gameplay_verified=false` by construction. Horizontal scrolling needs explicit X-axis device/game verification; do not treat wheel-vector presence alone as horizontal wheel success.

**INPUT-005 OPEN; full Raft NOT_READY 0/3.** Neither source tests nor Mini reports override the full-game XAPK 5/5 gate.
