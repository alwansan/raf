# T2 chat — SHA-original Foam pass1 constant branch feasibility

- session_id: `20261109T1916Z-T2-chat-foam-constant-branch-p8v6`
- origin: `chat`
- started_utc: `2026-11-09T19:16Z`
- base_sha: `abf1ede6bbea3b9073c9ab20b826be46dd486c93`
- resumed_from_sessions: `20261109T1905Z-T2-chat-foam-null-branch-r7k3`, `20261109T1909Z-T2-chat-event-ledger-repair-n6q8`
- work registration: `prompt/coordination/work/WATER-001/20261109T1916Z-T2-chat-foam-constant-branch-p8v6.json`, commit `22345302645a7260a464f2d36c70556b8078480c` **before source edit**.
- issue: `WATER-001` OPEN / full game NOT_READY 0/3.

## Baseline recovered

Original SHA-pinned [CI42680030121](https://github.com/alwansan/raf/actions/runs/42680030121) verified `T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW value_mixed_with_explicit_null_literal`: at least one conservatively reachable source IL return carried `ldnull`, but the preexisting interpreter explored both sides even when a condition was an actual literal constant. Original pass0 direct source typed RenderTexture field, pass1 typed Texture call result; crosspass identity unproven. T1 FFT, T3 shader, T4 mouse and T5 delivery active on distinct paths. No prior equivalent current T2 CID predicate run active.

## New original hypothesis / source edit

Commit `cc4e2519c35506c4a4a134b2428ee65c11269928` edits only `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs`. The Cecil value interpreter now retains `literal_i4_zero` and `literal_i4_nonzero` abstract stack values from genuine `ldc.i4` and tracks the operand consumed by `brtrue[.s]` and `brfalse[.s]`. It prunes the impossible branch only for exactly known scalar literal zero/nonzero/null; all unknown branch inputs, other conditional comparisons, and switch keep both paths conservatively. This is a static-CIL feasibility filter, NOT device runtime predicate inference. It preserves prior category unions and existing finite report tags.

Synthetic selftests now use a **parameter** instead of `ldc.i4.1` when asserting both paths are reachable, and include positive/negative tests for constant 0/nonzero under both true- and false-jump conditions, alongside prior shared-return phi and exceptional path rejects. No original source, private IL, field names, shader stage code, .meta or app package published.

## CI checkpoint and continuation

Path-filter triggered existing authenticated-original C# workflow automatically:
- [CI42681948189](https://github.com/alwansan/raf/actions/runs/42681948189) source `cc4e2519` — **in_progress on initial check**.
- [CI42681948064](https://github.com/alwansan/raf/actions/runs/42681948064) platform adapter auto-trigger unrelated; no manual dispatch or cancellation.

Check final run, `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS`, authenticated original DLL size 3211776 and Shader owner bytes 115978112, and `T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW` before claiming result. If original tag changes, record it precisely, distinguishing **static possible** from **known feasible/necessary** and remember a conditional branch with input-dependent values remains indeterminate. Verify cleanup and absence of private details in artifact. If failed, inspect job logs and correct own source without repeating unchanged workflows.

Broader WATER-001 open: no proof of actual pass0 destination == pass1 source instance, CB0 upload, ShaderLab installed or Android water pixels. No Mini/Unity/XAPK requested.
