# GFX-LAB — 20261110-GFX-chat-material-texture-semantics-24

- session_id: 20261110-GFX-chat-material-texture-semantics-24
- origin: chat
- resumed_from: 20261110-GFX-chat-variant-reflection-sweep-23
- base_sha: 253a2981fc246b810965ece4637a33516382be6e
- issue_id: RENDER-002
- experiment_key: GFX-MULTI-023-original-material-texture-semantic-and-channel-census
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: audit the six selected original models, seven Materials, 63 TexEnv entries, 21 bound Texture2D assets, UV transforms, tint/color/float/int slots, texture format/color-space/mip/settings metadata and decoded RGBA channel variability. All private source data stays in the runner.
- status: PREPARED_CI_PENDING
- workflow: .github/workflows/gfxlab-multi-material-texture-semantics.yml

## Why this experiment follows GFX-MULTI-022

GFX-MULTI-022 [CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021) exhaustively checked all 1,435 linked Shader48 variant rows and 1,275 unique referenced DXBC stage programs: RDEF 0/1,275 and parameter/sampler/CB metadata 0/1,435. The original Material-property-to-DX11-register bridge remains blocked. GFX-MULTI-023 therefore changes scope to source Material/Texture2D fidelity rather than repeating the same shader reflection census.

## Planned checks

- Verify seven original Material objects and the exact 63 TexEnv slots (21 bound, 42 null).
- Verify seven bound textures per role: BaseColor, Normal and Metallic.
- Hydrate only exact source stream Git blob chunks selected by the existing SHA-pinned sparse transport.
- Decode all 21 original Texture2D objects and verify source dimensions.
- Count format/color-space/mip/filter/wrap/aniso metadata codes without assigning unsupported enum semantics.
- Count Material color/float/int slots, original tint presence, and identity/nonidentity UV transforms.
- Compute only per-role channel variability flags (R/G/B/A); Normal AG and Metallic alpha patterns remain diagnostic candidates, not proof of DXT5nm or smoothness semantics.
- Publish aggregate JSON only. No PNG, OBJ, source names, PPtrs, offsets, raw pixels, shader bytes or register indices.

## Acceptance and limits

- All six models, seven materials and 21 textures must remain exact source selections from ZIP2 SHA.
- A successful decode establishes original texture bytes/dimensions in the private source pipeline, not Unity GLES or Adreno output.
- `originalShaderRestored=false`, `actual_android_original_shader_pixels_verified=false`, and `phase_closed=false` regardless of channel statistics.
- No APK is planned in this experiment.
