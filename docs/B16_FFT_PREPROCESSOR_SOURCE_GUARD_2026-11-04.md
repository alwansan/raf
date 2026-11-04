# B16 — FFT conditional ComputeShader source-gate correction (2026-11-04)

## Proven diagnostic gap

The existing source-only water/FFT preflight stripped comments and strings before identifying `#pragma kernel` and `[numthreads]` entrypoints. It did **not** honor the simplest HLSL conditional preprocessing directives: a clearly inactive `#if 0` could contain a fake kernel and complete function that would be counted as a structurally valid candidate, while Unity itself compiles no kernel from that branch. No game-original data or real shader was needed to demonstrate the structural false-positive.

The code change [0098b585](https://github.com/alwansan/raf/commit/0098b585e3ce9397d04fb838b1980623a64b23d1) extends `scripts/b47_compute_kernel_contract.py` to mask branch text while preserving newlines and the previous pragma/body checks. It selects only literal `#if 0`/`#if 1`, supporting nested conditionals, `#else`, and `#elif` when the branch history is known. Unknown `#ifdef`/`#ifndef`, symbolic expressions and unknown `#elif` mask both possible branches (conservative source-only gate). Missing/misaligned conditionals throw ValueError; they are not interpreted as authenticated compiled kernels. No authored .compute, ShaderLab, original GUID or other game source is edited.

## Reproducible validation

B16 tests [86a55d5](https://github.com/alwansan/raf/commit/86a55d592100052f6ca888c485a08e66df571061) cover disabled pragma/body, active pragma with disabled body, `#if 1`, `#if 0 ... #else`, `#elif 1`, nested branches, duplicate disabled declarations, symbolic/unknown branches, malformed conditional nesting, disguised directives in comments, and the actual `verify_water_render_contract.inspect` call on synthetic temporary Assets/FFT.compute and .meta.

Workflow [e0318a1](https://github.com/alwansan/raf/commit/e0318a101ee477605f63ec3514c4d5a9eb987c3a) (5-minute Ubuntu 24.04 source-only, no LFS/ZIP2/untrusted downloads), command:

```bash
python3 -m unittest -v tests.test_b16_compute_preprocessor_contract tests.test_b47_compute_kernel_contract tests.test_verify_water_render_contract
```

[GitHub Actions 41920741687](https://github.com/alwansan/raf/actions/runs/41920741687): **SUCCESS 34/34**, 12 new B16, 8 existing B47, 14 water render gate synthetic tests, source SHA `e0318a101ee477605f63ec3514c4d5a9eb987c3a`.

An earlier B47 workflow [41920543082](https://github.com/alwansan/raf/actions/runs/41920543082) failed **one historical meta-symlink test expectation**, not a B16 predicate mismatch: its old fixture expected an unsafe linked sidecar to return a normal false report, while the concurrently stricter water metadata guard raised ValueError. This discrepancy was present in the old SHA and the same B47 suite passed in B16's current 34-case integrated run; never mark the earlier red run as green.

## Actual Raft relevance and limits

The source gate is used by `scripts/verify_water_render_contract.py`, but passes **only structural** source checks. The phone APK86 [41812889049](https://github.com/alwansan/raf/actions/runs/41812889049) and [CL 4 November session summary](https://github.com/alwansan/CL/blob/5394407b5cd0a0ca1848ff0902f8d2133bf6ea29/raft%20log/lf/LogRaft-20261104-225757-156/session-summary.json) still show **40,327 ultimate-water invalid pass roots and 5,555 FFT kernel index6 roots**; this source fix has not entered a new Unity/Android build. The original Spectrum 1/6, Foam 1/2 and Blur 1/2 pass deficits and authentic compute identity are independent blockers. No claim of original FFT recovery, Vulkan/SPIR-V pixels, Unity compilation, device success or local world repair.

Next meaningful step: compare authentic ZIP2 `.compute` candidate under actual Unity compile definitions, authenticate each original program/kernel identity and resource binding, then integrate and verify strict gate and device behavior; separate B24/B17/B30 workers own Foam/Spectrum/FFT-program experimental lanes. Preserve owner-working audio and Settings and deferred touch.
