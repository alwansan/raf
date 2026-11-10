# GFX-LAB — 20261110-GFX-chat-glsl-source-evidence-08
- session_id: `20261110-GFX-chat-glsl-source-evidence-08`; origin=`chat`; resumed_from=`20261110-GFX-chat-unused-program-platform-07`
- base_sha: `b43b9258dda3db785abcda7dbcf76606212960d0`; source ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- experiment_key: `GFX-MULTI-034`, scope: verify if unlinked 139 GLES + 120 GLCore source programs contain bounded UTF8 GLSL with authored Shader48 property identifiers and uniform names.
- status: IN_PROGRESS; private source-only. No new Android APK or artifact with shader code; no T-team branch edits.
## Background
[GFX-MULTI-033 CI42808967835](https://github.com/alwansan/raf/actions/runs/42808967835) SUCCESS 205 tests: unused programs 139 GLES, 120 GLCore, 9 DX9, 1 other; alternate original Pass prog* rows 0; no leading direct version/SPIRV. The UnityPy public ShaderSubProgram exporter `UnityPy/export/ShaderConverter.py` interprets GL-family code as text. Check actual source privately.
## Boundaries
Even exact token or uniform name match in unlinked text is only candidate source semantic evidence, **NOT linked original shader runtime** or original DX11 t/s/CB offsets. Never disclose private GLSL, raw property names or source indexes.
## Runs / result
Pending.
