# B22 — Original Material scalar value export parity (2026-11-04)

## Scope
W2 authenticated a whole-game **usage census** (1556 Materials, 33899 float entries across 82 owners; no original m_Ints), and B44 checks exported RGBA tint values. Neither checks whether an original individual Material retained the **values** of its m_Floats/m_Ints after export. A changed _Cutoff, _SrcBlend, _DstBlend, _ZWrite, _Metallic or _Glossiness can change cutout, blend/depth or shading even when GUID, texture, shader and color checks pass. This is a hypothesis, NOT a proven cause of the phone's white materials.

## Source-integrated verifier
- The [B22 comparator](../scripts/b22_verify_material_scalars.py) is read-only. It uses the B44 exact size/SHA-pinned list of 14 shader-bearing serialized owner files, authenticates original UnityPy objects, and joins them to actual YAML through the **same-process private export identity trace** plus fileID/metadata GUID. No guessed filename or GUID matching.
- Original and exported float numbers are normalized to little-endian **IEEE-754 binary32 bits**. Integers are compared as exact signed int32. It rejects duplicate scalar names/YAML keys, NaN, infinity, invalid types, ambiguous serialization, source/trace/export identity loss and symlinked inputs.
- Outputs only aggregate integer counts for compared/missing/extra/changed scalars and differing Material counts. No per-Material identity or proprietary scalar name/value is published; the script never repairs source or output data.
- [14 synthetic unit tests](../tests/test_b22_verify_material_scalars.py) cover positive binary32 roundtrip, malicious or mistaken changed _Cutoff/blend/int values, absent/extra slots, duplicate YAML/slots, swapped GUID/path ID, incomplete trace, invalid scalar, symlink and no-value-leak report.
- [Isolated workflow](../.github/workflows/raft-b22-material-scalars.yml) uses Ubuntu 24.04, pinned PyYAML 6.0.3, 8-minute timeout, a separate concurrency group, cancel-in-progress:false, no original-game bytes or native build.

## Verified evidence
- [Source implementation 064f4d68](https://github.com/alwansan/raf/commit/064f4d68c65ed2f3ce83926e71dab7b1f620681e)
- [Test and workflow commit e1d95ca6](https://github.com/alwansan/raf/commit/e1d95ca6b44ef38d77b6e14dee5b7617eb4a0750)
- [CI run 41918404573](https://github.com/alwansan/raf/actions/runs/41918404573) job 126884115085, COMPLETED SUCCESS, all 14 synthetic tests and syntax compilation pass on exact source e1d95ca6.

**No real ZIP2 original-versus-export Material values were compared** and no actual export mismatch was found or repaired. The synthetic success proves only the comparator detection contract, not Raft pixels or visual recovery.

## Next use at an existing coordinated export
Prefer ZIP2 at immutable source pin 15964ea8f246b6e076ce26b60931ee2e1a9a2385. In private authorized staging, verify every original file SHA/size and retain the same-export trace and actual Material YAML/.meta. Run (only inside that staging):

    python3 -m pip install PyYAML==6.0.3
    python3 -m scripts.b22_verify_material_scalars --source "$RUNNER_TEMP/w1-original" --private-export-trace "$RUNNER_TEMP/private-export-lineage.json" --project "$RUNNER_TEMP/project/ExportedProject" --out "$RUNNER_TEMP/b22-safe-summary.json"

If mismatch: isolate private original/export serializer and restore the **proven** scalar semantics; do not guess or rewrite other game assets. If match: reject export scalar-value loss for authenticated 14-owner scope, not for the entire 82-owner source set. Run alongside B44 colors and B05 textures at the next justified export rather than duplicate heavy Unity/Actions jobs.

## Boundaries
Only 14 original shader-bearing owners are currently in the comparator source map, while W2's full game had 18 Material-bearing owners. No actual private same-export comparison, Unity import, GPU pixel, Adreno device, phone, world/save test, APK/OBB/XAPK or Release has happened in B22 scope. Source/project settings, audio, touch, original .meta/GUID/.rgd, native request and schedules remain unchanged. RENDER-002 and WATER-001 OPEN, game NOT_READY with 0/3 independent full immutable-candidate reviews.
