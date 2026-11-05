# T2 chat — source-authentic Foam unresolved RT return reason

- session_id: `20261105T1736Z-T2-chat-rt-return-reason-8e2d`, origin: `chat`, owner T2, WATER-001, status active.
- baseline: latest feature HEAD before reservation `665882701002aef024398df0bea8e5fc5fc20849`; work reserved first in `prompt/coordination/work/WATER-001/T2-20261105T1736Z-T2-chat-rt-return-reason-8e2d-ret-reason.json` commit `bc6cdd6fd7cd950847815050b9f1edfb50273a1a`.
- resumed_from_sessions: `20261105T1712Z-T2-chat-return-identity-minimal-4c8f` (original CI42073459459 SUCCESS) and `20261105T1723Z-T2-scheduled-rtcfg-a72e` (independent Python synthetic CFG 8/8 tests PASS, no original DLL).
- last original: ZIP2 SHA-pinned `Assembly-CSharp.dll` 3,211,776 bytes SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`; original typed RT element-returning matched method body has 1 `ret`, 3 branch opcodes, 1 unresolved direct return source; no proof of null/non-null return or runtime device pixels.
- New independent experiment_key: `T2|ZIP2-15964ea8|original-managed-sha0a6f0527|exact-RT-return-unresolved-ret-source-opcode-reason-v1`. Classify exact reason for unresolved return: branch-target/exception entry vs direct ordinary same-block producer class like local/field/arg/etc, only safe enum categories and counters. Do NOT infer actual value at runtime.
- Intended edits limited to T2 Mono.Cecil `FoamByrefElementValueOrigin.cs`, its existing `Program.cs` tests and `raft-t2-foam-managed-literals.yml` workflow. Does not touch scheduled `scripts/t2_rt_return_cfg.py` or its tests, T1/T3/T4/T5 source, game assets, .meta, audio/Settings or deferred touch.
- Next: publish source with expected blob sha guards, verify original SHA CI and safe output; save event, experiment, resource and final handoff. WATER-001 OPEN NOT_READY0/3.

## Concurrent scheduled T2 result and non-overlapping chat pivot

- Scheduled T2 published original return-site source category tests in the same owned C# file at commits `b7b249e532ee` and `d707e1911258`; original [CI42076640591](https://github.com/alwansan/raf/actions/runs/42076640591) and [CI42076713202](https://github.com/alwansan/raf/actions/runs/42076713202) SUCCESS. Its handoff states one sequential original `ldloc` return-site predecessor, not proof of runtime non-null. Scheduled T2 then reserved local-writer dataflow as next scope.
- Because C# source changed during the chat edit, chat did **not** overwrite it or duplicate its source CI. Own initial return-reason work marked `redirected_overlap`. New independent task: synthetic cross-assembly method identity guard in separate project/workflow, no original source or game files.
