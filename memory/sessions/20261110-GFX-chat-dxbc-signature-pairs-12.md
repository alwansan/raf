# GFX-LAB — 20261110-GFX-chat-dxbc-signature-pairs-12
- session_id: `20261110-GFX-chat-dxbc-signature-pairs-12`, origin=`chat`, resumed_from=`20261110-GFX-chat-linked-dxbc-reflection-11`
- base_sha: `f65d38001b34aa2339950698bc18d60975a77bd8`; source ZIP2@`15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- experiment_key: GFX-MULTI-038 / RENDER-002
- status: `IN_PROGRESS`
## Scope
Read the **524 exact keyword/tier pairs** in the original seven Shader48 DX11 Passes, parse bounded original ISGN and OSGN DXBC signature entries (24-byte D3D10 base format), and privately compare output→input semantic/index/type and available masks. Account separately for pixel system-value inputs. Export **aggregate counts only**, no raw semantics/program index/DXBC.
## Evidence limits
Signature *metadata* may help show whether a source pair is compatible, but cannot by itself establish interpolator execution, constant buffer register mappings, correct Material state, Unity shader reconstruction or PC↔Adreno pixel parity. The original shader remains **BLOCKED**.
## Source references
- Microsoft DXBC signature structures, RenderDoc `dxbc_container.cpp` public parser; no private game data in references.
- GFX-MULTI-037 [CI42813380416](https://github.com/alwansan/raf/actions/runs/42813380416) proved 1,275 source-linked DXBC containers have ISGN, OSGN, SHDR only and no RDEF/Debug chunks.
## Run/result
Pending.
