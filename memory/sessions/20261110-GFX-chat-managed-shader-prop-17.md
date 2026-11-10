# GFX-LAB — 20261110-GFX-chat-managed-shader-prop-17
- session_id: `20261110-GFX-chat-managed-shader-prop-17`; origin=`chat`; resumed_from `20261110-GFX-chat-affine-fullframe-16`
- baseline HEAD: `19e6acfe394111da9c1a5087b35d3e2fe302369b`; writable branch: `experiment/android-graphics-rootcause` only
- experiment: GFX-MULTI-043 (RENDER-002)
- Source PIN: ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
## New source direction
After confirmed GFX-MULTI-042 synthetic Adreno affine fullframe result (20,212 interior pixels; true original Shader48 shader still blocked), pursue original material resource name trace via **authentic PC managed metadata** rather than repeating GPU triangle tests. ZIP2 manifest has **366 files** and no standalone `.shader`/`.hlsl`/`.cginc`/`.compute`/`.glsl`/`.shaderlab` sidecars; this does not exclude binary embedded source. The authentic `Assembly-CSharp.dll` and `Custom.dll` contain managed code; parse their ECMA-335 `#US` literal string heaps with dnfile and correlate against original Shader48 `m_PropInfo` property names (27 total, nine texture properties) and original seven Material TexEnv sets. Count names only, never print private literals.
## Important negative controls
Literal name in a .NET assembly does NOT prove it was called at runtime, set in a material, or bound to DX11 sampler/register/ConstantBuffer. `MemberRef` Material/Shader API names alone also do not prove call-site association. Original G8 Material property→DX11 t/s/CB + CB byte offsets remains BLOCKED unless genuine original source-based linking appears. Neither GFX040/GFX041/042 synthetic APK carries Shader48.
## CI
Pending fail-closed source-free synthetic tests + original ZIP2 privately pinned runner with source purge and safe aggregate output.
