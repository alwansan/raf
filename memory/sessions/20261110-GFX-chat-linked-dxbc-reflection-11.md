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
