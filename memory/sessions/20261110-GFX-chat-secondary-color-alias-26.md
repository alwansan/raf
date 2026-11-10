# GFX-LAB — 20261110-GFX-chat-secondary-color-alias-26

- session_id: `20261110-GFX-chat-secondary-color-alias-26`
- origin: `chat`
- resumed_from: `20261110-GFX-chat-float-wrap-color-25`
- base_sha: `0136bcfc67363329c3dd395510d09da6bd5e4170`
- experiment_key: `GFX-MULTI-025-original-secondary-color-and-material-texture-alias-census`
- source_ref: `ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- scope: original 6-model renderer/material/texture identity graph and 14 Color slots; private name-based allowlist only.
- status: `PREPARED_CI_PENDING`

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
