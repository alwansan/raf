# GFX-LAB — 20261110-GFX-chat-linked-dxbc-reflection-11
- session_id: `20261110-GFX-chat-linked-dxbc-reflection-11`; origin=chat; resumed_from=`20261110-GFX-chat-gl-program-envelope-10`
- base_sha: `d3803ba469d9a8af246a593d7c6e5d780c5a9622`; ZIP2 authentic source `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- issue RENDER-002; experiment_key `GFX-MULTI-037`; resource_key gfxlab-multi037-linked-dxbc-private
- status: IMPLEMENTING
## Source reasoning
GFX-MULTI-036 [CI42812418402](https://github.com/alwansan/raf/actions/runs/42812418402) proved original compiled Shader48 platform **D3D11 only**; 259 orphan GL-type entries aren't authoritative original GLES programs. Earlier GFX-MULTI-022 found 0 RDEF among 1,275 authentic linked DX11 stage programs. DXBC public container can have alternative SDBG/SPDB/ILDB/RDAT/SRCI metadata. Inspect strictly as bounded source evidence.
## Negative controls
A FourCC tag or private property-name byte hit does not establish actual original Material register offset/CB layout, Pass states, Android shader/PC pixel match. Source remains private and purged. The only write branch is `experiment/android-graphics-rootcause`; no new APK or T-team edits.
## CI status
Pending.

## Terminal verified GFX-MULTI-037 source evidence (2026-11-10)
- GFX-MULTI-037 [CI42813380416](https://github.com/alwansan/raf/actions/runs/42813380416) **SUCCESS /230 Python tests**, fixed ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385` with cleanup confirmation. All **1,435 original stage links**, **524 exact VS/FS keyword/tier pairs**, **1,275 unique linked genuine DX11 programs** audited (620 vertex, 655 fragment). Every DXBC has exactly **ISGN×1 + OSGN×1 + SHDR×1**: ISGN=1,275, OSGN=1,275, SHDR=1,275; **RDEF=0, SDBG=0, SPDB=0, ILDB=0, RDAT=0, SRCI=0, STAT=0, OTHER=0**; zero alternate debug or reflection chunks. Original Material→t/s/constant-buffer resource offsets cannot be recovered from missing RDEF/debug metadata, and no device/PC pixel parity. OriginalShaderRestored=false. Safe aggregate [artifact 13762877353](https://github.com/alwansan/raf/actions/runs/42813380416/artifacts/13762877353), expires 2026-11-17T12:10:22Z.
- Full pass-linked DXBC metadata evidence excludes the proposed alternative reflected/debug chunk route in these files; **do not** claim that DXBC instruction declarations are sufficient to recover authored Material property names. SHDR t/s/b operands are only resource register indices without name link.
- Next: PC/ShaderLab original material/shader reflection is an external evidence dependency for exact author-to-register map. Source-only follow-up can independently validate 524 exact DXBC VS/FS IO signature pairs (GFX-MULTI-038), but it does not solve resource bindings or permit genuine Shader48 Android APK.
