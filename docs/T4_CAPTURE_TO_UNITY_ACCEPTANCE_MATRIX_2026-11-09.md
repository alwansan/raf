# T4 INPUT-005 — physical mouse Android→Unity acceptance matrix (9 Nov 2026)

**Status: evidence contract only, not a fix, not phone acceptance.** Scope: `INPUT-005/capture-to-legacy-20261109-q4m8`. T4 scheduled; source baseline `a02cf0835da13380e65bba6ab1395d59f7d3236c`. Do not conflate original 5 Nov phone game artifact with 8 Nov mini APK or subsequent source-only CI.

## Proven baseline and gap

- Owner confirms **world creation → enter → save → exit → re-enter** on artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source `e9c358eda01785b65e4eb14f18723da426635628`; publication failure is not world failure. Preserve original `.rgd` and FileManager/SaveAndLoad.
- [T4 authentic 8 Nov CL replay](T4_DEVICE_MOUSE_EVIDENCE_CL_20261108.md) found 373 deduplicated physical Android mouse events, 13 LEFT press/release pairs and 55 vertical wheel events, **all captured=false**; RIGHT, MIDDLE and horizontal wheel not demonstrated. These are **mini-lab callbacks**, not original Raft consumer events.
- [T4 original source adapter](T4_ANDROID_CAPTURED_LEGACY_BUTTON_WHEEL_BRIDGE_2026-11-08.md) stages 20 legacy button/scroll reads across 12 original files with SHA-authenticated ZIP2 source; source-only CI [42518143297](https://github.com/alwansan/raf/actions/runs/42518143297) succeeded. No corresponding signed full-game device run establishes that Unity read those values.
- 9 Nov T4 scheduled checkpoints hardened parser rejection of contradictory capture flags, malformed envelopes and negative button/source fields. Parser correctness does not establish Android pointer capture or game interaction.

## Required single-build, single-session evidence

| Case | Android evidence (same monotonic session and capture epoch) | Unity/Raft observation | Pass gate |
| --- | --- | --- | --- |
| Capture start | Explicit `capture_request=ON`, then `route=captured captured=true`; log actual focus and connected mouse | Camera rotates with relative motion across screen edge | ON alone = **inconclusive**, never PASS |
| LEFT | Captured physical `ACTION_BUTTON_PRESS` and `RELEASE` with buttonState transitions, not duplicate Activity route | Original Raft legacy `GetMouseButtonDown(0)`, held `GetMouseButton(0)`, then `GetMouseButtonUp(0)`; gameplay action | Native callback alone = **partial**, not PASS |
| RIGHT | Same captured pair for RIGHT | Legacy index 1 and original Raft action | Missing attempted press = **not tested** |
| MIDDLE | Same captured pair for MIDDLE | Legacy index 2 and original Raft action, if authored | Missing authored action means verify API route separately; do not fabricate action |
| Wheel | Captured `ACTION_SCROLL`, VSCROLL ± and HSCROLL ± separately when supported | Legacy `Mouse ScrollWheel` / `mouseScrollDelta` read, correct sign and frame | Zero / non-finite / uncaptured = no captured PASS |
| Menu and cursor | Capture OFF and release callback after exiting gameplay; request again upon return | Raft menu cursor visible and usable, system pointer not doubled; no Android bars at edges | Visual screenshots + event log required |
| Focus / detach | Focus loss, pause, physical detach, reacquire | No stuck button, no phantom click, keyboard works; touch unaffected | Capture state must reset across epochs |
| Save regression | World identifier, original `.rgd` existence, clean exit and reopen | Same world playable, save still readable | Preserve owner 42058825739 baseline; newer binary needs new phone proof |

## Collection and attribution

1. Record **APK versionCode, signer, source commit, artifact ID and OBB manifest/hash** before trial; never attribute results from the mini APK to a full-game build.
2. Run with physical mouse + keyboard in landscape. In a *single* log session first test menus, enter world, request capture, exercise LEFT/RIGHT/MIDDLE press+release and vertical/horizontal wheel deliberately, cross both edges, then exit to menu, detach mouse and repeat focus loss. Preserve native event timestamps, capture epoch, event route and Unity frame identifiers if emitted.
3. Export log + original unaltered screenshots through T5 unified testpack to [CL/test](https://github.com/alwansan/CL/tree/main/test). Avoid screenshot-only success and avoid treating automated EVIDENCE_READY as human PASS. If Unity consumer counters are not instrumented in this build, record **native-only** and keep consumer gate unverified.
4. Run existing `scripts/t4_analyze_mouse_lab_routes.py` on actual JSONL and check its `capture_request`, route conflict, button/wheel counts. Its output cannot by itself certify Unity legacy consumption. Match time/frame/epoch in both layers; reject stale epochs and duplicates.
5. Preserve T5 ownership of Resolution and three overlay controls; do not alter screen resolution from T4. Maintain existing keyboard and authored touch behavior, FMOD, Settings, original GUID/.meta and .rgd. No new Unity build without coordinated team gate.

**Decision:** INPUT-005 OPEN; source adapter exists but the missing proof is a captured Android callback **and** a corresponding original Raft Unity Legacy Input read in one signed full-game device session. No request to repeat existing mini CI.
