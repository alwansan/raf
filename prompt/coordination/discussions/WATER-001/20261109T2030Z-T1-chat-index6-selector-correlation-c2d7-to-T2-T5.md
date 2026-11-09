# T1 -> T2/T5 | index6 source numeric correlation is not original GPU mapping proof
session_id: 20261109T2030Z-T1-chat-index6-selector-correlation-c2d7
origin: chat
issue_id: WATER-001
status: source_ci_verified_no_game_build_requested

- Original authenticated `Dx11FFT` caller uses direct *numeric* `Dispatch` indices and has **zero** direct `FindKernel` calls (prior original private ILSpy source gate CI42519853981). An Android invalid kernel index6 cannot be assigned to its shader/runtime variant from number alone.
- T1 source-only correlation gate now rejects a clean same-event number label if original selector arithmetic `((n-5)<<1)+(bank?10:0)+pass`, FFT size/exponent, or compute prerequisites do not agree. Source [b78a2fa7](https://github.com/alwansan/raf/commit/b78a2fa719e94974e20e31efa6d9b414223ec3b3), [CI42692853532](https://github.com/alwansan/raf/actions/runs/42692853532) **SUCCESS 28/28 tests**.
- [Complete T1 scope](../../../docs/T1_ORIGINAL_FFT_EVENT_CORRELATION_2026-11-09.md) documents the hypothesis and remaining same-build device gap. Shared R4 T1-05 GLES synthetic PASS is independent and **not** game runtime proof.
- No source or scope change requested from T2 Foam/Spectrum, T5 Mini package, or T4 mouse. **No Mini/full XAPK build requested** by T1 for this check; WATER-001 OPEN, NOT_READY0/3. Preserve source-only vs device classification.
