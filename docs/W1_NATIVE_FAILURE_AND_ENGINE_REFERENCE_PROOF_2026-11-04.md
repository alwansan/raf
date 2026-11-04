# W1 full native failure and source-linked engine references — 4 November 2026

Full native [41741108965](https://github.com/alwansan/raf/actions/runs/41741108965), job126282703102, immutable source2cb893434d7c819f085d52b34fad1e6568db4ae8 **FAILED before Unity**. The strict builtin restorer matched0 of142parseable declarations. **No new APK/OBB/XAPK**.

ZIP2 acquisition worked:14cached SHA-verified providers,488439356bytes; the selected3scene owners matched the feature branch's original LFS pointers. Scene export, helper recovery, TMP/PostFX/volumetric restoration and bounded DepthCopy installation passed. No selected3 LFS download was needed.

The actual export inventory contains1536Material documents:786references resolve to exported Shader .meta GUIDs and750use11internal engine PPtrs. The only reported inventory errors are2shader_missing_meta; reference fields themselves had no null/unresolved/unsupported entries. Inventory was taken AFTER restorations.

## New engineering and real CI

Added scripts/w1_verify_engine_export.py with7negative-control/read-only tests and isolated CPU workflow raft-w1-engine-export-proof.yml. It checks exact generated assembly/reader/TPK/dataset pins, all14original source fingerprints and165Shader objects, then checks the actual observed pointer histogram against exact original shader keys. The196canonical private engine records are additionally pinned by digest, not a caller-supplied success flag. No original names or programs are published.

[CPU source proof41745779746](https://github.com/alwansan/raf/actions/runs/41745779746) **SUCCESS**, source2f5c2f337ed3002246e9aed570bf2f84656ac42c: all750observed internal references/11unique pointers are within the25uniquely mapped original engine keys. Original140non-engine objects are retained. One custom key repeats; there are0empty names. Canonical196-record digest eb97d9e75992a9b90afad6101cf6d914c15ec73131d7d7f31333ded29650513b; original25binding digest8bea40f258ee1e0d5efa028929021164d9b66da30e0f8d2e55d631ea219dde94.

Initial CPU41745566630 failed because the new experiment incorrectly required every original custom key to be unique. That assumption was removed without dropping the duplicate object; the full-export checker still fails closed on name-only ambiguity. All52local W1 tests PASS.

The digest-pinned source11b69cedb6f8905ce6603e7923cbc319d0c569be has [validation41745967644](https://github.com/alwansan/raf/actions/runs/41745967644), **IN_PROGRESS at last observation**. It is still extracting the exact database at last observation. Check this exact run on continuation; no native repeat was requested.

## Limits and next correction

This verifies the actual observed engine pointer IDs against original identities. It does not prove that each original Material kept its original shader assignment, equivalent GPU programs, correct rendering, or phone behavior. No production builtin/water gate was changed and no new native request was submitted. NOT_READY,0/3.

The native log states TMP originalShaders=11, vendorFallbacksAdded=2; PostFX14/0 and volumetric3/0. Shared restore_tmp_shaders.restore writes newly added fallback .shader files without .meta before any Unity import. This provides a concrete explanation consistent with the2newfiles and2missingmetas. Their exact missing paths were not retained by the count-only audit, so do not invent original GUIDs or conclude that original metadata was lost.

Next: trace original owner/pathID/export GUID and the repeated custom shader key, and run the new full-export closure checker at the initial complete140Shader export boundary BEFORE vendor fallbacks are added. Only an actual source-linked export proof can justify correcting the zero-loose-builtin restoration assumption. Authentic water shader/FFT recovery is still independently required; do not repeat an unchanged full native attempt.
