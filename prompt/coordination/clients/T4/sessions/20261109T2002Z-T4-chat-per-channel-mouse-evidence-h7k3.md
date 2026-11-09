# T4 chat — original mouse channel-level evidence correlation
session_id: 20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3
origin: chat
issue_id: INPUT-005
status: active
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
