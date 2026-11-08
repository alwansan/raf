# T3 scheduled checkpoint — 20261108T2131Z-T3-scheduled-orphan-material-m8q4
origin: scheduled
base_sha: 178c29b33236bc69d2cd730d84ef398c3e0a05b7
head_at_close: fce90e8f058068b01190707a7d79178cf5be5716
scope: RENDER-002 orphan material metadata coverage
resumed_from: 20261108T2026Z-T3-scheduled-external-guid-v6p9; T3 chat shared lab 20261108T2013Z-T3-chat-cl-pixelcopy-surface-f2n8

## Evidence
Owner phone 42058825739 succeeded world/save/reentry but visual issues persist; no claim of graphics fix. T3 real same-export 41939404454 proved 227/227 selected UV transforms, 89/89 internal pointers; external pointers and Android shader/alpha remain open. Shared mini lab 0.2.13 CI success but device PNG not yet verified in latest T3 state.

## New engineering
Identified false-positive: external material GUID scanner counted a .mat.meta GUID as resolved even if its paired .mat was absent. Published scope 314a2908, implementation ebc554ca, and regression fixture fce90e8f. A symlinked/missing material now increments orphan_mat_meta and does not count as an owner. Existing fixture now includes real .mat counterparts; new fixture covers orphan.
No raw assets, GUIDs, .rgd, Unity game, shared testpack, other worker files changed. No new build or duplicated CI dispatched.
Verification: source inspection and regression test added; Python/CI result not yet established at checkpoint. This fixes diagnostic classification only, not phone pixels.

## Next
Confirm source test CI for fce90e8f (or run python -m unittest tests/test_t3_particle_external_material_resolution.py); audit authenticated exported prefab/material tree, compare paired .mat and .meta, then inspect shader/texture/alpha of suspect smoke and white meshes. Preserve RENDER-002 OPEN NOT_READY.
