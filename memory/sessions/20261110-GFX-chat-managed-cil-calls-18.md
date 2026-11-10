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
