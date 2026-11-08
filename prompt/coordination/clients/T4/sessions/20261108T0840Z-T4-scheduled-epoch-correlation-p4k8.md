# T4 — Android physical mouse capture epoch correlation
session_id: 20261108T0840Z-T4-scheduled-epoch-correlation-p4k8
origin: scheduled
branch: feature/android-native-port

## Evidence and scope
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Owner confirmed gameplay world entered, saved original .rgd, exited and reopened on artifact run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628; release publishing failed. Preserve this phone evidence; it is not proof of the newer mouse bridge. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 documents black native pointer and edge system bars. T5 owns buttons, resolution and packaging; T4 owns physical mouse and Raft cursor. Keyboard and touch remain unchanged.

Resumed from 20261108T0737Z-T4-scheduled-epoch-telemetry-c9m4 and earlier T4 CI 42447922773 (source tests success). Work record: prompt/coordination/work/INPUT-005/20261108T0840Z-T4-scheduled-epoch-correlation-p4k8.json; scope commit fbc2bda877e6bbd9d6cf0d628c5b9ffd0a3f761c.

## Changes
- 8e084dfa1948594d3e52dd5b126d08701d987e0d: bounded first request/retry diagnostics now include current request generation. Capture requests and listeners remain unchanged.
- 2bcb9bc78bbc4c9be1424d91b02cd709e3cf4b88: relative movement event reports the generation of the callback that actually supplied motion, not the latest request generation (which can advance before Update logs the marker).
- bb1c78f950fa7ddd1e3a1d2acf00e1221685bd5c: three source-contract regression tests for request order, epoch attribution, and unchanged legacy axis fallback.

## Verification limits
Source review confirms the intended logging paths and no changes to native View request/release, original cursor lock, keyboard, touch, save, .meta, GUID, audio, or Settings. New tests have not yet been executed in CI; no Unity/device verification and no fresh CL mouse trace. Existing CI successes predate these changes. No native build or duplicate Actions requested; no claim that the physical mouse or Raft cursor is fixed.

## Next
Run the three Python source tests in an appropriate source-only CI/check, then obtain a phone log from a package containing these changes. Correlate physical_mouse_capture_requested/retry epoch with physical_mouse_relative epoch and view_changed/lost/release. Test mouse movement at screen edges, Escape/menu/reentry, refocus, detach, and keyboard; preserve world save/reopen. INPUT-005 OPEN; LOCAL-005 owner phone success retained, not closed. Trial build vote remains T4 needs, no 5/5 consensus.
