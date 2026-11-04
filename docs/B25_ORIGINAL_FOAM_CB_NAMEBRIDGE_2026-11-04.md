# B25 — authenticated original Foam/Global constant-buffer name/slot bridge (2026-11-04)

## Source and scope
P0 WATER-001. Complementary to [B24's original four-stage DXBC translation](B24_ORIGINAL_FOAM_PROGRAM_TRANSLATION_2026-11-04.md) and [B25's identical genuine render-state proof](B25_ORIGINAL_FOAM_RENDER_STATE_2026-11-04.md). Original ZIP2 input fixed at `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, owner `Raft_Data/sharedassets0.assets` exactly **115978112 bytes**, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, original Shader object PathID **2420**, raw object SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.

B25's `scripts/b25_foam_cb_namebridge.py` privately reads each original Foam pass `m_NameIndices` and the source-pinned B24 `m_ConstantBuffers`/`m_ConstantBufferBindings` stage layouts, checks original name-index/register equality, emits only SHA256 commitments and numeric source counts, **never names, raw shader programs, HLSL, or original assets**. No original game files, .meta/GUIDs, shaders, Unity or Android were modified.

## Verified immutable original result

[Final B25 workflow 41928183838](https://github.com/alwansan/raf/actions/runs/41928183838), source `afc9a403db9e0c8db08bda9b7fd8df3b91a580ea`, **COMPLETED SUCCESS** on exact original ZIP2/SHA object, with **26/26 synthetic tests** (11 state + 15 CB name bridge). Real Foam contains two passes and four original stage programs, with **eight original CB name-index→register associations**: vertex CB slots 0/1/2 and fragment CB slot 0 in EACH pass. Original property-name table contains 14 records for pass0, 8 for pass1.

| Original CB slot | Original name SHA256 | Partial CB size | Verified source-role |
| --- | --- | ---: | --- |
| 0 | `812aa05b293f131a08f99707b3f8979993ac2a19acfce16a94d6da67cc993d06` | 160 B | Vertex and fragment in both passes; 4 original references require an **authenticated alias** because true source name is not a literal HLSL identifier. CB0 vector members 2 in pass0, 1 in pass1. |
| 1 | `ea1518ee9277b12e444777ac75092b0525855de7c2dc06cd8b842ed446c74acd` | 176 B | Both vertex passes; 1 matrix member; literal name grammar admissible, runtime descriptor/upload NOT verified. |
| 2 | `8cf6b4d3f239bcc59e67194ae749f6532862116484d759a7a5fe209ea34fafe4` | 368 B | Both vertex passes; 1 matrix member; literal name grammar admissible, runtime descriptor/upload NOT verified. |

All three source CB name/slot identities are stable across both original passes; the original pass0/pass1 CB0 *member counts* differ and must stay different. Original render-state fragments are independently identical at 247B/SHA256 `19b4753ccc0393a8ebe4f804aded5e5c8363d9b641cac1870d2d6d0c73b50170`. None of this licenses merging original programs.

## Rejected assumptions, retained failures
- [41927469783](https://github.com/alwansan/raf/actions/runs/41927469783) initially failed original registry check after 24/24 synthetic tests: overstrict assumption every `m_NameIndices` entry is an HLSL identifier.
- [41927610381](https://github.com/alwansan/raf/actions/runs/41927610381) and [41927765070](https://github.com/alwansan/raf/actions/runs/41927765070) bounded original schema: pass0 registry 14 (name, index) tuples, first name not a direct identifier; no raw names logged.
- [41928029023](https://github.com/alwansan/raf/actions/runs/41928029023): 26 synthetic passed, but even original **referenced CB0** symbol cannot appear unchanged as direct HLSL identifier.
- Rejected further assumption that CB0 can be directly rewritten to guessed CBuffer identifier. Corrected version **preserves original opaque symbol by SHA and slot** and explicitly reports `requires_verified_shaderlab_alias=true`. Final CI 41928183838 succeeded without fabricating aliases.
- Intermediate test fixture attempts (41927922827/41927971807/41927997556/41928160127) failed on evolving control-character fixtures; final 26/26 tests cover the intended behavior.

## Next barrier — not solved
Private original DXBC/SPIR-V reflection must match CB0 opaque symbol to genuine descriptor/slot, permit only a validated HLSL alias preserving register/CB layout and numeric behavior. Then assemble two true ShaderLab passes with original four stage programs, texture/sampler bindings, same-export Material/GUID lineage and actual Unity+Android import/render tests. **No ShaderLab installed, no GPU/Adreno/device proof, no game APK**. WATER-001, RENDER-002, LOCAL-005 OPEN, NOT_READY 0/3. Audio and Settings unchanged; touch/layout deferred; no Unity/native build requested.

Reproduce `python3 -m unittest discover -s tests -p test_b25_foam_cb_namebridge.py -v` and `python3 -m unittest discover -s tests -p test_b25_foam_pass_state.py -v`; pinned workflow `.github/workflows/raft-b25-foam-pass-state.yml` stages original content privately and uploads SHA/count-only aggregate.
