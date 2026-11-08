# T2 experiment — SHA-original Foam pass material-to-image producer evidence
session_id: 20261108T1925Z-T2-chat-original-blit-cecil-v2
origin: chat
base_sha: 6c787ca8436dea3d3a52537577642345f76de0ad
experiment_key: T2-FOAM-SHA-ORIGINAL-BLIT-20261108
issue: WATER-001
status: COMPLETED_SOURCE_ORIGINAL_AUDIT; OPEN_PASS1_SOURCE_PRODUCER
scope: authentic original ZIP2 Mono.Cecil method bodies (SHA checked privately), safe counts and role tags only
taken_over_from: T2 earlier FoamShaderFindResultFlow original typed IL + T2 synthetic Blit gate CI42512807487; scheduled gap clients/T2/sessions/20261108T1922Z-T2-scheduled-original-il-boundary-p7q4.md

## Implementation and verification
- New isolated `android-port/Experiments/T2/FoamBlitOriginalProducers` project and `scripts/t2_foam_original_blit_report.py` strict shape/authentication anti-spoof validator with 14/14 tests. Workflow `.github/workflows/raft-t2-foam-original-blit-producers.yml`, 25-min bounded and ZIP2 SHA pin `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original bytes SHA-verified then purged, only safe numeric report artifact. No game shaders/raw assets/IL in artifacts.
- Initial CI42515708324 FAIL missing parser import from sparse checkout; CI42515827760 FAIL other transitive source-only imports; fixed checkout to source-only scripts tree, no game files. [CI42515921184](https://github.com/alwansan/raf/actions/runs/42515921184) original run SUCCESS (11/11 + C# selftest + original SHA), safe artifact 13631596355. [CI42516309771](https://github.com/alwansan/raf/actions/runs/42516309771) SUCCESS on extended material argument counts (14/14), artifact 13631821162. [CI42516516391](https://github.com/alwansan/raf/actions/runs/42516516391) COMPLETED SUCCESS on latest reason-code fix, artifact 13631856408; SHA-signed input and private name extraction again verified; logs contain safe tags only.
- Original actual data: 19118 managed method bodies, 81 typed Shader.Find; unique SHA-original Foam Shader.Find and one exact downstream Shader field → Material constructor → Material field chain. 66 exact 4-arg Graphics.Blit calls globally (18 literal0, 11 literal1, 37 other/dynamic), NOT counts of Foam calls.
- Authentic Foam material field is the actual typed material argument of exactly one pass0 Blit and one pass1 Blit; 0 material-local-alias direct candidates.
- Pass0: source RenderTexture / destination RenderTexture, both typed_field at IL, actual texture object identity unknown. Pass1: exact original material field confirmed, its **destination** was directly typable, but the first unclassifiable input in reverse CIL order is **source**; safe log `T2_FOAM_PASS1_FIRST_IMAGE_OPERAND source_not_direct`. No claim of null/missing runtime source.
- Whole summary and original-safe artifact evidence: `docs/T2_FOAM_SHA_ORIGINAL_BLIT_PRODUCER_2026-11-08.md`.

## Boundaries / next
Authenticated typed IL does NOT prove same texture instance across passes, uniform/CB0 upload, sampled texture/sampler, pass render state, original ShaderLab installed in Unity2021, Android water pixels or full-game readiness. T2 shared mini r2 NO_BUILD, first shared APK CI42509945996 still awaits phone case results; no duplicate build or protected branch/other worker edits.
Next isolated action: privately trace pass1 source-expression producer in exact typed CIL including nested calls/fields/locals and control flow. Restrict derived source instance identity to independently evidenced def-use and crosspass target equality; unsupported/ambiguous remains unknown.
