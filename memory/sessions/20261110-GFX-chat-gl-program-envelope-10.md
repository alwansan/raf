# GFX-LAB — 20261110-GFX-chat-gl-program-envelope-10
- session_id: `20261110-GFX-chat-gl-program-envelope-10`; origin=`chat`; resumed_from `20261110-GFX-chat-glsl-embedded-markers-09`
- base_sha: `f28fc520a7f1fc6a8f1673361005ee4481f7b583`
- issue RENDER-002; experiment_key `GFX-MULTI-036`; source ZIP2@`15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- status: IMPLEMENTING
## Scope
Understand whether the original Shader48 compiled blob's actual `ShaderCompilerPlatform` is D3D11 or GL, versus merely carrying 259 unreferenced GL-family typed entries. Classify opaque code-size/framing evidence and compare only private nonempty keyword signatures to authentic linked stages. Do not parse registers without documented layout; no private bytes/labels/IDs in outputs.
## External reference limits
UnityPy `ShaderSubProgram` and AssetStudio both read a typed program and an opaque `m_ProgramCode` byte array and classify some GL types for export as text. They do not establish that *this user's blob* contains an original Android Shader48 Pass or solve the inner GL binary resource-binding format. Independent source metadata and Android/PC parity still needed.
## Negative controls
No speculative t/s/CB offset or stage mapping from adjacency/keyword equality; no source GLSL/HLSL SPIR-V or user assets committed; other branches read-only; originalShaderRestored=false.
## CI
Pending source-private workflow with tests. After result update session, RESTORE, OPEN_WORK, MEMORY, STATE and phase closure gates.

## Implementation and staged CI (2026-11-10)
- New `gfxlab/tools/multi_shader_gl_program_envelope.py` and `gfxlab/tests/test_multi_shader_gl_program_envelope.py`: source compiler platform via public UnityPy enum, GL code size/ASCII ratio/version family, private hash uniqueness, primitive length/known compression headers and nonempty keyword-signature comparisons.
- Independent `.github/workflows/gfxlab-multi-gl-envelope-source.yml` with pinned ZIP2 and `if: always()` source purge. No original shader or private IDs exported; observations are **syntactic-only**, not reliable resource/CB binding.
- Initial [CI42812057156](https://github.com/alwansan/raf/actions/runs/42812057156) failed source-free synthetic unbounded payload test: test inserted oversized content into an unlinked non-GL program not bounded by the first implementation; changed to bound **every** unused program before family filtering.
- [CI42812151086](https://github.com/alwansan/raf/actions/runs/42812151086) unit tests passed, source-private probe reached original and found a `m_Keywords` array not supported by our overly strict comparator. No keyword identity proof was claimed. Updated comparator to return **incomparable** for unsupported/empty/duplicate entries rather than fabricate a normalized identity; protected by new test. Transient [CI42812385346](https://github.com/alwansan/raf/actions/runs/42812385346) reflects interim code/test mismatch.
- [CI42812418402](https://github.com/alwansan/raf/actions/runs/42812418402) source-free tests passed, SHA-pinned source scan **in progress at this checkpoint**. Do not declare runtime shader restored or source platform conclusion before confirmed result.
