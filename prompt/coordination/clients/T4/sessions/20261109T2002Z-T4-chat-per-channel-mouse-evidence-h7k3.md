# T4 chat — original mouse channel-level evidence correlation
session_id: 20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3
origin: chat
issue_id: INPUT-005
status: completed_source_only_device_pending
base_sha: 99c25340edb45bbd18d4a33ed9937d0679e7114f
scope_commit: 3853a4929f65f21f18977783142682f3c683b337
resumed_from_sessions:
- 20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6
- 20261109T1939Z-T4-scheduled-reader-poison-q8m5
experiment_key: T4-INPUT005-genuine-Android-pressMask-unity-reader-channel-correlation-v1-Unity2021
resource_key: none
owned_paths: scripts/t4_correlate_mouse_runtime_epochs.py; scripts/tests/test_t4_correlate_mouse_runtime_epochs.py; this session/work/experiment/event only.

## Verified recovery
CI42687110814 succeeded 30/30 in prior chat; the game source-only analyzer checked genuine logger sessions, epoch boundaries and aggregate callback/reader counts. It had no channel-specific match. Latest [CL/test shared-20261109-225506-552476830](https://github.com/alwansan/CL/tree/main/test/shared-20261109-225506-552476830) reported one genuine v0.2.14-shared phone session, 30 cases, **T4-01..09 NEEDS_INPUT**, not pass/fail; no T4 capture-run logs. T1-05 synthetic local512 PASS is not original Raft FFT. T5 built latest one unified mini CI42686652150 independently. No new signed Raft full-game acceptance. HEAD 99c25340 before work reservation; zero queued/in_progress Actions at reservation.

## Hypothesis
Existing correlation accepts *any* captured callback and *any* positive Unity fallback getter in one logger-session epoch. For example, a physical LEFT callback could pair with an unrelated RIGHT fallback; total positives alone do not resolve the mouse channel. C# original producer emits `pressMask`, `releaseMask`, `verticalScrollCallbacks`, `horizontalScrollCallbacks`; `PhysicalMouseLegacyReaderEvidence.Report()` emits 11 per-channel `Calls,legacy,fallback` slots. Parse and cross-check only complete authentic-looking source telemetry, record button press/down and release/up co-observations, plus vertical Axis and wheel vector candidates without asserting horizontal-only scroll from vector read. Preserve generic aggregate result for legacy records but do not elevate incomplete/mismatched slot data to channel proof.

## Planned verification
Add positive and negative synthetic producer-conformant records (left/right/middle mismatch, missing slots, disjoint masks, scroll axis/vector, counters inconsistent), run existing isolated 5-minute Python workflow; no Unity build, no APK/XAPK dispatch, no side-effect on T5/other workers. Keep `unity_gameplay_verified=false` and `device_pass=false`.

## Next
Complete per-channel code/CI, document evidence and limitations; next real owner signed-game one-process data still needed to establish actual button/wheel actions.

## Implementation and CI proof
- Original C# source cross-check: `AndroidPhysicalMouseCapture.LogCapturedActions` publishes button press/release masks and vertical/horizontal callback totals; `PhysicalMouseLegacyReaderEvidence.Report()` publishes eleven independent `held/down/up` and `scrollAxis/scrollVector` slots with `Calls,legacy,fallback` counters. Prior T4 aggregate correlation might pair a LEFT captured callback with an unrelated RIGHT fallback positive. The new report labels channel matches explicitly as **co-observations**, never gesture delivery or phone PASS.
- Source commit [9aab2f7f](https://github.com/alwansan/raf/commit/9aab2f7f7ec4445382c1a335616627a8f2341a69) adds optional complete slot parsing, sum consistency and monotonicity checks, press/release mask consistency, LEFT/RIGHT/MIDDLE down/up candidates, VSCROLL axis and wheel-vector candidate, explicit `horizontal_wheel_getter_independently_proven=false`. Abbreviated old logs and implicit ACTION_DOWN/UP without pressMask cannot generate false explicit-button channel proof.
- Test commit [efbbd593](https://github.com/alwansan/raf/commit/efbbd593f0f390e4bc220e759f618c76f2b4b016) adds **12** adversarial and positive tests: left/right/middle channels, cross-channel spoof, vertical/horizontal limits, incomplete slots, mismatched totals, duplicate slots, invalid mask rollback and impossible zero-press mask.
- Initial [CI42689746931](https://github.com/alwansan/raf/actions/runs/42689746931) COMPLETED SUCCESS, 30/30 after source change; final [CI42689914245](https://github.com/alwansan/raf/actions/runs/42689914245) COMPLETED SUCCESS on efbbd593, job `129406623136`, log states **Ran 42 tests in 0.013s; OK**. No Unity or Android app build was launched by T4.
- Detailed report `docs/T4_MOUSE_ORIGINAL_CHANNEL_CORRELATION_2026-11-09.md` commit `5aec1e2e`; own experiment `prompt/coordination/experiments/T4/20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3.json` commit `44195f8d`; own canonical B_TEAM event `prompt/coordination/B_TEAM/events/T4/20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3.json` commit `cb6de34e`.
- Independently inspected owner CL main `test/shared-20261109-225506-552476830`: app v0.2.14-shared, source `2d7c268248b505e4dd9ad1daa9491787df07665c`, pack 30 tests; `T4-01..09` all **NEEDS_INPUT** without mouse child capture attempt. No device PASS inferred. A T1 synthetic GLES compute PASS is a separate worker's evidence, not original Raft FFT.
- No shared Mini build, no full XAPK, no modification to Unity/game original files, camera, Android gesture handling, full-game native build request, T5/T3/T2/T1 source, or `.rgd` data. Source-only evidence remains separate from actual original Raft mouse gameplay.

## Safe next checkpoint
This scope is completed and no source resources are still leased. **INPUT-005 OPEN; full game NOT_READY 0/3.** At the next T4 scheduled/chat pass, check latest actual phone CL/test before repeating a case. When T5/owner has a new genuinely signed full Raft game candidate containing latest button+wheel adapter, pin its source signature and collect a **single app-process chronological PersistentDiagnosticLog** with captured=true plus matching getter counters from actual LEFT/RIGHT/MIDDLE and V/H gestures. Run `python3 scripts/t4_correlate_mouse_runtime_epochs.py /path/to/one-process.jsonl` and report channel co-observations separately from the **human-observed gameplay response**; horizontal wheel needs independently verified X direction. Test camera/focus/keyboard/touch and world/.rgd save regression as well. Do not request a duplicate Mini or XAPK from this source-only result.
