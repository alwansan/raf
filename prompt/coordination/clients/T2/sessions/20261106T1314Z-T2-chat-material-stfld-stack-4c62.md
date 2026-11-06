# T2 — chat: original Foam CB0 receiving Material stfld exact value stack provenance

- session_id: `20261106T1314Z-T2-chat-material-stfld-stack-4c62`
- origin: `chat`
- status: `active`
- work: [reserved scope](../../../work/WATER-001/T2-20261106T1314Z-T2-chat-material-stfld-stack-4c62.json)
- registration base_sha: `1ce09e9c248739c788ea2fc40eff358d1da7f112`; scope commit `062421387d483b0a4e89c9099404d337f3ef25e8`
- resumed_from_sessions: `20261106T1306Z-T2-chat-material-field-assignment-8e6a` (original SHA [CI42222313603](https://github.com/alwansan/raf/actions/runs/42222313603) and [CI42222884964](https://github.com/alwansan/raf/actions/runs/42222884964) success), `20261106T122027Z-T2-scheduled-ci-reconcile-a7c2`.
- Original source: ZIP2 pinned `15964ea8f246b6e076ce26b60931ee2e1a9a2385` ; source-original `Raft_Data/sharedassets0.assets` SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; original managed `Assembly-CSharp.dll` 3211776 bytes SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Prior source original one CB0 string `Material.SetVector(string,Vector4)` receiver is one typed Material field; exactly one `stfld` in original managed method, same writer method contains Material ctor but value producer unproven.
- Actions at registration: T5 separate signed APK/OBB ZIP job in progress `42223800025`; no T2 private Cecil or Unity/Foam CI queued/running. Do not cancel/share it.
- hypothesis: bound a conservative single-basic-block stack provenance for the original *exact* `stfld` value, including local storage, `dup`, public typed Material constructor with `Shader` formal, and reaching definitions; fail closed on branching/unsupported opcodes. Distinguish an exact assigned Material(Shader) constructor from mere same-method constructor presence. No claim that Shader formal is original Foam without material source identity.
- intended files: T2-only `android-port/Experiments/T2/FoamCb0ManagedLiterals/MaterialStoreValueTrace.cs`, calling `Program.cs`, isolated T2 workflow plus this own work/experiment/event/session/report. No original game Shader/Meta/GUID, audio, Settings, world, input or other team files.
- run_urls: no new run at registration.
- next_step: code+synthetic rigorous controls, authenticate original CI, record per-typed-origin-only result, explicit NOT_READY for Unity/Adreno water.
