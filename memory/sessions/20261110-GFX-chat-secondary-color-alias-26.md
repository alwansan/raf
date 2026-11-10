# GFX-LAB — 20261110-GFX-chat-secondary-color-alias-26

- session_id: `20261110-GFX-chat-secondary-color-alias-26`
- origin: `chat`
- resumed_from: `20261110-GFX-chat-float-wrap-color-25`
- base_sha: `0136bcfc67363329c3dd395510d09da6bd5e4170`
- experiment_key: `GFX-MULTI-025-original-secondary-color-and-material-texture-alias-census`
- source_ref: `ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- scope: original 6-model renderer/material/texture identity graph and 14 Color slots; private name-based allowlist only.
- status: `SUCCESS_SOURCE_ONLY_GFX_MULTI_025`

## Baseline
- [CI42745536309](https://github.com/alwansan/raf/actions/runs/42745536309) GFX-MULTI-024 SUCCESS: 139 tests; seven original material slots map to six unique Material21 objects; twenty-one bound texture references map to 18 unique Texture2D objects. All 112 Float and 14 Color original saved-property labels match Shader48's 27 declared property labels.
- Seven Color slots are exact RGBA white and seven are nonidentity; GFX-MULTI-025 tests whether nonidentity means RGB black with Alpha=1 or actual nonzero RGB, without exporting values.
- No Android Shader48 equivalence, original shader registers, constant-buffer byte offset, PC/device pixels or rig restoration was proven.

## Planned private checks
- Read all six original source model entries and Renderer Material links at SHA pinned source; identify repeated Material21 and Texture2D identities inside the runner; export only anonymous group-size counts.
- Inspect the 14 original source Material Color properties and exact Shader48 property-name membership; classify allowlisted known Unity color names without exposing original identifiers. Count black-RGB/white/other with Alpha bucket.
- Source-free tests validate no private pointers or values appear in public safe output.
- No APK; update RESTORE, OPEN_WORK, MEMORY and STATE after CI.

## Runs
- Pending until workflow executes.

## GFX-MULTI-025 — exact source secondary color and shared identity proof (2026-11-10)

[CI42746455458](https://github.com/alwansan/raf/actions/runs/42746455458) **COMPLETED SUCCESS**, **146 unit tests**, source ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Source-private six selected models, seven Material21 Renderer slots and 21 original Texture2D links:
- Material alias groups: 5 single-reference groups and 1 double-reference group, **6 distinct original Material21 objects**; one material shared across models.
- Texture alias groups: 15 single-reference groups + 3 double-reference groups, **18 distinct original Texture2D objects**; three shared across models, **zero cross-role alias groups** (no reuse between BaseColor/Normal/Metallic roles).
- Source 14 saved Color slots match 14/14 Shader48 property names: seven known Base Tint white RGBA (RGB nonzero) and seven **`_EmissionColor` named property candidates with RGB exactly black and alpha exactly one**. Thus the seven nonidentity Color entries from GFX024 are *black emissive colors*, not failed diffuse tint. No GPU emissive-rendering equivalence has been proven.
- Only anonymous count histograms and safe allowlisted property categories published; no source name beyond public allowlist, private PPtrs, original vectors, IDs, shaders or textures exposed.
- Safe artifact [13730829715](https://github.com/alwansan/raf/actions/runs/42746455458/artifacts/13730829715), expires 2026-11-17T03:00:31Z UTC. All private source files purged (`GFX_MULTI025_ALL_PRIVATE_SOURCE_PURGED=true`).
- `originalShaderRestored=false`; source Material→DX11 t/s/CB offsets unknown; `android_gpu_pixels_verified=false`, `phase_closed=false`. No APK, no game assets in public Git, no changes to T1–T5 branches or main/zip2.

### GFX-MULTI-026 next
Audit seven original Shader48 Pass render-state declarations and original Materials' render queue/keywords/instancing; map what is explicitly present in original source vs missing or undecodable, using source-only bounded coverage. Do not invent Cull/Blend/ZTest/ZWrite/ColorMask states or declare original shader parity before Android GPU/PC reference.
