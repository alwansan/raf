# T2 chat — exact original Foam RenderTexture[] byref address consumer

- session_id: `20261105T1509Z-T2-chat-original-byref-sink-a83c`, origin: `chat`, issue: `WATER-001`, status: `active`.
- base_sha: `a0edf06a3ea50b61c302d468f5a1e1910bd93cdc`.
- resumed_from_sessions: `20261105T1442Z-T2-chat-foam-field-reads-c8d1`, `20261105T1434Z-T2-chat-rendertexture-serialization-93ad`.
- prior source-authentic [CI42047763379](https://github.com/alwansan/raf/actions/runs/42047763379) SUCCESS, exact Foam private RenderTexture[] field had one `ldflda` outside getter and eight non-getter reads; no runtime or array allocation proven.
- work pre-registered first: `prompt/coordination/work/WATER-001/T2-20261105T1509Z-T2-chat-original-byref-sink-a83c-address-consumer.json`, commit `c491f76077edcf7984cb5de95101edc1aafb000d`.
- experiment_key: `T2|ZIP2-sha15964ea8|manageddll-sha0a6f0527|exact-foam-RenderTexture-array-ldflda-consumer|bounded-source-only-v1`.
- hypothesis: strictly classify whether original one `ldflda` address is consumed as a typed byref method argument, direct indirect store/clear/read or unsupported/unknown. Branch-sensitive fail closed; never publish actual original method/field/type identifiers, IL, or caller int constants. Even a byref call is *potential* mutation, not proof of write or runtime execution.
- intended files: own `FoamFieldAddressConsumer.cs`, `Program.cs`, `.github/workflows/raft-t2-foam-managed-literals.yml`, work/session/experiment. No scene, original game code, shader/FX, audio, Settings, deferred touch.
- coordination: at preflight no in-progress/queued Actions; T4 event missing id schema was fixed by `e027d6a81b`, subsequent [T1 ledger refresh CI42049042381](https://github.com/alwansan/raf/actions/runs/42049042381) SUCCESS. No overlapping T2 scheduled Cecil job.
- next_step: implement bounded source-only Cecil tag flow and discriminating synthetic fixtures; run original SHA-pinned CI and inspect privacy-safe result; save distinct evidence/limits and next concrete integration gate. WATER-001 OPEN NOT_READY0/3.

## Source commit and CI checkpoint

- Published [commit 34f840561993b44c59cd7c61b22f1f013e64cd89](https://github.com/alwansan/raf/commit/34f840561993b44c59cd7c61b22f1f013e64cd89) on refreshed HEAD by expected SHA fast-forward after another agent's concurrent update; no force or files from other clients overwritten.
- Own files: `FoamFieldAddressConsumer.cs` new, `Program.cs` and own `.github/workflows/raft-t2-foam-managed-literals.yml`. Synthetic fixtures distinguish direct `stind.ref`, typed byref call, `ldind.ref`→array element write, `ldind.ref`→array length read, and equal-typed different-field decoy. Unsupported opcode/branch returns explicit unresolved category; never emit original symbols, IL, names, original indices or small-domain hashes.
- Original SHA-pinned [CI42053062181](https://github.com/alwansan/raf/actions/runs/42053062181) `in_progress` at checkpoint. Work `waiting_ci`; no original byref sink claim until successful CI and safe JSON read.
- Separately running [T3 original Shader48 translation CI42052605123](https://github.com/alwansan/raf/actions/runs/42052605123) and [T5 full native package build42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) have separate resource/workflow ownership and were neither cancelled nor changed.
