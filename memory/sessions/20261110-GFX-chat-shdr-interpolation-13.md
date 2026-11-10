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
