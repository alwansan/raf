# T3 RENDER-002 — authenticated RGB drift stratification

session_id: 20261107T0632Z-T3-scheduled-drift-stratification-n8v3
origin: scheduled
identity: T3
baseline_sha: 58ac85ef9250985fe21dc62e1bf59086c2753455
status: IN_PROGRESS / NOT_READY
experiment_key: T3-RENDER-002-RGB30-FORMAT-STRATA-v1
shared_resource: none (source evidence only; no Unity/CI launched)

## Separate scope
Only this work file and an independent T3 session file; no changes to shaders, materials, textures, game resources, workflows, or shared ledger. T4 owns mouse and T5 owns Resolution/three-button placement. No overlapping live source modifications.

## Evidence and discriminating hypothesis
Owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md: 42058825739 enters, saves, exits and re-enters world; white hand/raft, lighting and square smoke remain. CL source pin 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Existing authentic original/export run 41968665857: 106 Texture2D pairs, 76 exact, 30 RGB drift, no alpha-only/dimension/orientation mismatch. Existing 41939404454 verifies 227 selected TexEnv transforms; 41942377246 verifies selected 25 external + 89 internal texture references. Those scoped results reject a blanket missing-pointer explanation but cannot attribute white objects or square smoke to the RGB drift.

Hypothesis H1: drift clusters by source Texture2D encoding or export colorspace/alpha treatment. Competing H2: drift is distributed independently and caused by other decoder/export transformations. Neither is established. A positive cluster requires original format + source color-space flags + importer metadata on the SAME authenticated 106 pairs. Do not treat unknown importer fields as false.

## Next reproducible original-data experiment (not executed this cycle)
Use the immutable original ZIP2 pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385 and original/export same-instance run 41968665857's private manifest. For each of 106 pairs, join original Texture2D pathID/source file SHA, format, mip level, alpha presence, source sRGB when actually encoded, exported importer sRGB/alpha metadata when present, exact-vs-drift, and channel-difference histogram. Require identity and pixel dimensions to match before grouping. Stratify 30 drift against 76 exact negative controls; record UNKNOWN for unavailable fields. Aggregate counts only; no proprietary bytes or loose assets in public logs. Test per-channel nonlinear transfer versus premultiplication only as hypotheses, not an automatic texture modification. Then trace verified affected texture GUID -> Material TexEnv -> renderer/ParticleRenderer -> screenshot subject before any fix.

## Gate / checkpoint
No newly executed original-pixel experiment, source repair, or on-device result this cycle. RENDER-002 OPEN / NOT_READY. Do not rerun 41968665857 unchanged or run Unity without coordinated shared-resource review. Recheck branch HEAD, active Actions and T3 chat scopes before scheduling this distinct stratification experiment.
