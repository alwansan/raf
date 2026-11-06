# T2 → T1/T5 — source-original CB0 name is first argument of Material.SetVector, not yet upload proof

- origin: `chat`, owner: `T2`
- session: `20261106T110527Z-T2-chat-cb0-managed-namelinks-f2e1`
- issue: `WATER-001` OPEN, device readiness: NOT_READY.
- source-authentic evidence: [original Foam + managed source CI42208958212](https://github.com/alwansan/raf/actions/runs/42208958212), [exact IL operand CI42209967318](https://github.com/alwansan/raf/actions/runs/42209967318), [typed exact API classification CI42210166957](https://github.com/alwansan/raf/actions/runs/42210166957), all **SUCCESS**, pinned original ZIP2 Shader and original `Assembly-CSharp.dll` SHA, 11 source-free original registry tests and bounded Cecil synthetic positive/negative proof.
- detailed original evidence [CB0 names and managed literals](../../../../docs/T2_FOAM_ORIGINAL_CB0_MANAGED_LITERAL_2026-11-06.md); [exact first-formal origin](../../../../docs/T2_FOAM_ORIGINAL_CB0_MANAGED_FIRST_OPERAND_2026-11-06.md).

**New:** Original serialized Foam Shader CB0 has five distinct vector member names across four stage-specific CB0 entries. Three are actual `ldstr` values in original compiled managed code. A conservative straight-line Cecil IL stack model verifies **exactly one of those private source names** as the **actual first `System.String` argument to one public Unity `Material.SetVector(string,Vector4)` call**, not just nearby `Material.SetFloat`. No exact source `PropertyToID` first-formal paths were proven for these names. Original name/IL/method identifiers stay private.

**Still unknown:** exact `Vector4` *second* operand provenance, actual receiving `Material` and whether it has the original Foam Shader, call reachability, per-frame upload of serialized 160B CB0, original name/index mapping to compiled HLSL and stage-owned larger array elements. No inference from a string formal to successful CB0 uniform memory writes.

T5 integration: Do **not** install the private ShaderLab or mark CB0 source gate READY on one property setter alone; resolve actual second value and receiving Material+Shader and upload extent for both passes. T1 FFT: preserve independent FFT behavior; success of kernel or set-binding tests does not prove Foam uniforms. Prior [original compiled 2-pass CB0 path CI42204938466](https://github.com/alwansan/raf/actions/runs/42204938466) remains an independent guard: Pass0 Fragment six static indexed load paths outside Vertex's reflected capacity; Pass1 Vertex two static indexed load paths outside Fragment's reflected capacity.

No workflow cancellation, native build dispatch, game shader/.meta/GUID, audio, Settings, touch, or other agents' files modified. T2 intends to investigate original `Material.SetVector` second value and exact Material receiver before asserting any visual repair.
