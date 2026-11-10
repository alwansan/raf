# GFX-LAB — 20261110-GFX-chat-original-obj-index-parity-07
- session_id: 20261110-GFX-chat-original-obj-index-parity-07; origin: chat
- resumed_from: 20261110-GFX-chat-shader-variant-feasibility-06
- base_sha: 372240c8fcf0b7ff6f0c4a860ebb029d7167469c
- experiment_key: GFX-MULTI-007-original-obj-vertex-use
- scope: source-only OBJ declared vs triangle referenced vertex count to investigate M01 and M04 both 374 vertex difference between original and Unity
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- runs: CI42720920391 Android success, GFX-MULTI-006 v3 retry pending, new GFX-MULTI-007 source audit pending
- controls: exact source Mesh.export and triangle parity, reject missing/invalid original face refs, no raw OBJ or private geometry outputs
- limitations: even if 374 unreferenced vertices explain count mismatch, still no proof of tangent/rig/skin/submesh parity or original shader correctness
