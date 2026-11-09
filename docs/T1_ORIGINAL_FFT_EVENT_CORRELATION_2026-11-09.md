# T1 — Original Dx11FFT index-6 event attribution: numeric coincidence vs verified source selector

**Issue:** WATER-001 OPEN; full-game NOT_READY 0/3. **Date:** 2026-11-09. **Source commit:** [b78a2fa719e94974e20e31efa6d9b414223ec3b3](https://github.com/alwansan/raf/commit/b78a2fa719e94974e20e31efa6d9b414223ec3b3). **Source-only CI:** [42692853532](https://github.com/alwansan/raf/actions/runs/42692853532), 28 tests PASSED.

## Why this matters

Authenticated original `Raft/Raft_Data/Managed/Assembly-CSharp.dll` and its decompiled `Dx11FFT` caller have **zero** direct `FindKernel` callsites. The caller uses a direct numeric `Dispatch` argument from observed `Mathf.Log` truncation. The known formula is `((n - 5) << 1) + (bank ? 10 : 0) + pass_offset`, with n in 5..9 for the 20 original source candidates and pass_offset 0/1.

A LogRaft report of **kernel index 6** is not evidence that `Dx11FFT` caused the error, that Unity imported a kernel named for compiled slot6, or that this numeric argument was actually used. A source-compatible hypothetical case is FFTsize256, n8, bank0, pass0; it is not an observed Android attribution.

## Bug in the previous structural correlation

The previous `scripts/t1_fft_original_direct_dispatch_gate.py` returned `same_event_numeric_argument_match_only` whenever untrusted `correlated_event_id` selected a row whose `dispatch_kernel_arg` equaled the reported error number, even if **the row's own `source_numeric_kernel_arg` was inconsistent with the authenticated original selector formula**, the FFT size disagreed with `Mathf` exponent, or compute bindings were absent. Counters disclosed these contradictions elsewhere but the correlation label was misleading.

## Targeted fix

Without changing the evidence JSON schema or any game/mini runtime code, the gate now retains per-event predicates and distinguishes:

1. `unattributed` / `same_event_index_disagreement`.
2. `same_event_number_matches_but_source_selector_mismatch` when numeric source argument and/or actual Dispatch disagree with original formula.
3. `same_event_number_matches_but_source_context_unverified` when the numeric source equation matches but FFT size/exponent or original 20-candidate domain differs.
4. `same_event_number_matches_but_dispatch_preconditions_unverified` when compute shader/support, positive group counts or nonempty bindings are absent.
5. `same_event_numeric_argument_match_only` only when those bounded structural predicates all agree.

New `correlated_event_source_selector_consistent` is purely an **untrusted source-arithmetic predicate**, **not a Unity runtime lookup proof**. The explicit `correlated_event_numerical_match_is_runtime_identity_proof=false` and existing `actual_runtime_trace_independently_attested=false` remain non-negotiable; no original shader or output data is exposed.

## Verified experiment

- Source files: [direct dispatch gate](../scripts/t1_fft_original_direct_dispatch_gate.py) and [adversarial tests](../tests/test_t1_fft_original_direct_dispatch_gate.py).
- [CI 42692853532](https://github.com/alwansan/raf/actions/runs/42692853532) ran **28/28 Python tests PASS**, including 7 new counterexamples: wrong source argument, wrong source exponent, bank mismatch, FFT size/exponent mismatch, unavailable compute, zero groups / empty binding names, clean numeric match with no elevation of original proof.
- Workflow `.github/workflows/raft-t1-original-direct-dispatch-gate.yml` stayed unchanged; it is scoped source-only and explicitly says original `FindKernel` calls zero and mapping unproved.
- No private Unity source, original game assets, raw log lines, non-T1 modules, or build request changed.

**Next:** On an independently authorized same-build full Raft Android test, collect anonymized direct `Dx11FFT` numeric Dispatch metadata, source SHA, APK SHA, session and correlated error call ID; compare actual exponent/size/bank/pass with the source equation. Preserve the option that index6 came from another renderer. This source gate does **not** close WATER-001 or create a need for a Mini/XAPK rebuild.
