# T3 scoped evidence chain — 20261108T0932Z-T3-scheduled-particle-chain-m8q5
session_id: 20261108T0932Z-T3-scheduled-particle-chain-m8q5
origin: scheduled
issue_id: RENDER-002
status: active
updated_at: 2026-11-08T09:32:00Z
base_sha: 1aacc01d72f9d2fd84ba9ba87ecc6895dd9739e7
resumed_from_sessions: 20261108T0826Z-T3-scheduled-v3q7; 20261108T0732Z-T3-scheduled-null-pptr-v9k2
intended_files: this work record; own T3 session; independent evidence protocol only
experiment_key: RENDER-002:ZIP2-pin-15964ea8:CL-pin-520c4cf4:particle-prefab-renderer-material-shader-alpha-variant:20261108
resource_key: none (read-only source and CL)

## Evidence and hypothesis
Owner device run 42058825739 at e9c358eda01785b65e4eb14f18723da426635628 demonstrated world/save/reopen, not shader correctness. CL images identify square smoke in menu and white hand/raft in gameplay; no direct pixel inspection this session. Prior same-export 41939404454 proved 227/227 TexEnv UV and 89/89 internal texture identity in selected 41 materials; 25 external refs and shader variants unproven. 41940350604 scoped RGBA parity is not Android render proof. Separate UltimateWater foam/spectrum errors must not be attributed to smoke without shared shader/material evidence.

## Decisive discriminating experiment (not yet executed)
1. Authenticate ZIP2 provider pin and original file size/SHA via docs/ZIP2_SOURCE_PROVIDER.md; never publish raw data. Inspect original particle prefab hierarchy, ParticleSystemRenderer material PPtr and shader PPtr; compare with actual AssetRipper export on same source snapshot, including GUID, fileID, texture PPtrs, main texture alpha presence, blend factors, ZWrite, render queue, shader keywords and enabled passes.
2. Distinguish four hypotheses: (A) missing material/texture PPtr, (B) dummy/missing fragment alpha or shader variant, (C) billboard particle vertex streams/UV mismatch, (D) scene exposure/lighting/color-space. Require explicit matched original/export chain and a device comparison for pixel conclusion.
3. Do not mutate source assets or infer actual device visuals from CI; coordinate any Unity run with T5 and active Actions first. T4 owns physical mouse; T5 owns resolution/buttons.

## Current outcome
No new experiment or source repair yet: no authenticated original prefab/particle graph available in this session's accessible GitHub text reads. This work record documents exact next discriminating test; do not treat it as a repaired effect. No native workflow requested.