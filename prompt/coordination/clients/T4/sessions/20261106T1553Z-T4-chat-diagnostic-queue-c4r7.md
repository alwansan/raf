# T4 chat — bounded critical diagnostics queue under broken storage

- session_id: `20261106T1553Z-T4-chat-diagnostic-queue-c4r7`
- origin: `chat`; status: `active`
- base_sha: `0538a6a2f310bb9f01391c50bdd73af4655ec19c`
- resumed_from_sessions: `20261106T1543Z-T4-scheduled-p8r2`, `20261106T1519Z-T4-chat-freshclr-owner-rgd-h3q9`
- issue: LOCAL-005 (diagnostic evidence for local world/save)
- work: `prompt/coordination/work/LOCAL-005/T4-20261106T1553Z-T4-chat-diagnostic-queue-c4r7-critical-logger-queue-fault.json`
- experiment: `T4-LOCAL005-PersistentDiagnosticLog-source-synthetic-IO-failure-mixed-critical-uncritical-queueLimit-redgreen-net8-v1`

## Evidence baseline and bounded hypothesis before editing
Owner 5-Nov phone run [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) confirms gameplay/save/reopen only for old source e9c358e, with tens of thousands of water and kernel errors in 5-Nov logs. No new phone candidate/test. Last T4 original CLR 7/7 fresh-process [CI42242683652](https://github.com/alwansan/raf/actions/runs/42242683652) is exact original managed result, not Unity device proof. Latest T4 scheduled 1543Z was a provenance audit with no game/source changes.

Examined `android-port/Runtime/Platform/PersistentDiagnosticLog.cs`: `Write` when `Interlocked.Increment(ref count) > queueLimit` decrements count, then for critical severity calls `Flush()` but **unconditionally increments count** before enqueuing. `Flush` internally catches disk I/O exceptions; if the startup/rotated segment has failed before `Drain` dequeues pending events, a mixed flood of dropped normal + critical messages can fill past the advertised queue cap and increase memory pressure during the exact owner-world shader/FFT error floods. No user RGD needs changing.

## Independent test and fix plan
Only existing diagnostic sink and `android-port/Tests/Diagnostics/Program.cs`. First add a source-only .NET8 deterministic red test: queueLimit=1, block background drain with test-controlled ioGate, dispose startup FileStream deliberately (private test instance only), write one pending line, then alternate dropped noncritical with critical; inspect pending/count via reflection, demand count <= limit even on I/O errors. The current source should fail. Then fix `Write` to recheck capacity after best-effort `Flush`, discard extra critical events when disk remains blocked (record dropped count), preserving healthy critical immediate flush and all existing diagnostics tests.

Existing workflow `.github/workflows/raft-persistent-diagnostics-tests.yml` runs native source-free .NET8, no original assets or heavy Unity, no new workflow. Red/green CI SHA logs and safe owner device boundary to be saved. No T1/T2/T3 water/render, T5 signed package, virtual touch/buttons/settings, .rgd or Unity assets changed.

## Next
Publish red test, inspect exact CI, patch capacity condition, require successful existing .NET8 gate and record event/T5 test handoff. LOCAL-005/INPUT-005 OPEN; NOT_READY 0/3.
