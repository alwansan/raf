# GT — Chat-16: original Particle108 RDEF absence, sampler mismatch, real unbound Unity probe

- session_id: GT-20261112-CHAT-16-PARTICLE108-UNBOUND-UNITY
- origin: chat
- repository: `alwansan/raf`; write only `feature/android-native-port`
- source: SHA-pinned `zip2` commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, no Git LFS
- Owner stopped T1–T5. No dependency on their agents. Keep original scenes/assets/GUID/meta untouched.

## Verified real source data and safe failure evidence

1. [43228860357](https://github.com/alwansan/raf/actions/runs/43228860357) verified **eight of eight exact original Particle108 VS/FS DXBC stages lack RDEF** (`original_RDEF_absent_stages=8`; `original_RDEF_unique_stages=0`). A missing RDEF chunk is authentic absence, NOT a fabricated empty sampler table. Four source keyword pairs and six source scenes SHA-authenticated.
2. [43229468414](https://github.com/alwansan/raf/actions/runs/43229468414) retained 4 authentic source VS/FS pairs, 8 glslang stages; all translated HLSL across those stages had **10 `SamplerState` declarations** and 10 explicit sampler register annotations. Strict resource binding refused `TRANSLATOR_SOURCE_REGISTER_SLOT_MISSING`.
3. [43232633015](https://github.com/alwansan/raf/actions/runs/43232633015): follow-on resource class split proved the unresolved binding is a **sampler**: `TRANSLATOR_SOURCE_SAMPLER_SLOT_MISSING`. This must remain a fail-closed condition. The source `m_TextureParams` sampler indices and translated SPIR-V/HLSL sampler bindings are not yet proved equivalent; do not guess or assign all samplers by ordinal.

## Real isolated Unity 2021 evidence

[43232000368](https://github.com/alwansan/raf/actions/runs/43232000368), first independent unbound original-derived compile-only workflow, used source-authenticated original four pairs and provisional two-keyword ShaderLab; passed the synthetic and glslang checks, reached **real Unity Editor 2021.3.45f2 Android Vulkan**. Real Editor result:
- private shader imported=true; one Material pass; 4 `ShaderVariantCollection` variants registered
- Android-only Vulkan target=true; private AssetBundle was physically created (6,231 bytes)
- **Unity shader errors=3; total shader messages=4; final status INCONCLUSIVE / job FAILURE**
- three unnamed/misbound samplers (`samplers0` .. `samplers2`) unrecognized as Unity texture-property sampler names or defined inline samplers in the Vertex program.
- independent GLSL link diagnostic: `cb1_0_m0` vertex and fragment arrays have incompatible original translated sizes 5 vs 21.
- AssetBundle existence or success of 8 glslang stages does NOT imply a working shader. No original Material binding, GUID restoration, Android device pixels or full XAPK claimed.

Created [139d407](https://github.com/alwansan/raf/commit/139d407882bc483b8a66ff1b43493a6b5519f4a5) compiler-only unbound original-derived workflow (separate from strict source-bound pipeline). Added stage-local **private symbol-only cbuffer fix** [f530538](https://github.com/alwansan/raf/commit/f530538e56e9ac66d7e2cd7a660869bb9686798c), synthetic positive/negative tests [40fe774](https://github.com/alwansan/raf/commit/40fe7746b59f07fcb25fbff61a7421863650af4e), and wired [2aca1a1](https://github.com/alwansan/raf/commit/2aca1a16f48ebf851993b8243287af5064cf4cf2) to run **real Unity** with separate Vertex/Fragment `cb*` symbols, while preserving every private HLSL register annotation, original owner hash and sampler spelling. The diagnostic transformation affects only a disposable isolated project, not the game's original assets. Latest modified unbound probe is [43233472806](https://github.com/alwansan/raf/actions/runs/43233472806), which was pending when recorded; **no PASS may be claimed until completed.**

## Native build and next steps

- Full game [43205543533](https://github.com/alwansan/raf/actions/runs/43205543533) remains in progress at real Unity Editor import; the last downloaded log progressed through genuine imported textures at 2026-11-12T13:22:51Z. No APK/OBB/XAPK confirmed. Do not launch duplicates or cancel the active native run.
- Source 9 arrays, 28 references, 416 cross-owner external Material→Texture links and 50 BC3 top-mip layers were proved separately in 43207734641; old native full build snapshot c8680938 does NOT include later strict combined gate commits.
- 770 exported custom Material documents still use Dummy shader after vendor restorers; **do not mark these restored**. Original Adreno rendering equivalence not proved.
- Next: inspect result of 43233472806 for cbuffer-conflict disappearance. Continue exact original sampler source↔translator binding study using Stage/SPIR-V reflection or original DXBC token declarations, with private count-only reports; no ordinal/placeholder sampler guessing. Only then attempt same-instance original Shader48 Material GUID binding in the full export, then device pixels.
