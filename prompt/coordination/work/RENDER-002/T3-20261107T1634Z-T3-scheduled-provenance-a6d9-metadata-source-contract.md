# T3 RENDER-002 — metadata source contract

session_id: 20261107T1634Z-T3-scheduled-provenance-a6d9
origin: scheduled
status: IN_PROGRESS / NOT_READY
scope: independent metadata provenance investigation; no game asset or shared workflow changes
files: this work record and clients/T3/sessions/20261107T1634Z-T3-scheduled-provenance-a6d9.md only
experiment_key: T3-RGB30-METADATA-PROVENANCE-20261107
shared_resource: none; no Unity/Actions launched

## Evidence and hypothesis
Owner device report docs/DEVICE_FEEDBACK_42058825739_AR.md confirms local world/save/reload on artifact 42058825739, but white raft/hand and square smoke remain. Prior CI41968665857 aggregate 106 original/export textures: 76 exact, 30 RGB drift; aggregate reports do not provide individual format/source_srgb/importer_srgb. Prior actual original-to-export material checks CI41939404454 and CI41940350604: 41 Materials, 227 TexEnv slots and 150 color slots match in their bounded sample. Thus do not attribute white surfaces to lost Material color or internal UV identity without stronger evidence.

Hypothesis: the 30 RGB differences may be correlated with original compressed format, sRGB import or decoded color conversion; the current aggregates cannot discriminate these. Required next experiment: derive private per-pair format/source_srgb/importer_srgb from SHA-authenticated same-process original/export, retain identity/dimension/alpha parity, run scripts/t3_rgb_drift_strata.py --require-drift-metadata; emit counts only. No raw assets or identifiers in public artifact. Follow original Material shader PPtr -> ShaderLab/pass/keywords and ParticleRenderer blend/alpha to establish white and square smoke independently of texture drift.

## Evidence limits
The local /mnt/data/t3 snapshot is older (5 tests), not equivalent to the currently published script and expanded tests. Five older snapshot tests passed 2026-11-07; this is NOT CI validation of latest source. GitHub access via container DNS failed; GitHub connector fetch succeeded. No phone/GPU test, no new Unity export, no package build, no shader fix. CL links from device report are provenance, not inspected image pixels this run.

## Next
Recheck HEAD, active T scopes and existing CI before any new private export. Obtain per-pair manifest from pinned ZIP2 without exposing raw data; classify and map actual problematic materials to shader/particle properties. Avoid T1/T2 water and T4/T5 mouse/UI overlap.
