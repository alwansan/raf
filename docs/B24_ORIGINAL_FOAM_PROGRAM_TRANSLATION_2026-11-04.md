# B24 — Authenticated Foam/Global original two-pass stage translations (4 November 2026)

## Independent target

The native water gate still reports only **1 of 2** passes for `UltimateWater/Foam/Global`. B24 independently tested whether both original compiled passes can be recovered with real original stage identities; this is **not** a Unity ShaderLab replacement, a device rendering fix or permission to weaken `verify_water_render_contract`.

## Original source identity and private procedure

- Only `Raft/Raft_Data/sharedassets0.assets` from immutable ZIP2 provider `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, reconstructed from ZIP2 split chunks without LFS. Independently required exact size **115,978,112** and SHA-256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`.
- Authenticated original serialized shader PathID **2420**, raw object SHA-256 **`67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`**. Exactly 1 SubShader × 2 ordinary passes, one vertex and one fragment variant per pass, no keyword variants. No fabricated second pass.
- Original DXBC stages linked with the existing W1 original records and pass metadata; private `vkd3d-compiler` DXBC→SPIR-V, `spirv-val` Vulkan 1.1, `spirv-cross`→HLSL and private `glslangValidator` roundtrip→SPIR-V + `spirv-val`. Original binaries, generated HLSL and SPIR-V never leave runner scratch; artifact is aggregate-only.
- Stage program SHA-256 commitments, original pass order: pass0 vertex `77ffe091c60430461b9c125b2d839fedd04982a66a1f7e55331a26536f9e9522`, pass0 fragment `abcee848cbe73e0d16054844473cf7df7f0c9ae6cc62bc6a47dba9848aae4b69`, pass1 vertex `22b508edfeb543931fb649ddbbebe55248da2a4766e6ed066dc5c604428a57b5`, pass1 fragment `f8342b875524cc4b214a59dbcdc609e24c9477416c562af53003e6b04b1e5291`.

## Proof and corrected assumption

[Original translation run 41919758958](https://github.com/alwansan/raf/actions/runs/41919758958) **SUCCESS**. Both original passes and **all 4** linked stage DXBC programs passed original SPIR-V validation, private HLSL recovery and Vulkan 1.1 roundtrip validation. The recorded original serialized per-stage parameter envelopes are identical between passes for each stage (vertex **112 bytes**, fragment **52 bytes**); there are no numeric parameter records in those envelopes, but the genuine non-zero-size partial-CB declarations must **not** be removed/ignored. Vertex carries 3 partial CB slots, fragment carries 1.

Early negative runs [41918667270](https://github.com/alwansan/raf/actions/runs/41918667270), [41919019272](https://github.com/alwansan/raf/actions/runs/41919019272), [41919331051](https://github.com/alwansan/raf/actions/runs/41919331051), [41919628947](https://github.com/alwansan/raf/actions/runs/41919628947) were source guard failures, not evidence of failed DXBC translation. B24's original assumptions incorrectly fixed the first pass's CB vector-member count on both passes. Authentic serialized **pass0** uses **2** vector member records in CB0 for both vertex and fragment; authentic **pass1** uses **1** in CB0 for both stages. The original source was SHA-pinned throughout. B24 updated the validator to recover this exact distinction, then tightened it to require **exactly 1** on pass1 and pinned the object's SHA. Additional synthetic cases reject drift and invalid original layouts. The stricter post-proof CI recheck is [41920166966](https://github.com/alwansan/raf/actions/runs/41920166966); verify its final conclusion before claiming the final HEAD is green.

## Missing acceptance

**No original ShaderLab has yet been constructed or installed.** No proof of exact original CB name/register upload from Unity, sampler/texture state, original material GUID linkage, ShaderLab pass graph in exported project, Unity import, Android Adreno parity, or game performance. This experiment narrows the remaining work to authentic per-pass CB/resource binding and ShaderLab installation. Strict `WATER-001` stays OPEN; no source authenticity gates, `.meta`, GUID, Audio, Settings or touch code were touched.

Owner report: Audio and Settings currently work; touch/layout remains explicitly deferred.
