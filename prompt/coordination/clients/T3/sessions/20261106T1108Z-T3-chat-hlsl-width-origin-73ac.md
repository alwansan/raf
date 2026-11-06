# T3 chat — authentic Particle108 output HLSL vs SPIR-V stage linkage boundary

- **session_id:** `20261106T1108Z-T3-chat-hlsl-width-origin-73ac`
- **origin:** `chat`
- **scope:** independently source-verified Particle108 HLSL output field and Vertex/Fragment semantic-link comparison, RENDER-002.
- **base_sha:** `ec6714b57ab1f56ed97cac1019c3cbce8dc6bd74`.
- **resumed_from:** `20261106T1034Z-T3-chat-consumed-width-0c6e`, T3 scheduled `20261106T1026Z-T3-scheduled-91ac`.
- **status:** completed **source-only**. RENDER-002 **OPEN / NOT_READY**. No Android on-device pixels, Unity source shader fix, or APK/XAPK from T3 this cycle.
- [Independent work scope](../../../work/RENDER-002/20261106T1108Z-T3-chat-hlsl-width-origin-73ac.json)
- [Source-authentic experiment](../../../experiments/T3/20261106T1108Z-T3-chat-hlsl-width-origin-73ac.json)
- [CI terminal result](https://github.com/alwansan/raf/actions/runs/42209509708), job `127864903249`, **SUCCESS**.

## Distinct work and ownership

At session start read latest branch HEAD/commits, active CI, current T3 chat and scheduled sessions, the live RESTORE/CHAT_AND_SCHEDULE/PROMPT protocols and current owner evidence boundary. T3 scheduled gate tests operate in `scripts/t3_shader_identity_gate.py`, independent of this original Particle108 private HLSL tool. T1 FFT, T2 Foam, T4 physical mouse/world, T5 integration handled separately. Registered `prompt/coordination/work/RENDER-002/20261106T1108Z-T3-chat-hlsl-width-origin-73ac.json` status active prior to source writes. Only files touched:
- `scripts/t3_particle108_hlsl_output_width_origin.py`: private SPIR-V source and roundtrip reflect/type-name shape, source SPIR-V→generated HLSL exact field name/type, generated HLSL Vertex output and Fragment input semantic/type contract; all public values safe aggregate count-only.
- `tests/test_t3_particle108_hlsl_output_width_origin.py`: 25 source-free positive/negative controls, fail-closed parser, type/multiset vs name proof, duplicate semantics, source-vs-roundtrip reflected names and no private value leakage.
- `.github/workflows/raft-t3-particle108-hlsl-width-origin.yml`: isolated 26-minute SHA-pinned 4-owner/6-scene ZIP2 source experiment on branch `feature/android-native-port`; original bytes and HLSL only ephemeral runner, no artifact upload.
- This session work/experiment/event metadata; no game shader/material/mesh/texture GUID, `.meta`, native Android C#, .rgd, audio, Settings, water/FFT, touch, shared Unity workflows or packaging modified.

Original game source ZIP2 immutable commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; four shader/material owners (269,007,288 verified bytes in staging) and six original scenes SHA-authenticated inside CI. Four original Particle108 VS/FS keyword pairs (eight genuine DXBC stage programs) selected by original serialized metadata, not guessed.

## Verified sequence

Initial [42208384407](https://github.com/alwansan/raf/actions/runs/42208384407) failed early **only** because source-free parser regex had mistakenly doubled backslash escapes; fixed in commit `d355c5ebc11dc93683cbaa8dac63c1cdd3242214`. Then [42208635697](https://github.com/alwansan/raf/actions/runs/42208635697) **success**: 15/15 source-free tests, original SHA verification and four authentic pairs. Probe established 16/16 direct source-SPIR-V-name→generated-HLSL-output-name matches and 16/16 type matches, zero actual named emitted HLSL output widths narrowed/widened; source/HLSL/roundtrip type multisets equal across all four variants despite old same-numeric-SPIR-V-Location narrowing count. This cautions against a blind HLSL width patch.

Extended to actual roundtrip SPIR-V names: [42209056346](https://github.com/alwansan/raf/actions/runs/42209056346) success; 16/16 roundtrip output names exist uniquely, but **0/16 exact matches** to original SPIR-V or HLSL names. Name-only binding to roundtrip SPIR-V is therefore unsafe. Separate queued [42209422936](https://github.com/alwansan/raf/actions/runs/42209422936) automatically superseded by latest pending same-workflow test commit and was cancelled by GitHub pending concurrency; no in-progress run of other T client cancelled manually.

Final [42209509708](https://github.com/alwansan/raf/actions/runs/42209509708) success, job `127864903249`: **25/25 source-free tests** and real original ZIP2 four-owner/six-scene SHA authentic stage probe. New direct regenerated **HLSL Vertex/Fragment semantic link 4/4 compatible**: 16 Vertex user outputs, 14 Fragment user inputs, **0 missing HLSL semantic**, **0 HLSL semantic type mismatch**, **0 parsing/unsupported field**. Original vkd3d source SPIR-V VSFS link 4/4; separate glslangValidator HLSL→SPIR-V roundtrip VSFS link only **2/4**. Source/HLSL/recompiled SPIR-V Vertex output *type multisets* equal **4/4**. This isolates stage-interface drift to **HLSL→SPIR-V recompilation or Location mapping**, not loss of field widths from SPIRV-Cross emitted HLSL. Do not extrapolate to exact original authored DXBC semantic or on-device pixel parity.

## Actionable next work

Evaluate **disposable private paired-stage glslang HLSL linkage** or compiler-specific semantic Location mapping using the paired generated HLSL structs. A 4/4 SPIR-V stage-link result and spirv-val would be necessary but insufficient for Unity shader/Material install or device acceptance. Original DXBC semantic→SPIR-V Location and roundtrip output identity still need explicit evidence. Do not auto-patch Unity resources, fabricate kernel/variant readiness or claim rendering fixed. Scope now released so future T3 scheduled/chat session may pick different files. All team ledger and events preserved.
