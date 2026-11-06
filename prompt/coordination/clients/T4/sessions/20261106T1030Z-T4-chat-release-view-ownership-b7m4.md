# T4 chat — fail-closed Android View ownership on pointer capture release

- session_id: `20261106T1030Z-T4-chat-release-view-ownership-b7m4`
- origin: `chat`
- base_sha: `d8bf08a9fe4305dadea4948c2079962669292a86`
- resumed_from_sessions: `20261106T1014Z-T4-chat-owner-world-wire-parity-n7q3`, `20261106T0946Z-T4-chat-pointer-view-ci-q4r8`, `20261106T0943Z-T4-scheduled-q7n4`
- issue_id: `INPUT-005` (OPEN)
- scope: `prompt/coordination/work/INPUT-005/T4-20261106T1030Z-T4-chat-release-view-ownership-b7m4-release-identity-failclosed.json`
- experiment: `prompt/coordination/experiments/T4/20261106T1030Z-T4-chat-release-view-ownership-b7m4.json`
- event: `prompt/coordination/B_TEAM/events/T4/20261106T1030Z-T4-chat-release-view-ownership-b7m4.json`
- source baseline: `AndroidPhysicalMouseCapture.cs` blob `5b5af47d9f05016f72f32ce6afbcc7460600ef25`
- final implementation SHA: `cb86cdcd8baf462f35c4217758a0a9e19fd56d4e`
- final exact CI: [42204448436](https://github.com/alwansan/raf/actions/runs/42204448436) **COMPLETED SUCCESS** at the final exact source SHA, job `127847457650`; separate Android platform CI [42204354877](https://github.com/alwansan/raf/actions/runs/42204354877) **SUCCESS** at earlier equivalent production source SHA `db74ad77` (before final test-only change).
- status: `completed_bounded_managed_source_ci_success`; **device unverified**.

## Why this is a new safe scope

Earlier T4 scheduled [0943Z](20261106T0943Z-T4-scheduled-q7n4.md) proved a source hazard: `ReleaseCapture` discarded the request-target identity and later called `releasePointerCapture` on a fresh `getCurrentFocus()` View. In a focus-switch, that may revoke a **different** View's capture. It did not prove that old View capture leaked, since Android OS may revoke on focus loss. This chat cycle fixes only the independent *wrong-target release* path; it does not attempt to keep a Java View JNI object across threads or claim a device hang.

## Exact implementation and safety

- `android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs`: snapshot the prior nonzero `captureViewIdentity` during the existing `captureGate` lock, then clear the identity as before. On Android UI thread, the queued release retains the original `releaseEpoch` / `requested` guard. Call `releasePointerCapture` **only** when the current focused View's `System.identityHashCode` equals that recorded request target and is nonzero, and it currently has pointer capture. Do not call it on another focused View.
- Do not store/reuse an `AndroidJavaObject` cross-thread. This is a bounded safety guard, not a guarantee that the original View is released after focus loss; the earlier OS auto-release hypothesis remains UNVERIFIED.
- Preserve original `epoch++;` and `int releaseEpoch = Volatile.Read(ref epoch);` source and asynchronous callback sequence; retain Android 26+ original source filters, camera fallbacks, keyboard, LEFT touch and system exit paths.
- `tests/test_t4_pointer_view_identity_contract.py`: two new static negative/ordering cases for ownership, epoch guard, and no JNI wrapper access before Android UI dispatch; original tests retained.
- No full Unity build, source game SaveAndLoad/World .rgd, shaders, FX, audio, Settings, touch layout, T5 packaging, other team's source, device data, original game assets or GUID changed. Only writable branch feature/android-native-port was used, without force.

## CI evidence with failures kept explicit

- Initial atomic implementation [5ca365e](https://github.com/alwansan/raf/commit/5ca365e134a2a3134017cf5128c4ee42a86a1e62): [CI42204140756](https://github.com/alwansan/raf/actions/runs/42204140756) failed **three source-only legacy lexical expectations** looking for original `epoch++;` and `int releaseEpoch = Volatile.Read(ref epoch);`; no C# compile or device was attempted in that failing job. Separate platform [42204140743](https://github.com/alwansan/raf/actions/runs/42204140743) was success.
- Next [db74ad7](https://github.com/alwansan/raf/commit/db74ad778cb8315c61fe3519d0fa3a2a76e10894) restored original epoch code while retaining the new View ownership guard; [CI42204361104](https://github.com/alwansan/raf/actions/runs/42204361104) failed **only one newly-authored overbroad test**: it incorrectly rejected a *comment* containing `AndroidJavaObject`. Actual static C# production code compiled in separate platform [42204354877](https://github.com/alwansan/raf/actions/runs/42204354877), SUCCESS.
- Final test-only [`cb86cdcd`](https://github.com/alwansan/raf/commit/cb86cdcd8baf462f35c4217758a0a9e19fd56d4e) checks actual Java object construction/calls rather than comment text. [CI42204448436](https://github.com/alwansan/raf/actions/runs/42204448436) **SUCCESS**. Actual job logs show 7/7 original route + 7/7 axis patch + 21/21 native bridge policy + 5/5 physical presence + **6/6** View identity (including 2 new release checks) = **46/46 source Python tests passed**. C# thread-safe motion controls and actual original ZIP2 Unity2021 ABI compile success; exact original DLL SHA and private ILSpy/axis patch stage succeeded. No original source leaked.
- The T4 CI job was not manually duplicated; the existing bounded workflow path triggers ran. All runs were observed to completion; no jobs canceled.

## Boundaries and device handoff

This proves source-level fail-closed release policy and managed-ABI compatibility only. `System.identityHashCode` is a diagnostic numeric identity that can theoretically collide; tests do not simulate Android View transitions. It is **not** Android runtime, full Unity IL2CPP, real mouse/keyboard, 360° camera, release at focus loss, or save-world device success. INPUT-005 remains OPEN; the older owner phone artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) confirms world/save/quit/reopen only on its earlier source, not on this fix. LOCAL-005 owner RGD original 7/7 byte exact .NET8 remains separately proven at [42201568118](https://github.com/alwansan/raf/actions/runs/42201568118). Overall NOT_READY 0/3.

Next step: T5 hand over **one immutable signed APK+matching OBB** (source SHA, package/versionCode, APK/OBB SHA256). On POCO F5 Pro with actual mouse+keyboard, verify menu Raft cursor vs system pointer; 360° camera movement; pause/resume/focus loss/reacquire, disconnect and system bars; correlate physical_mouse_capture_requested/view_changed/released/lost/relative and capture epochs. On same candidate, save real world, fully terminate process, reopen same .rgd/world, verify progress and original Save/Load snapshot/completion markers. If wrong View still captured or old View not released, collect Android callback evidence before new JNI design; never fake world state. Protect audio and Settings, defer touch/layout.
