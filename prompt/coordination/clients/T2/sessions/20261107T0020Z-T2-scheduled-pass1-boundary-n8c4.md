# T2 — scheduled Foam pass1 producer boundary review

- session_id: `20261107T0020Z-T2-scheduled-pass1-boundary-n8c4`
- origin: scheduled
- issue_id: WATER-001
- status: completed (review only; no new shader fix)
- base_sha: `80302ef52d2a3766e46f5e4cd9e473ca699bf284`
- work registration commit: `f52f3a111b95060b5f53d31bb0146fffd981598b`
- resumed_from: `20261106T2250Z-T2-chat-foam-blit-pass-role-83f4`, `20261106T2320Z-T2-scheduled-summary-gate-c8f1`, and `20261107T2227Z-T2-chat-blit-texture-role-6c52` (its UTC date in the filename differs from its recorded 2026-11-06T22:27Z creation timestamp).

## Owner/device evidence read first

`docs/DEVICE_FEEDBACK_42058825739_AR.md` documents owner-entered/saved/reopened world from artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) on POCO F5 Pro, while release publishing failed. CL pinned `520c4cf409aa20a4db54ff80ed87d8807d9cba57` and images show white raft/effects; session 220911-559 has 23,884 water pass errors and 3,850 FFT kernel errors. Do not regress to APK86 narrative or equate device log counts to a new source-only shader proof. Physical mouse belongs to T4, Resolution and three buttons to T5; general touch layout deferred.

## Current exact result and engineering interpretation

Original-source [42308583977](https://github.com/alwansan/raf/actions/runs/42308583977) PASS at `4e5f4d24` with 65/65 safe-report tests and pinned source. Two original Foam Material-field Blit sites are proven with explicit pass selectors. Pass0: direct typed RenderTexture source **and** destination. Pass1: both producer classifications **unknown**. This is **not** a missing-texture finding; the parser intentionally refuses noncanonical IL. Prior [42305522855](https://github.com/alwansan/raf/actions/runs/42305522855) lacked per-site correlation, now superseded for this exact question.

The next experiment must distinguish three disjoint outcomes for pass1: (a) bounded backward slice resolves a typed source/destination; (b) slice terminates at a call/branch/field with type known but runtime identity unknown; (c) branch merge or side effect makes static proof unsafe. Required fail-closed controls: reject ambiguous stack merges, exception handler entry, multiple assignments, unknown call side effects and pass selector drift; report only category counts and original pinned SHA, never field names or IL. A successful scan still cannot prove allocation, texture pixels, CB0 upload or Adreno output. Avoid repeating pass0/pass1 literal and direct-type census with unchanged input.

## Coordination and current limitation

The current chat-owned T2 work already modified `android-port/Experiments/T2/FoamShaderFindResultFlow/Program.cs`, `scripts/t2_foam_shaderfind_return_report.py`, and `tests/test_t2_foam_shaderfind_return_report.py`; this scheduled review deliberately did **not** edit those files or start an equivalent CI. No Unity/native request, game shader, asset, .meta/GUID, audio, Settings, touch, release or other worker state was modified. The latest team summary [42308935364](https://github.com/alwansan/raf/actions/runs/42308935364) failed on a T3 event identity gate, not Foam compile; T3 owns that event. The current T2 vote stays `لا يحتاج` until a substantial integrated rendering patch.

This cycle produced a bounded next-test specification and refreshed source/CI reconciliation, **not a new original-data experiment or a rendering fix**. The pass1 chain remains open; no safe independent implementation was completed without overlapping active chat-owned scanner files. WATER-001 OPEN, NOT_READY.

## Next step

On live HEAD, inspect the active T2 chat scanner ownership and implement the isolated pass1 backward-slice in nonoverlapping files only if no equivalent run exists. Use authenticated ZIP2 managed DLL and private scratch; verify adversarial controls before a single original-data CI. Then bind both Foam ShaderLab passes to original Unity Material/CB0 and coordinate actual Unity/device evidence with T1/T3/T5.
