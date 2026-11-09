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

## Verified result and real-source boundary (2026-11-09T19:18Z)

- [CI42681948189](https://github.com/alwansan/raf/actions/runs/42681948189) **completed / SUCCESS** on `cc4e2519c35506c4a4a134b2428ee65c11269928`; job `129378522996`.
- 17/17 report/privacy Python tests `OK`; Mono.Cecil C# compilation and `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS`. Both constant `brtrue`/ `brfalse` directions and opaque-input two-branch preservation tested.
- Pinned ZIP2 source authenticated with exact original DLL 3,211,776 bytes and original Shader owner 115,978,112 bytes; `lfs=false`. All original scan, private source purge, and safe artifact publishing steps succeeded.
- Original safe result **unchanged**: `T2_FOAM_PASS0_CALLEE_RETURN_VALUE_FLOW not_call_return_source`; `T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW value_mixed_with_explicit_null_literal`. Pass0 trace still `RenderTexture typed_field` (6 steps); pass1 trace still `Texture typed_call_result` (21 steps with one void call). The path is not removed by pruning simple constant-zero/nonzero CIL `brtrue/brfalse` conditions.
- Authentic finding is **a possible explicit-null producer path in the static callee CFG**, not observed runtime null; it does not establish actual device execution, shader/pixel failure cause, receiver object identity, material sampler/CB0 upload or render parity. WATER-001 **OPEN**.
- Appended latest authenticated result and caveats to `docs/T2_FOAM_ORIGINAL_RETURN_VALUE_FLOW_2026-11-09.md` in commit `7b196a216efe2a00d2f4945bb5743c584d229556`. No game/ShaderLab/.meta or other workers' files modified.

Next distinct engineering question: source-private path predicate and receiver/context correlation (rather than a further source-free null guard). A valid crosspass equality proof must tie pass0 destination and pass1 source to the same actual heap object for a matched frame/lifecycle; raw static return categories cannot do this. Avoid duplicate CI or full XAPK until a materially different experiment/source and T5 gate.

## Final live team observation — 2026-11-09T19:20Z

[CI42681948064](https://github.com/alwansan/raf/actions/runs/42681948064) (platform adapter) also completed SUCCESS, without APK release. T3's separate original smoke34 ShaderLab workflow [CI42681908313](https://github.com/alwansan/raf/actions/runs/42681908313) completed SUCCESS; it is not T2 Foam/device proof. Automatic canonical team-summary [CI42682378346](https://github.com/alwansan/raf/actions/runs/42682378346) still FAILED at missing unique event identity in T3-owned `prompt/coordination/B_TEAM/events/T3/20261106T2007Z-T3-chat-explicit-original-d52e.json`. T2 previously sent its precise owner-scoped handoff under `prompt/coordination/discussions/COORD-001/20261109T1911Z-T2-chat-T3-event-identity-n6q8.md`; do not weaken strict global ledger or edit T3 event. Current Foam work scope completed, broader WATER-001 OPEN.
