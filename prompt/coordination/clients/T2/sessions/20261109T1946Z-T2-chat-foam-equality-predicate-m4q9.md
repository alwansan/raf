# T2 — Foam SHA-original constant-equality predicate study

- session_id: `20261109T1946Z-T2-chat-foam-equality-predicate-m4q9`
- origin: `chat`
- started_utc: `2026-11-09T19:46Z`
- base_sha: `65e7b9c353c07927a63e405aaa8b49cd2a424460`
- resumed_from_sessions: `20261109T1916Z-T2-chat-foam-constant-branch-p8v6`, `20261109T1616Z-T2-scheduled-stage-key-guard-v7q2`
- scope registration: `prompt/coordination/work/WATER-001/20261109T1946Z-T2-chat-foam-equality-predicate-m4q9.json` at commit `9c5969ddfe6c0de41ad0a4990a80f83991e9887b`, BEFORE source edit
- issue: WATER-001 OPEN / full game NOT_READY 0/3
- intended source file: `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs` alone, plus this session/work and own safe evidence
- experiment_key: `T2-original-ZIP2-Foam-pass1-callee-CIL-constant-equality-branch-fold-3211776-no-private-symbols-v1`
- resource_key: `T2-original-FoamBlitOriginalProducers-Cecil-source-only`

## Verified previous evidence

- Genuine pinned-original CIL run [42681948189](https://github.com/alwansan/raf/actions/runs/42681948189), source `cc4e2519`, completed SUCCESS: synthetic and 17 Python checks; original pass0 `not_call_return_source`, original pass1 `value_mixed_with_explicit_null_literal`.
- This is a *conservatively reachable explicit-null CIL producer category*, not proof of null on phone or even a feasible runtime branch. Pass0 source is a typed RenderTexture field and pass1 is a Texture-returning call; actual same-frame RenderTexture object identity is NOT proved.
- At scope registration no in-progress Actions found on feature branch. Separate T1 FFT, T3 shaders, T4 mouse and T5 mini-lab ownership retained. One shared mini-app build [42686652150](https://github.com/alwansan/raf/actions/runs/42686652150) later started by T5; not touched.

## Engineering change

Commit [5b9adfbc](https://github.com/alwansan/raf/commit/5b9adfbc82160f1e8bc6a00713577e7fb3549ed4), preserving the original game and all other team's source, adds bounded exact primitive-equality pruning in the original Foam Cecil interpreter:
- `ceq`, `beq[.s]` and `bne.un[.s]` can prune only proven `literal_i4_zero` == `literal_i4_zero`, `null` == `null`, and proven zero vs nonzero inequality.
- Two `literal_i4_nonzero` categories are intentionally not treated as equal (e.g. 1 vs 2). Joined, runtime/argument-dependent, reference and computed categories still take both potential CFG branches. Other comparisons remain conservative.
- Source-free Mono.Cecil selftests cover both directions of `ceq`, `beq`, `bne.un` and the same-nonzero-class ambiguous negative control. No original IL, shader, symbols or Unity private data published.

## CI pending checkpoint

- Authenticated original source [CI42686782993](https://github.com/alwansan/raf/actions/runs/42686782993), triggered by commit `5b9adfbc`, status **in_progress at first observation**.
- Separate automatic platform workflow [CI42686783004](https://github.com/alwansan/raf/actions/runs/42686783004), status **in_progress at first observation**; no manual dispatch or cancellation.
- The real original DLL and source owner must pass SHA pins, private scratch purge, 17 privacy Python tests, and `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS` before any positive result is recorded.

## Handoff

Check CI final job logs for compilation, bounded selftest and authenticated original pass1 safe `T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW`. If it remains `value_mixed_with_explicit_null_literal`, source-null remains only conservative possibility; next distinct problem is source-private path predicate/receiver and crosspass same-instance RenderTexture proof, not repetitive synthetic-only guards. Do not call shader/device parity, Foam restored, or WATER-001 closed. No Mini/Unity/XAPK requested; T5 handles shared Mini builds and full XAPK vote independently.

## Authenticated completed CI — 2026-11-09T19:49Z

- [CI42686782993](https://github.com/alwansan/raf/actions/runs/42686782993) **COMPLETED SUCCESS**, source SHA `5b9adfbc82160f1e8bc6a00713577e7fb3549ed4`, job `129395615815`.
- Actual log: **17/17 Python OK**; **`T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS`** verifies new `ceq`, `beq`, `bne.un`, false-edge and nonzero-class ambiguity controls. Authentic source: `T2_FOAM_BLIT_SOURCE_SHA_PASS original_dll_bytes=3211776 owner_bytes=115978112 lfs=false`. Private scratch purge and safe finite outputs succeeded.
- Authentic original still yields `T2_FOAM_PASS0_CALLEE_RETURN_VALUE_FLOW not_call_return_source`, `T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW value_mixed_with_explicit_null_literal`. Pass0 source: `RenderTexture typed_field steps=6 void_calls=0`; pass1 source: `Texture typed_call_result steps=21 void_calls=1`.
- Separate [Android platform CI42686783004](https://github.com/alwansan/raf/actions/runs/42686783004) **COMPLETED SUCCESS**, job `129395609766`, no original Foam shader pixels.
- Existing T5 shared mini-app [42686652150](https://github.com/alwansan/raf/actions/runs/42686652150) **COMPLETED SUCCESS**. T2 did not trigger, modify, cancel or duplicate T5's build.
- Safe documentation: `docs/T2_FOAM_ORIGINAL_RETURN_VALUE_FLOW_2026-11-09.md`, commit `026da1730a707b43a56a74ce3a7deda6c7f8c364`.

**Result:** T2 equality predicate control validated on genuine SHA-pinned Foam original; original null-literal category remains conservatively reachable and is **not** a proven runtime null or causal diagnosis. The completed narrow scope is CIL equality feasibility only; WATER-001 remains OPEN / NOT_READY 0/3. Next isolated original experiment should track actual receiver state and object allocation/alias per matched frame, or record an unprovable boundary instead of manufacturing a positive. Do not publish protected source or describe source CI as Android pixel proof.
