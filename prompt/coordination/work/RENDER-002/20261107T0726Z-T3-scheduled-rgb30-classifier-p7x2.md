# T3 RENDER-002 — RGB30 private-manifest classifier

session_id: 20261107T0726Z-T3-scheduled-rgb30-classifier-p7x2
origin: scheduled
identity: T3
status: SOURCE_TOOL_LOCAL_TESTED / NOT_READY
experiment_key: T3-RENDER-002-RGB30-PRIVATE-STRATA-v1
shared_resource: none

## Scope and hypothesis
Follow-up to 20261107T0632Z-T3-scheduled-drift-stratification-n8v3, separate new file. Do not edit T4 physical mouse, T5 Resolution/UI, T1/T2 water, or shared original-data exporters. Prior authenticated run 41968665857: 106 Texture2D pairs, 30 RGB drift, 76 exact. Hypothesis: drift clusters by original encoding, source sRGB or importer sRGB; no causal tie to phone white materials or square smoke yet.

## Concrete local execution
Created independent Python aggregate-only classifier and five unittest negative/positive controls locally (source artifact available in this run's sandbox). Verified 5/5 tests PASS and py_compile PASS on 2026-11-07. It enforces original/export identity, dimension and alpha equality for each pair; requires 106 pairs/30 drift baseline; refuses unsafe format labels, missing booleans and invalid sRGB values; emits only counts stratified by format/source_srgb/importer_srgb, with unavailable fields UNKNOWN. This is a synthetic test only; no private original/export manifest was acquired or processed. The script is not yet integrated into repository CI. Do not claim real original-format clustering or graphics repair.

## Resume
Acquire authenticated same-export private manifest for run 41968665857, verify ZIP2 source pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385, run classifier privately and publish aggregate-only result. Check whether original metadata is available; UNKNOWN is not false. Join drift IDs privately to Material/ParticleRenderer/shader and screenshot only after validated provenance. No Unity/native build or CL mutation. Preserve .meta/GUID/.rgd/audio/Settings. RENDER-002 OPEN / NOT_READY.
