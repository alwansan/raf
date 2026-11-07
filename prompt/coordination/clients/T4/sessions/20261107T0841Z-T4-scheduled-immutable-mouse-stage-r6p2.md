# T4 — immutable physical mouse staging boundary

- session_id: 20261107T0841Z-T4-scheduled-immutable-mouse-stage-r6p2
- origin: scheduled
- issue: INPUT-005; LOCAL-005 remains OPEN for regression only
- start HEAD: `3ce3cedd2fa4aa3e4ce1bfce9b3e534d654f3096`
- scope commit: `6bb7dcb7d345445bef328418d4fb2dee0f0aa5e7`
- work: `prompt/coordination/work/INPUT-005/T4-20261107T0841Z-T4-scheduled-immutable-mouse-stage-r6p2.json`
- previous checkpoint: `clients/T4/sessions/20261107T0740Z-T4-scheduled-mouse-bridge-boundary-q9r2.md`

## New immutable-source finding

Read directly from GitHub at **native run 42296450023 source `a1737bd7`**, not merely today's HEAD:

1. `.github/workflows/raft-unity-editor-android-import.yml` blob `f93c9381a22ae42b96b2e04299f58a8e95de085a`: line 667 calls `python3 -m scripts.t4_adapt_original_mouse_axes` with the original DLL and `--apply`; line 672 copies `AndroidPhysicalMouseCapture.cs`, `PhysicalMouseDeltaAccumulator.cs`, `PhysicalMouseMotionSource.cs` and immersive-bars source to exported Unity Assets.
2. `scripts/t4_adapt_original_mouse_axes.py` blob `e0ee65310ac85d6eb770de8cf87cc067fff4338d`: `EXPECTED = {"mouse_x": 4, "mouse_y": 4, "cursor_lock": 2}`; guarded original-source adaptation rather than blanket mouse/keyboard rewrite.
3. `android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs` blob `75f5b3145189362434bb6d2e9b6b743f639bffad`: native `requestPointerCapture`, listener, relative deltas and Unity fallback present.
4. `android-port/Runtime/Platform/AndroidTestDiagnostics.cs` blob `d508f2297ca48ea2955fd4dc20612e120d80a168`: startup adds `AndroidPhysicalMouseCapture` component.
5. Attempted to read the same capture source at owner-tested immutable `e9c358eda01785b65e4eb14f18723da426635628`; GitHub returned 404 for this path. Thus do **not** attribute the newer mouse bridge to the owner-tested world/save package. The absence of that path alone does not establish the old APK's mouse implementation.

This is a stronger **source staging** proof for the newer Unity run than checking today's branch. It is **not** extracted APK content proof, native pointer capture success, or physical-device evidence. Existing run 42296450023 reconstructed Unity successfully but release publishing failed HTTP403; no redundant build triggered. No changes to touch, keyboard, buttons, resolution, save schema or gameplay. T5 owns the three buttons/Resolution and package preservation.

## Next decisive evidence

T5 should preserve signed APK/OBB and inspect the package build manifest/source SHA; T4 should compare phone log markers `physical_mouse_capture_requested`, `physical_mouse_relative`, `physical_mouse_capture_lost` and `physical_mouse_capture_view_changed` on the newer package while testing continuous camera rotation across edges, Raft menu cursor, Escape, focus/unplug and keyboard. If the logs show no request despite connected physical mouse, investigate Input System `Mouse.all` vs Android legacy `Input.mousePresent` detection before modifying the bridge. Do not assume success from source alone.

Owner-confirmed world entry, save, exit and reopen on run 42058825739 remains preserved as **limited device success**. No .rgd schema mutation or fake completion flag. Read-only CL evidence is in `docs/DEVICE_FEEDBACK_42058825739_AR.md`; no new CL device test claimed. No other Actions cancelled or duplicated. Status: INPUT-005 OPEN, native phone acceptance unknown, readiness NOT_READY.
