# A3 DELIVERY-014 — exclusive publication of single-part signed Android output

**Date:** 4 November 2026 (UTC checkpoint 2026-11-03 22:56). **Branch:** `feature/android-native-port`. **Agent:** A3 under new identity `raft-20261103T224800Z-a3c41e7b`, session `A3-20261103T225045Z-9d52c8a1`, resumed from completed `raft-20261103T145149Z-a3e71b29`.

## Reproduced production defect

`scripts/package_android_delivery.py:PartsWriter.finish` published a one-part APK/OBB/XAPK with `Path.rename` after writing and closing `.part001`. On POSIX, `rename` replaces an already-existing target even if another publisher created a legitimate signed output name after preparation. This is **different from** A3's previous DELIVERY-013 fix in `scripts/reassemble_android_delivery.py`; the packaging writer had the same hazard.

A3 committed a four-fixture synthetic test and isolated Ubuntu-24.04 CPU workflow at [test commit 5b3ccf60](https://github.com/alwansan/raf/commit/5b3ccf60f558da225188b2f47cb8b28791cb6bb2). [Expected RED CI41734635288](https://github.com/alwansan/raf/actions/runs/41734635288), job126260534560, **FAILURE**: 2/4 tests passed, collision test failed because `ValueError` was not raised and competitor was replaced; unsupported-hardlink injection errored because the old module had no `os` import. This verifies a real source behavior with artificial files, not proven real user data loss.

## Verified fix and results

[Production fix db88edd26](https://github.com/alwansan/raf/commit/db88edd26d0454db5cd971c643ca80786de77c87) imports `os` and replaces single-part `rename` with `os.link(part, final)`, which creates the final pathname atomically only if absent. The checked part is already closed; then the temporary link is removed. `FileExistsError` raises a clear no-overwrite error, and other `OSError` reports a hard-link filesystem requirement. The change keeps the full byte hash/part manifest and does not create an extra multi-GB copy. Multi-part transport remains unchanged.

[GREEN CI41734812562](https://github.com/alwansan/raf/actions/runs/41734812562), job126261144475, completed **SUCCESS** at exact fix commit `db88edd26d0454db5cd971c643ca80786de77c87`: **4/4** new source-owned tests (normal single-part, competing file preservation, hardlink denial, multi-part unchanged) plus **13/13** existing `test_android_delivery_package.py` checks. All tests were tiny synthetic fixture inputs and no actual Unity/native/real signed output ran.

## Limits, coordination, and follow-up

This fixes the demonstrated source no-clobber defect on a hardlink-capable packaging filesystem. Hard-link support on the workflow's Ubuntu runner is supported by tests; Android shared storage, Termux home, external storage and real-size signed delivery acceptance must be separately exercised by the authorized native-delivery coordinator. It does **not** prove installation, signing, APK/OBB/XAPK publication, water/FFT, shader/colour, FMOD, world, haptics or phone rendering. `WATER-001`, `RENDER-002` and `FFT-FORMAT-009` remain open. Project **NOT_READY**, no immutable build candidate and **0/3** independent full readiness reviews.

No edits to `Raft/**`, ZIP2, LFS assets, metadata/GUID, Haptics staging, original sources, other agent work, native build request, Releases, other branches, CL, or automations. A3's own coordination records are linked from this report; this scoped work is `completed` rather than game readiness. Future work requires a fresh live HEAD/Actions review and separate identity.
