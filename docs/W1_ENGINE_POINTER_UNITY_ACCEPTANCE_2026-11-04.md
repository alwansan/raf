# W1 original engine-pointer acceptance across the full shader corpus
4 November 2026. Client raft-20261103T162900Z-73e8c2a1; writable branch feature/android-native-port only.

## Final verified result
[Full-corpus run41738481868](https://github.com/alwansan/raf/actions/runs/41738481868) **COMPLETED SUCCESS**, exact source da39e24c3f4e85276d386182c960895b88e35839, job126273694040, aggregate artifact13280257470.

All14 independently pinned original Shader-bearing owners were reauthenticated from read-only ZIP2 commit15964ea8f246b6e076ce26b60931ee2e1a9a2385:488,439,356bytes,165actual original Shaderobjects. Cache-first planning reused the two largest files and fetched only the12missing owners; no LFS.

All25 original official-vendor-name shader objects map uniquely to the exact exporter's embedded engine database using names and ordered property lists;140other original shader keys do not match that database. No unresolved or ambiguous original vendor keys. All50wrong-name/property negative controls were detected. All25mapped keys are unique, so25private positive materials were prepared with25different-valid-pointer controls.

Actual Unity2021.3.45f2 results:
- 25/25shader names matched;
- 25/25ordered material-property schemas matched;
- 25/25wrong-pointer controls detected;
- Android Vulkan-only private material bundle built,414,127bytes;
- zero shader compiler errors.

The private materials, original names/IDs, expected bindings and bundle were not uploaded. Only aggregate evidence is retained. No game material, original shader source, .meta/GUID, color value or game project was modified by this experiment.

## Proven predecessor
[Nine-key run41737038201](https://github.com/alwansan/raf/actions/runs/41737038201), exact source be740083d8faeea55ed2ba030cceea0d239e5f60, job126268778276, artifact13278789548: SUCCESS,9/9names,9/9schemas,9/9negative controls,208,424-byte Vulkan bundle,0shadererrors. Its earlier pending status is superseded. The full corpus contains16additional engine keys; the expanded Unity test therefore exercises additional cases.

[Exact reader/database CPU run41736103335](https://github.com/alwansan/raf/actions/runs/41736103335) established that SourceGenerated1.3.2.0 selects Shader_2021_3_35 for Unity2021.3.45f2 and copies parsed names during both release/editor reads. The actual embedded engine database selects2021.2.0b14 and has6default+190extra shader records. Raw empty m_Name fields and incomplete canonical-owner typetrees are not evidence of missing exporter shader names. Full-run reader fingerprints are recorded in the companion JSON.

## Relation to the old build blocker
Pinned EngineAssetsExporter+PredefinedAssetCache+SingleRedirectExportCollection source redirects matching keys to internal engine pointers and marks those collections non-exportable. The165original objects split into25engine matches+140non-engine keys. That matches the140loose Shaderfiles observed in the prior native export before restorers added further files (142at the failing built-in stage). This is strong source/count evidence for a false assumption in the requirement that at least one loose vendor shader must be present. It is not direct verification of every association in that old full export.

No production gate was weakened. Native41687765928 still failed before Unity and produced no XAPK. The next source fix must bind original shader identities and actual complete-export Material→Shader references, including internal-engine PPtrs, before changing the zero-loose-file rule. A graph closure check alone cannot establish that each original material kept its shader association.

## Limits and next action
These results establish engine pointer/name/property-schema resolution and AndroidVulkan compilation for every mapped key in the authenticated original shader corpus. They do not establish original DXBC program or rendered-image equivalence, original material color/property values, all runtime keyword variants, actual complete-export associations, phone behavior, or water/FFT correctness. The140non-engine keys still require their own source/program restoration and validation; this count does not claim they are all currently broken.

Next: inspect/reproduce the complete export's original Material associations and engine PPtrs, then implement a justified fail-closed correction to the built-in restoration gate. Do not repeat these unchanged CPU or Unity mappings or retry the identical full native build. Preserve the independent water/FFT, custom rendering and full candidate readiness gates. NOT_READY; three complete immutable-source readiness reviews0/3. No Player/APK, Release, native request, schedule, CL or protected-branch changes by W1.
