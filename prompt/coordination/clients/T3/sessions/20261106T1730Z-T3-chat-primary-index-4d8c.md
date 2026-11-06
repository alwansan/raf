# T3 chat — Particle108 authentic DXBC primary register differential

- **session_id:** `20261106T1730Z-T3-chat-primary-index-4d8c`, **origin:** chat, owner T3; issue RENDER-002 **OPEN / NOT_READY**.
- **resumed_from_sessions:** `20261106T1721Z-T3-chat-dxbc-operands-6e2a` and `20261106T1710Z-T3-chat-shdr-declarations-3c7e`.
- **base_sha:** `1a5170e8bccb64d4f88bf30dc5013f1dd363347b`; scope reserved BEFORE editing at `prompt/coordination/work/RENDER-002/20261106T1730Z-T3-chat-primary-index-4d8c.json` commit `697787bd3f9e582deda2f5dbe09ffe2b0456bd31`.
- **experiment_key:** `T3-ZIP2-15964-Particle108-8stage-4pairs-operand-first-register-vs-second-index-v1`. Shared source resource pinned to ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, four original owner files and six SHA-authenticated scenes; no ongoing competing original probe during launch.

## Source and tests

- Extended `scripts/t3_particle108_original_dxbc_operand_bindings.py` with `classify_primary_index_profiles`, [commit 336c1733](https://github.com/alwansan/raf/commit/336c1733d0928436c84dd89d7eda60dd328781ce). Distinguishes full DCL opcode+index signatures, opcode+first immediate register index, and family+first immediate index. Also computes source-private CB/SRV/Sampler/UAV primary-key stability independently per original VS and PS. No raw register values or original DXBC assets leave runner; the second index of 2D cbuffer declaration is NOT assumed to represent a proven byte size or array span.
- Added 3 synthetic fixtures separating CB secondary-only variation, true primary register variation and opcode-only variation [commit 8be3de5c](https://github.com/alwansan/raf/commit/8be3de5c3d96073066a1fe1f75204550142ef29a). Source-free [Actions 42262190492 SUCCESS](https://github.com/alwansan/raf/actions/runs/42262190492): **16/16 PASS** including 13 prior strict negative controls.
- New 18m isolated, ZIP2 SHA-pinned original workflow `.github/workflows/raft-t3-particle108-primary-slots.yml` [commit 013f4b19](https://github.com/alwansan/raf/commit/013f4b1945ccc96feb149e8ebbb9412e7fa63139). One original-source dispatch via `prompt/coordination/requests/t3-primary-slots-20261106-4d8c.trigger` [commit 199470cb](https://github.com/alwansan/raf/commit/199470cb973ed59e81f05ab870147504f1aeb6e1). Returned workflow to **manual-only** [commit a9ce13f2](https://github.com/alwansan/raf/commit/a9ce13f210d10fabb0f9018571e5ca9469f993f3), no jobs cancelled or duplicated.
- **Genuine source [Actions 42262329490 SUCCESS](https://github.com/alwansan/raf/actions/runs/42262329490)**, job `128045202243`, immutable execution SHA `199470cb973ed59e81f05ab870147504f1aeb6e1`. Four original Shader/Material asset owners, six scene SHA pins, original four VS+FS keyword pairs and eight genuine stage programs verified. 16/16 synthetic controls PASS within same workflow.

## Conclusive private-signature comparison (public counts only)

| Original stage | Full layouts | Opcode+first-index layouts | Family+first-index layouts | CB primary profiles | SRV primary | Sampler primary |
|---|---:|---:|---:|---:|---:|---:|
| VS (4 variants) | 4 | 3 | 3 | **3** | **1** | **1** |
| PS/fragment (4 variants) | 2 | 2 | 2 | **1** | **2** | **2** |

- This distinguishes true **primary register index identity** drift from full-index/secondary-index or opcode metadata drift. VS CB primary binding varies, VS SRV/sampler first-register sets remain stable. PS CB primary remains stable while PS SRV/sampler first-register sets vary. VS full layouts 4 versus 3 primary means at least one additional difference is not a family/first-index difference; no second CB index semantics claimed.
- Previous authentic CI [42261563646](https://github.com/alwansan/raf/actions/runs/42261563646) found 44 declarations over eight stages: 24 CB (two-index operands), 10 SRV, 10 sampler, 0 UAV. Previous real [42258686807](https://github.com/alwansan/raf/actions/runs/42258686807) proved all eight lack RDEF. Only aggregate counts reported; no original numeric registers, Shader48 private bytes, GUIDs, names, resource sizes or PathIDs exposed.
- Experiment JSON at `prompt/coordination/experiments/T3/20261106T1730Z-T3-chat-primary-index-4d8c.json`, [commit 4f4b4b74](https://github.com/alwansan/raf/commit/4f4b4b74247fa79d2b5708e11fe2a2efcc402d5d).

## Handoff and limits

This is a source-original D3D11 resource identity diagnostic, **NOT** original Unity ShaderLab recovery, SPIR-V descriptor equivalence, source material modification, GPU pixels or device acceptance. No .shader/.mat/.meta/scene/save assets, FMOD, Settings, touch, Unity native request, APK/OBB or game launch touched. Owner's phone still awaits verified color, water, FX and square-smoke restoration; world/save/reentry on earlier artifact is a separate achieved device observation.

**Next:** privately join source-original per-stage/keyword first DCL register keys with corresponding VKD3D-generated SPIR-V descriptors, preserving cbuffer secondary fields and variant identity; validate sampler/SRV/CB family mapping without logging protected numbers. Only after proven binding translate into ShaderLab and run Unity/phone image validation. Do not rerun equivalent original count-only jobs. `RENDER-002 OPEN / NOT_READY`.
