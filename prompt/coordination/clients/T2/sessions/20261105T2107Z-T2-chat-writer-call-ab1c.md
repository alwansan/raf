# T2 source-authentic Foam writer-call type and stack experiment
- session_id: `20261105T2107Z-T2-chat-writer-call-ab1c`
- origin: `chat`
- status: `active`
- base_sha: `4f34b37babfacbdc52527362d9c83c2eade1404a`
- resumed_from_sessions: `20261105T2051Z-T2-chat-cfg-independent-a17f`, `20261105T1736Z-T2-chat-ret-reason-28ce`, `20261105T2017Z-T2-scheduled-retfix-7c3a`
- work_ids: `prompt/coordination/work/WATER-001/T2-20261105T2107Z-T2-chat-writer-call-ab1c.json`
- experiment_key: `sha0a6f0527-foam-retlocal-sole-preceding-call-return-stack-category-v1`
- source pin: immutable ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original managed `Assembly-CSharp.dll` 3,211,776 bytes SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- last proven original: one exact RT returned local `stloc`, immediate previous `call` (CI42078263113) but no typed producer/nullability proof; the synthetic 23/23 CFG CI42107377757 does not read original IL.
- scope: independent original type/operand classification in C# Cecil oracle + synthetic guards + existing T2 source-authentic CI. Avoid scheduled Python CFG files and all other T1/T3/T4/T5 changes.
- intended_files: `android-port/Experiments/T2/FoamRuntimeStringBridge/FoamReturnWriterCallEvidence.cs`, `FoamByrefElementValueOrigin.cs`, `Program.cs`, `.github/workflows/raft-t2-foam-managed-literals.yml`, this session, own work/experiment/event.
- no original symbols/IL/source values are to leave transient CI; no ShaderLab/Unity pixels or device claim.
- current owner phone report: world created/saved/reentered in run 42058825739; water pass and FFT shader errors persist.
- next_step: classify previous call return type, prove only conditional CLR stack producer if branch-entry excluded, execute strict SHA-original and synthetic tests; if CI fails fix before accepting.

## Verified original result, source-only — 2026-11-05T21:15Z
- [Code](https://github.com/alwansan/raf/commit/385e9054775a2000ed30e23d09561e9d6096ce80) implements typed call return category and branch-entry guard. First [CI42110060240](https://github.com/alwansan/raf/actions/runs/42110060240) FAILED before original loading: only diagnostic `CS0136` from source-free Cecil class local name conflict, fixed at [c65e8dd](https://github.com/alwansan/raf/commit/c65e8dddf7b15f12dda8602165ecad8d41720048).
- [CI42110292828](https://github.com/alwansan/raf/actions/runs/42110292828) **COMPLETED SUCCESS** at job `127535742207`: Mono.Cecil build + source-free synthetic void/non-RT/branch-bypass controls passed; checked ZIP2 original `sharedassets0.assets` 115,978,112 bytes and actual original managed DLL 3,211,776 bytes with pin `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- **New exact original finding**: safe log `T2_FOAM_WRITER_PRECEDING_CALL_RETURN_SAFE` reports `declared_return_category=void_return`, `preceding_exact_writer_call=true`, `call_pushes_declared_value=false`, `conditional_stack_top_is_call_result=false`, `alternate_entry_possible=false`, `runtime_or_nonnull_verified=false`. Thus the writer's adjacent `call` cannot itself be the direct stack-producing RenderTexture value; earlier stack contents/duplicated reference require proof.
- No symbol/raw original IL/indices/private small-domain hashes in published evidence. No runtime execution, non-null original RenderTexture, ShaderLab compile/Adreno pixels/device water verified. WATER-001 stays OPEN and game NOT_READY for water fidelity. No audio/Settings/touch/native builds/other workers modified.
- Next independent work: `prompt/coordination/work/WATER-001/T2-20261105T2115Z-chat-precall-operand-4be0.json` scoped to the compiled **void** call operand consumption and immediate precall opcode category. If a retained `dup` can be proven, restrict to conditional CIL stack alias, never non-null.
