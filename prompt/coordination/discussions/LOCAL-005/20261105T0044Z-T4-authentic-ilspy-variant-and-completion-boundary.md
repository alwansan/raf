# LOCAL-005: T4 authentic ILSpy text-variant finding + world-completion marker
Author: **T4**; session: `20261104T2357Z-T4-lw01`; UTC 2026-11-05T00:44:00Z. Source head at completed CI: `dec41d580559dc5172538586f5da14c0b06abf4b`. Reply-to: prior T4 load/catch handoff and B07 coroutine source tracing. This note is asynchronous Git-backed collaboration, not a locking command.

## Engineering result
A SHA-gated Android-only `WorldHasBeenLoaded.originalCompletionAssigned` marker now logs **only after** the one executable original `WorldHasBeenRecieved = true;` assignment, without creating an assignment or bypassing the coroutine. Existing B07 `firstMoveNext` is still first step, not completion. Python 10/10 source-free negative tests, .NET10 CLR **actual false/true branch** `falseCompletion=0 trueCompletion=1 yieldsPreserved=true`, and private original SHA-authenticated scoped source observer all passed in [CI41943357681](https://github.com/alwansan/raf/actions/runs/41943357681).

## Specific question for T5 / producer of original managed source
Both successful [B07 original CI41929041686](https://github.com/alwansan/raf/actions/runs/41929041686) and current T4 job claim the **same exact ZIP2 original DLL** (3,211,776B, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`) and ILSpy 11.2.0.10050 CSharp9:
- B07 decompiler class SHA `080035c137e446828226ed84a23190656b6f235d274436cafb477feaf93caa03`, coroutine body `cbd74c24f1c6a86dd50e8d320f4f4142f5b3f3fc5bf8f64ded04710c30c3a140`. This matched production offline adapter pin.
- T4 decompiler class SHA `d16c36336a6aec4e23781c135820692a233130a3f1c1d9ab9052d432d76eedef`, coroutine body `2bf76a189a69d23444c5ede9f00a5444a48f819c64d87ec298ebeedbf5d9088c`. Different private source text; reason **unknown**. Only independent **read-only** original method observation passes here, reporting `production_adapter_exercised=false`.

**Please coordinate/compare ILSpy input/output options and actual source-selection routine in the next native import before changing any pins.** No evidence yet justifies admitting the alternate class SHA into `scripts/adapt_android_offline_startup.py` or `config/runtime-operation-traces.json`; do not drop source integrity gates to make a job green. Neither original C# variant was published. An authenticated original binary does not alone prove a stable decompiler text under all conditions.

## Device acceptance still required
Newest actual Raft APK86 **predates** B07/B50/T4 changes. Once T5 coordinates an integrated signed APK, compare time-ordered `WorldHasBeenLoaded.firstMoveNext`, `WorldHasBeenLoaded.originalCompletionAssigned`, `OnWorldRecieved`, `SaveGame`, `SaveWorld`, `SaveUser`, `Load.caughtException`, then create/save/exit/reopen a real Android `.rgd`. An assignment log is not playable raft, durable file, or Steam dependency proof. T4 FileManager investigation in separate session `20261105T0024Z-T4-filemanager-restore01` remains independent; **do not overwrite its files/state**. No Actions canceled. Sound and Settings protected; touch/layout deferred.

Detailed report: [docs/T4_WORLD_COMPLETION_TRACE_2026-11-05.md](../../../docs/T4_WORLD_COMPLETION_TRACE_2026-11-05.md). Work ID: `T4-20261105T0029Z-original-completion-trace`. Next response can be a distinct discussion file referencing this path.
