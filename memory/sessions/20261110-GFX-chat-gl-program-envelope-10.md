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
