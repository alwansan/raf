# B07 LOCAL-005 — original world coroutine first MoveNext trace (4 November 2026)

Session `20261104T2242Z-B07-c7ea`; resumed B07's prior `20261104T2112Z-B07-6e51` callback instrumentation. Scope: a safe Android-only diagnostic of whether the original `Raft_Network.WorldHasBeenLoaded()` iterator **actually begins executing** (its first `MoveNext`), not merely whether an `IEnumerator` was constructed.

## Source integration and trust boundary

- Original provider `alwansan/raf:zip2` pinned at `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original `Raft_Network.cs` normalized SHA-256 `080035c137e446828226ed84a23190656b6f235d274436cafb477feaf93caa03`, original `WorldHasBeenLoaded` method-body SHA-256 `cbd74c24f1c6a86dd50e8d320f4f4142f5b3f3fc5bf8f64ded04710c30c3a140`, original managed DLL 3211776 bytes SHA-256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- New [B07 source helper](../scripts/b07_world_coroutine_trace.py) rejects unknown original source SHA, method/body drift, wrong return type, absent real `yield`, preprocessor condition in the original body, and duplicate application. It adds exactly one `#if UNITY_ANDROID && !UNITY_EDITOR` `AndroidRuntimeLog.Write("world","WorldHasBeenLoaded.firstMoveNext",...)` at the beginning of the method body, preserving every original byte after that point.
- Wired via [offline original-source adapter](../scripts/adapt_android_offline_startup.py), which is used by the Android project staging. The helper is invoked only after the adapter's original source SHA gate. No callback body rewrite, `yield` reordering, injected catch around a yield, fake `WorldHasBeenRecieved`, network or Steam behavior change, `.rgd` schema change, sound/Settings/input, shader or resource change.
- This event marks **the first iterator step only**. It does not attest that subsequent awaits complete, scene loading succeeds, saving succeeds, a game becomes playable, or a flag is true. Separate B07 `GameManager.OnWorldRecieved` operation Begin/End/exception instrumentation remains the next boundary to compare.

## Verified bounded evidence

[CI41929041686](https://github.com/alwansan/raf/actions/runs/41929041686) / job `126920934945` **COMPLETED SUCCESS**, on workflow source `d5c3b1feabe255d66acd4b17e3e3efd1b59b5991`:

- Python unit tests: **9/9** B07 original-free negative controls, **19/19** existing offline startup regression tests, all PASS.
- Real managed .NET 10 synthetic iterator runtime: Android compile `yields=2 exceptionRethrown=true entries=1`; non-Android compile `yields=2 exceptionRethrown=true entries=0`. Both preserve first-step laziness, ordered yields and exception propagation. No decompiled source in the fixture.
- Private ILSpy 11.2.0.10050 decompilation of the SHA-checked original managed DLL, original `Raft_Network` source/body preservation after adding B07 probe, and production offline adapter invocation with exactly one resulting operation marker: PASS. Raw original code, ILSpy output, binary assets and secrets were not published.

Initial B07 source callback proof remains [CI41916347469](https://github.com/alwansan/raf/actions/runs/41916347469), distinct from this iterator boundary.

## Remaining blockers and next test

The latest authentic Android game test remains `android-early-test-41812889049-1` (APK86, immutable source `d181ee7152580f49ee0b41dfd05fa2bfdacfafe5`); latest CL `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`. New B07/B50/B24 fixes are **not** established as installed-device behavior. LOCAL-005 stays OPEN; WATER-001 and RENDER-002 stay OPEN; readiness NOT_READY with 0/3 independent full reviews. The next coordinated native game trial should capture `WorldHasBeenLoaded.firstMoveNext`, `OnWorldRecieved` begin/end/errors, real host/Steam error stack and actual world create/save/exit/reload `.rgd` result. If the coroutine never enters, trace caller/StartCoroutine; if it enters but callback fails, inspect original exception path. Do not mask the UI, forge success, run duplicate native jobs or claim full release acceptance.
