# T3 independent session — 20261105T1130Z-T3-nonnormal-semantic-guard

Identity: T3 only. This is a separate continuation; shared T3 state/MEMORY is stale and another same-name session 20261105T1100Z may be active, so neither is overwritten. Resumed from 20261105T1032Z and reviewed newer 1100Z work. Track RENDER-002, ASSET-RESTORE-001.

## Baseline and verified evidence
- Branch feature/android-native-port; HEAD at review 9237cdab88427fa0b6f784019b230bd5719801f8 (other T agents updating concurrently). No other branch modified.
- Genuine 106/106 original vs same-export RGBA semantic comparison passed at CI42014733420 after applying exact original NormalmapDXT5nm conversion to 30 objects; raw 76 exact, 30 normal map encoding differences. This does **not** prove Unity/Adreno visuals or all 1617 exported PNG.
- Prior same-instance 41 Material/227 TexEnv/150 RGBA and shader-pointer work inherited. T3 concurrent session 1100Z targets shader links; avoid overlapping that path.
- At inspection T4 GitHub Actions #42019173918 and #42019173998 in progress. No jobs cancelled.
- Historical B02/B03/B04/B05/B11/B12/B15/B21/B22/B31/B38/B43/B44/B46 remain attributed to original agents.

## Distinct actual defect and change
The semantic comparison function `semantic_rgba_input` validated metadata but returned `decoded` unchanged for non-normal usages without validating RGBA mode, image type, dimensions or positive serialized TextureFormat. Malformed source objects could therefore be treated as comparable identity by a caller that skips normal-map transform, leading to an unjustified EXACT verdict if the caller reused a compatible fake object. This was a fail-open input boundary, not a demonstrated error in the original 106 valid objects.

- Commit 1cd1bff823f7ff7cfe6f3c4a2fcc66285a5346b2 adds fail-closed checks for every semantic input.
- Commit ea2415b0cab37684bf8028dbd4a40042bdcdd882 adds five focused tests for valid passthrough and invalid RGB/object/format/zero dimensions.
- Intended commands: `python -m unittest tests.test_t3_semantic_non_normal_input_guard` (or `python -m unittest discover -s tests -p 'test_t3_semantic_non_normal_input_guard.py'`).
- Local network sandbox cannot resolve github.com, so the exact checked-out source cannot be fetched to run these tests here. CI result for new commits not yet confirmed; no Unity/phone proof claimed.
- The code does not modify assets, PNG, shader programs, GUIDs, .meta, scenes, prefabs, .rgd, audio, Settings or touch. Existing original 106 comparison result is unchanged.

## Rejected and remaining hypotheses
Do not treat prior 30 raw pixel mismatches as corrupted albedo: they were authentic NormalmapDXT5nm conversion semantics, and a source-authentic test already resolved all 106. The new guard is defensive for future malformed sources, not a game-color fix. Full-game texture scope and shader/material program authenticity remain unverified.

## Next step
Confirm CI on ea2415b0 and, if failing, fix only this guard/test. Coordinate with active same-name T3 shader link experiment before touching those scripts. Then expand actual exported texture coverage beyond 106 selected links and perform Unity/Adreno visual test when a coordinated diagnostic build exists. RENDER-002 OPEN; NOT_READY. No new APK or device claim.
