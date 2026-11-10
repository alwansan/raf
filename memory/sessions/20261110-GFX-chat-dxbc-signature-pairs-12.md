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

## Terminal result — 2026-11-10
- GFX-MULTI-038 [CI42814767180](https://github.com/alwansan/raf/actions/runs/42814767180) **SUCCESS /238 Python tests**, original ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Original Shader48 7 Passes, **524/524 exact stage pairs** metadata-compatible for ordinary (non-system) interpolator signatures; **3,516/3,516 ordinary fragment input entries** matched source VS OSGN name+index/type/available component mask, **0 missing, 0 type mismatches, 0 mask gaps, 0 ambiguous**. **512/524** pairs have ordinary varyings; remaining 12 have only system inputs (so matching ordinary inputs is vacuous for those pairs). **620** pixel system-value input records handled separately, not counted as proved pipeline/rasterizer interpolation. 464 distinct VS and 472 PS programs from matched pairs inspected; source compiler still D3D11. 7 source pass pair counts [80,156,32,80,40,120,16]. Source cleanup PASS. **NO** original material→t/s/CB binding, interpolation/rasterizer correctness, original Unity Android GLES shader, or PC↔Adreno pixel parity. Safe aggregate `gfxlab/evidence/20261110_gfx038_dxbc_signature_safe_counts.json`; CI artifact [13762474824](https://github.com/alwansan/raf/actions/runs/42814767180/artifacts/13762474824) expires 2026-11-17T12:20:11Z.
- Tool `gfxlab/tools/multi_shader_dxbc_signature_pairs.py`, tests `gfxlab/tests/test_multi_shader_dxbc_signature_pairs.py`, workflow `.github/workflows/gfxlab-multi-dxbc-signature-pairs.yml`.
- **Interpretation**: metadata-only stage pair integrity confirmed for ordinary varyings, NOT actual shader restoration; pixel system inputs and interpolation flags are not proven solely from ISGN/OSGN. No source shader bytes, semantic names, registers or user assets committed.
- Next `GFX-MULTI-039` could independently audit authentic SHDR tokenized-stage input declarations/interpolation modes and resource declaration presence **without inventing register mappings**. Existing GFX-MULTI-016 examined a representative pair only; avoid duplicating GFX-MULTI-013 all seven offline representative passes.
