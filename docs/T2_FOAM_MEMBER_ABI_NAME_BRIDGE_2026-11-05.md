# T2 WATER-001 — authenticated original Foam member indices and compiled CB name gap

## Provenance and actual execution

T2 (session `20261104T2354Z-T2-foamabi01`) continues **B20/B24/B25**'s authentic two-pass/four-stage Foam source recovery and B09/B17 Spectrum and B45 Blur evidence without replacing their attribution. This is a *source/translation ABI diagnosis*, **not** a game shader or phone pixel fix.

- Original data provider: `zip2` commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, reconstructed `Raft_Data/sharedassets0.assets`, 115,978,112 bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3` (checked via pinned manifest, no LFS).
- Original Shader PathID **2420**, raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`. B20 private packet stages four genuine translated GPU programs; no raw shaders or names are published.
- Initial genuinely authenticated CI [41937996942](https://github.com/alwansan/raf/actions/runs/41937996942), source commit [18a94534](https://github.com/alwansan/raf/commit/18a94534b0f03262e2416b5ce058af9058aa3c2e): **SUCCESS**, 15/15 adversarial tests, original owner verified, B20 4 stages and exact eight CB links checked. Artifact `13373574557`, transport ZIP SHA256 `5c62be9eae62fcd13dad756b82afb821f3715fdcb891822a45cbcffde12a4dfc`.
- Additional authentic name comparison [41938551022](https://github.com/alwansan/raf/actions/runs/41938551022), source commit [bed03ac4](https://github.com/alwansan/raf/commit/bed03ac405a628396f12e9ad1ecd5dcc5b690820): **SUCCESS**, 15/15 existing tests and authentic private source/SPIR-V reflection. Aggregate-only artifact `13375515862`, ZIP SHA256 `d3062e46fb6d7a837e4de5e36d9f0b5b6e28e58423e0be29be1d3dd17aebb3fa`. Read artifact directly and verify ZIP transport digest.
- Added targeted source-free name equality/parser negative controls in [c472f0dd](https://github.com/alwansan/raf/commit/c472f0dd41afe018302572b8ab899ed24434856c), follow-up source-authentic workflow [41938898381](https://github.com/alwansan/raf/actions/runs/41938898381), **result pending at drafting**; do not call it passed until confirmed.
- Original latest released game [APK86](https://github.com/alwansan/raf/releases/tag/android-early-test-41812889049-1) predates T2 and B20 source evidence; CL original log HEAD `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`. Device game behavior has not been retested with current source.

## Original numeric member and identity findings

The new `scripts/t2_foam_member_abi.py` deliberately interprets original `m_VectorParams[].m_Index` and `m_MatrixParams[].m_Index` as **numeric source indices**, not proven byte offsets. It independently reads SPIR-V `types[*].members[*].offset` as reflected **byte offsets** and avoids inventing a source-to-SPIR-V member identity. For the eight original CB pass/stage/slot bindings, `spirv-cross` shows **one reflected member in each bound UBO**; source contains one or two vector entries or one matrix entry depending on pass and stage. Only **2/8** CB links have any naive index×16 candidate overlap with reflected member offsets; this overlap has no semantic or upload meaning until source units and member identity are proven.

| Original pass / stage / slot | Source partial CB bytes | SPIR-V reflected block bytes | Original source members | Candidate intersection |
| --- | ---: | ---: | --- | ---: |
| 0 / vertex / b0 | 160 | 96 | 2 vectors | 0 |
| 0 / vertex / b1 | 176 | 64 | 1 matrix | 1 |
| 0 / vertex / b2 | 368 | 336 | 1 matrix | 0 |
| 0 / fragment / b0 | 160 | 128 | 2 vectors | 0 |
| 1 / vertex / b0 | 160 | 160 | 1 vector | 0 |
| 1 / vertex / b1 | 176 | 64 | 1 matrix | 1 |
| 1 / vertex / b2 | 368 | 336 | 1 matrix | 0 |
| 1 / fragment / b0 | 160 | 112 | 1 vector | 0 |

One source `m_Size` equals reflected block size; seven differ. The size mismatch previously observed by B20 must **not** be repaired by padding or claimed as corrupted original data.

T2 separately compared exact **private** original registry CB names, generated HLSL `cbuffer ... : register(bN)` names, and reflected SPIR-V names at the same authenticated numeric b-register. Result:

- **0/8** original CB names equal generated HLSL names.
- **8/8** generated HLSL names equal reflected SPIR-V names.
- **4/8** original CB names are valid lexical HLSL identifiers; the remaining 4 are opaque and unusable literally.
- No original symbol, translated HLSL, object bytes or raw shader is written to source commits, outputs or logs. Published aggregates are booleans, slots, counts and known sizes.

This proves a **name bridge gap for all eight links**, even where the original name happens to be syntactically valid, but not that the runtime is necessarily broken by name mismatch; `b0`/register mapping and Unity property upload semantics require separate evidence. The correct next action is to establish original CB member type/offset and Unity upload binding on an authenticated material/ShaderLab reconstruction; **do not** silently rename every CB to an invented alias.

## Integration and remaining proof

The bounded original-data checker, adversarial tests and isolated workflow are source-integrated, with private staging deleted before safe artifact upload. Neither the actual exported original ShaderLab nor `.meta`/GUID ownership, materials, sampler or render target state, Unity Editor compile, device GPU pixels, FFT kernel mapping, local world and `.rgd` were modified or proven by T2. Sound/Settings remain untouched and touch/layout deferred.

**WATER-001 OPEN; Android game NOT_READY (0/3 full readiness reviews)**. Continue by linking original CB parameter schema to translated active member usage and authentic Unity upload alias; then construct a real private two-pass Foam ShaderLab with verified render/sampler states, import in Unity and compare output. Spectrum seven-pass and Blur staged sources and T1 FFT remain independent required work.
