# T3 scheduled session — 2026-11-07 15:28 UTC
session_id: 20261107T1528Z-T3-scheduled-cross-strata-n3f6
origin: scheduled
identity: T3
branch: feature/android-native-port
initial_HEAD: b24449923cc9ef75dce7c61c1009720dbc8b7132

## Proven prior checkpoint
Owner phone artifact 42058825739: world entry/save/exit/re-entry succeeded, not visual recovery. CI41968665857 authentic export aggregate 106 pairs (76 exact / 30 RGB-drift), no per-pair source-format/sRGB metadata in public artifact. Latest earlier T3 session 20261107T1426Z-T3-scheduled-metadata-contract-q8f2.md. T1/T2 water, T4 physical mouse, T5 resolution/layout/package are separate scopes.

## This cycle
Registered independent work at work/RENDER-002/T3-20261107T1528Z-T3-scheduled-cross-strata-n3f6.md commit 98c4740673695930a427e00fd44d234bc373700d. Read live HEAD before code patch. Added aggregate joint strata (format × source_srgb × importer_srgb) to scripts/t3_rgb_drift_strata.py commit 8001cf9b84666b1eaab0abaae344914b489175e6. Added synthetic regression for exact/drift partition and UNKNOWN source-sRGB commit d0460c9b0ba9245fb0b3fab3f2505d9d109582e9. No raw filenames, pixel arrays, pathIDs, or private material data output. No Unity/native run or duplicate CI.

## Verification boundary
Inspected published source and test using GitHub connector; current container DNS cannot resolve raw.githubusercontent.com, so unable to execute newly published test suite locally. Older mounted five-test snapshot passed, but is NOT evidence for new code. CI result pending/not run. Joint strata is a diagnostic improvement only; no phone render fix.

## Next
Execute published full test suite in a clean runner, preferably lightweight source-only CI; then extract authenticated per-pair format/source_srgb/importer_srgb metadata in private export (existing aggregate artifact insufficient) and join with material/shader/ParticleRenderer evidence for white hand/raft and square smoke. Check live HEAD and work overlap first. RENDER-002 OPEN / NOT_READY.
