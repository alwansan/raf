# GFX-LAB — 20261110-GFX-chat-shdr-interpolation-13
- session_id: `20261110-GFX-chat-shdr-interpolation-13`; origin=`chat`; resumed_from=`20261110-GFX-chat-dxbc-signature-pairs-12`; base_sha=`17b2b439690f0a692e0e4d2abbcd347e057a71c1`
- experiment_key: GFX-MULTI-039 / issue RENDER-002
- Source ZIP2 SHA: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- status: IN_PROGRESS
## Scope
Examine **all 1,275 unique linked DX11 Shader48 SHDR programs** (620 VS + 655 PS) from 1,435 authentic original stage-variant links. Classify D3D10 tokenized program `DCL_INPUT_PS` and `DCL_INPUT_PS_SIV` [14:11] interpolation enum 0–7, system generated input separately, and count resource/CB/sampler declarations without publishing proprietary source bytecode/register/keyword identity. Earlier GFX-MULTI-016 examined a representative pair per Pass only, so this is full coverage.
## Material / pixel blockers
All 524 exact ISGN/OSGN pairs were metadata-compatible [CI42814767180](https://github.com/alwansan/raf/actions/runs/42814767180), but interpolation qualifiers, resource binding and runtime GPU tests are distinct. Never claim Shader48 restored based on source declaration counts.
## CI
Pending.

## GFX-MULTI-039 terminal verified (2026-11-10)
- GFX-MULTI-039 [CI42815863927](https://github.com/alwansan/raf/actions/runs/42815863927) **SUCCESS /245 Python tests**; source ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, all **1,275 authentic linked DX11 SHDR** programs parsed (620 Vertex /655 Pixel), across 1,435 links and 524 exact original pairs. Source pixel interpolation declarations total **3,497** = **linear 3,405**, **constant 76**, **linear_noperspective 16**, other modes 0. Of 3,497, 3,481 `DCL_INPUT_PS` ordinary and 16 `DCL_INPUT_PS_SIV`; no generated `DCL_INPUT_PS_SGV`. Distinct source program resource declarations: Vertex constant buffers 3,168, Pixel constant buffers 2,556, Pixel resource declarations 3,247, Pixel sampler declarations 3,095. These count **declarations across distinct programs** and **not** unique material properties/register identities or pixel-runtime events. Source private purge PASS; safe aggregate `gfxlab/evidence/20261110_gfx039_shdr_interpolation_safe_counts.json`, [artifact 13763899734](https://github.com/alwansan/raf/actions/runs/42815863927/artifacts/13763899734) expires 2026-11-17T12:27:52Z. **Original Shader48 Android still false**, CB/material binding absent, GLES compilation/PC pixel parity not proven.
- Original instruction mode bytes [14:11] parsed from public DirectX-Headers D3D10 tokenized format, `DCL_INPUT_PS`=98, `DCL_INPUT_PS_SIV`=100; `DCL_INPUT_PS_SGV`=99 counted separately. No private interpolation identifiers/values other than public aggregate class names exported. Existing GFX-MULTI-016 representative declarations expanded to all 1,275 linked stages.
- Source-only next step: `GFX-MULTI-040` seek **authoritative original material/CB binding evidence**, or if not available, create a bounded reproducible PC shader/RenderDoc capture guide and compact synthetic-only Android interpolation probe. Avoid repeated source audits without an authentic Material→GPU register link.
- Current status `SOURCE_INTERPOLATION_DECLARATIONS_COMPLETE; ORIGINAL_SHADER48_RUNTIME_BLOCKED`, no APK requested or built.
