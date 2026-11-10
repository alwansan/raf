# GFX-LAB 20261110-GFX-chat-managed-cil-calls-18
- session_id `20261110-GFX-chat-managed-cil-calls-18` | origin `chat` | resumed_from `20261110-GFX-chat-managed-shader-prop-17`
- baseline `f3e9002187e072713875f620ad02447ce7048d30`, only writable `experiment/android-graphics-rootcause`.
- Original pinned ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
## GFX-MULTI-044 / RENDER-002
GFX043 source-authenticated `Assembly-CSharp.dll` `#US` had 4488 entries, 10/27 exact Shader48 authored properties, 3/9 textures and 2/3 original Material-bound TexEnv names. Method-name-only `MemberRef` contained SetTexture/PropertyToID etc but the previous test did not resolve *actual calls*.
This follow-up scans bounded ECMA-335 IL `MethodDef` bodies (using dncil+dnfile); counts `ldstr` exact source property token and `call/callvirt` whose metadata target declaring type is `UnityEngine.Material`, `UnityEngine.Shader`, or `UnityEngine.MaterialPropertyBlock`. A call and literal in the same method (or within a short forward window) is only a candidate, not proven argument flow or original Material→DX11 t/s/b/CB.
Source on private runner only; synthetic pure tests; no original code or property literals published. Do not build Shader48 Android APK from this evidence alone.
## CI
Pending.

## Verified GFX-MULTI-044 CI result
- [CI42830910833](https://github.com/alwansan/raf/actions/runs/42830910833) SUCCESS; 285 source-free Python tests; original ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385; private source purge passed
- Original Assembly-CSharp managed CIL: 19,118 MethodDefs /491,490 IL instructions /0 parse failures; exact Shader48 property `ldstr` names in 17 methods (10 distinct) and 821 calls to real UnityEngine Material/Shader/MaterialPropertyBlock API methods in 203 methods
- **14 methods** contain both literal property names and relevant API call, 7 distinct Shader48 properties; **16** ldstr instructions with relevant call in following 12 instructions covering 5 distinct properties; 11 methods include original Material-bound texture names plus API calls
- These are method-level/proximity candidates only; no CIL stack dataflow proven. No original Shader48 property to DX11 t/s/b register or ConstantBuffer byte offset mapping
- Safe persistent report `gfxlab/evidence/20261110_gfx044_managed_cil_usage_safe_counts.json`; artifact 13772290580; no original code/strings/photos uploaded
- Next GFX-MULTI-045 candidate: real bounded CIL evaluation-stack argument flow, then independent genuine shader reflection for GPU binding. OriginalShaderRestored=false
